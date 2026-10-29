"""Connection and utility tools for MuseScore MCP."""

from ..client import MuseScoreClient
from ..client.responses import unwrap_response
from fastmcp.exceptions import ToolError
from typing import Annotated, Optional


def setup_connection_tools(mcp, client: MuseScoreClient, context_service=None):
    """Setup connection and utility tools."""
    
    @mcp.tool(
        description="Connect to the MuseScore WebSocket API.",
        tags={"connection"},
    )
    async def connect_to_musescore():
        result = await client.connect()
        return {"success": result}

    @mcp.tool(
        description="Ping the MuseScore WebSocket API to check connection.",
        tags={"connection"},
    )
    async def ping_musescore():
        return await client.send_command("ping")

    @mcp.tool(
        description="读取当前乐谱的LilyPond音符文本。确认窗口、谱名和总谱／分谱用get_score_identity；编配读取用read_arrangement_context。",
        tags={"connection", "score"},
        annotations={"readOnlyHint": True},
    )
    async def get_score():
        res = unwrap_response(await client.send_command("getScore"))
        if res.get("success") and "analysis" in res:
            from ..utils.lilypond_converter import json_to_lilypond
            analysis = res["analysis"]
            lily_str = json_to_lilypond(analysis)
            
            identity = analysis.get("identity", {})
            meta = ["当前谱：" + (identity.get("displayTitle") or analysis.get("title") or "未命名乐谱")]
            if identity.get("partName"):
                meta.append("分谱：" + identity["partName"])
            if identity.get("filePath"):
                meta.append("文件：" + identity["filePath"])
            if "numMeasures" in analysis:
                meta.append(f"小节数：{analysis['numMeasures']}")
            meta.append(f"谱表数：{len(analysis.get('staves', []))}")
            return "\n".join(meta) + "\n[音符文本（LilyPond）]\n" + lily_str

        return res

    @mcp.tool(description="Read bridge version, MuseScore version, score availability and optional Evolution API support.",
              tags={"connection"}, annotations={"readOnlyHint": True})
    async def get_capabilities():
        return unwrap_response(await client.send_command("getCapabilities"))

    @mcp.tool(description="读取当前程序窗口、标签页、总谱／分谱、谱面标题、作品信息标题、文件位置和未保存状态。先用这份信息确认正在讨论哪份谱。读取保持选音与播放位置。",
              tags={"connection", "score"}, annotations={"readOnlyHint": True})
    async def get_score_identity():
        try:
            result = unwrap_response(await client.send_command("getScoreIdentity"))
        except ToolError as error:
            if "unknown command" in str(error).lower():
                raise ToolError("当前程序未提供乐谱身份，请更新MuseScore并重新连接。") from error
            raise
        if not isinstance(result, dict) or "hasScore" not in result:
            raise ToolError("当前程序未提供乐谱身份，请更新MuseScore并重新连接。")
        return result

    @mcp.tool(description="Read authoritative structured notes, voices, timing, ties, tuning and velocity properties. Measure bounds are inclusive; reading leaves selection unchanged.",
              tags={"score"}, annotations={"readOnlyHint": True})
    async def get_score_data(
        first_measure: Annotated[int, "First measure (1-based, inclusive)"] = 1,
        last_measure: Annotated[Optional[int], "Last measure (1-based, inclusive); omitted means end of score"] = None,
    ):
        if first_measure < 1 or (last_measure is not None and last_measure < first_measure):
            raise ToolError("Invalid measure range")
        if context_service:
            capability_response = await client.send_command("getCapabilities")
            message = str(capability_response.get("message") or capability_response.get("error") or "")
            capabilities = {} if message.endswith("Unknown command: getCapabilities") else unwrap_response(capability_response)
            if capabilities.get("arrangementContext"):
                from ..context.service import ContextError
                try:
                    request = {"whole": True, "firstMeasure": first_measure}
                    if last_measure is not None:
                        request["lastMeasure"] = last_measure
                    context = await context_service.capture(request, retain=False)
                    return score_data_projection(context)
                except ContextError as error:
                    raise ToolError(str(error)) from error
        result = unwrap_response(await client.send_command("getScore"))
        if not isinstance(result, dict) or not isinstance(result.get("analysis"), dict):
            raise ToolError("MuseScore returned no score data")
        analysis = result["analysis"]
        return {**analysis, "measures": [m for m in analysis.get("measures", [])
                if m["measure"] >= first_measure and (last_measure is None or m["measure"] <= last_measure)]}


def score_data_projection(context):
    """Keep the existing measure/staff response while using native paging."""
    snapshot = context["scoreSnapshot"]
    scope = snapshot["scope"]
    staff_count = (scope["endTrack"] + 3) // 4
    measures = {}
    for meter in snapshot["meters"]:
        measures.setdefault(meter["measure"], {"measure": meter["measure"],
            "startTick": meter["tick"], "endTick": meter["end"], "numElements": 0,
            "elements": {f"staff{i}": [] for i in range(staff_count)}})
    groups = {}
    for row in snapshot["notes"]:
        if row.get("contextOnly"):
            continue
        key = (row["tick"], row["track"], row.get("graceIndex", -1))
        if key not in groups:
            groups[key] = {"name": "Chord", "startTick": row["tick"], "voice": row["track"] % 4,
                "durationTicks": row["duration"], "quarterDuration": row["quarterDuration"],
                "isTuplet": bool(row.get("tuplet")), "isTie": False, "notes": []}
            measures[row["measure"]]["elements"][f"staff{row['track']//4}"].append(groups[key])
            measures[row["measure"]]["numElements"] += 1
        group = groups[key]
        group["isTie"] |= row.get("tieForward", False)
        group["notes"].append({**row, "pitchMidi": row.get("notatedPitch", row["writtenPitch"]), "tpc": row.get("notatedTpc", row["writtenTpc"]),
            "tieForward": row.get("tieForward", False), "veloType": row["velocityType"], "veloOffset": row["velocityRaw"]})
    ordered = sorted(measures.values(), key=lambda m: m["startTick"])
    for row in snapshot["rests"]:
        measure = next((m for m in ordered if m["startTick"] <= row["tick"] < m["endTick"]), None)
        if measure:
            measure["elements"][f"staff{row['track']//4}"].append({"name": "Rest", "startTick": row["tick"],
                "voice": row["track"] % 4, "durationTicks": row["duration"], "quarterDuration": row["quarterDuration"]})
            measure["numElements"] += 1
    metadata = {key: context[key] for key in ("identity", "scoreSessionId", "documentId") if key in context}
    return {**metadata, "ticksPerQuarter": context["ticksPerQuarter"], "title": context.get("title", ""),
        "numMeasures": scope["lastMeasure"], "staves": [next((dict(row) for row in snapshot.get("staves", []) if row["index"]==i), {"index": i,"name": f"staff{i}"}) for i in range(staff_count)],
        "measures": ordered, "snapshotId": context["snapshotId"], "coverage": context["coverage"]}
