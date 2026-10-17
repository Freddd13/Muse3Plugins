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
        description="Get information about the current score.",
        tags={"connection", "score"},
        annotations={"readOnlyHint": True},
    )
    async def get_score():
        res = unwrap_response(await client.send_command("getScore"))
        if res.get("success") and "analysis" in res:
            from ..utils.lilypond_converter import json_to_lilypond
            analysis = res["analysis"]
            lily_str = json_to_lilypond(analysis)
            
            meta = []
            if "numMeasures" in analysis:
                meta.append(f"Total Mesures: {analysis['numMeasures']}")
                
            num_staves = len(analysis.get("staves", []))
            if num_staves > 0:
                meta.append(f"Nombre de portées: {num_staves}")
                
            meta_str = ", ".join(meta) if meta else "Aucune métadonnée"
            
            return f"[Métadonnées] {meta_str}\n[Partition]\n{lily_str}"
        return res

    @mcp.tool(description="Read bridge version, MuseScore version, score availability and optional Evolution API support.",
              tags={"connection"}, annotations={"readOnlyHint": True})
    async def get_capabilities():
        return unwrap_response(await client.send_command("getCapabilities"))

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
        key = (row["tick"], row["track"], row.get("graceIndex", -1))
        if key not in groups:
            groups[key] = {"name": "Chord", "startTick": row["tick"], "voice": row["track"] % 4,
                "durationTicks": row["duration"], "quarterDuration": row["quarterDuration"],
                "isTuplet": bool(row.get("tuplet")), "isTie": False, "notes": []}
            measures[row["measure"]]["elements"][f"staff{row['track']//4}"].append(groups[key])
            measures[row["measure"]]["numElements"] += 1
        group = groups[key]
        group["isTie"] |= row.get("tieForward", False)
        group["notes"].append({**row, "pitchMidi": row["writtenPitch"], "tpc": row["writtenTpc"],
            "tieForward": row.get("tieForward", False), "veloType": row["velocityType"], "veloOffset": row["velocityRaw"]})
    ordered = sorted(measures.values(), key=lambda m: m["startTick"])
    for row in snapshot["rests"]:
        measure = next((m for m in ordered if m["startTick"] <= row["tick"] < m["endTick"]), None)
        if measure:
            measure["elements"][f"staff{row['track']//4}"].append({"name": "Rest", "startTick": row["tick"],
                "voice": row["track"] % 4, "durationTicks": row["duration"], "quarterDuration": row["quarterDuration"]})
            measure["numElements"] += 1
    return {"ticksPerQuarter": context["ticksPerQuarter"], "title": context.get("title", ""),
        "numMeasures": scope["lastMeasure"], "staves": [{"name": f"staff{i}"} for i in range(staff_count)],
        "measures": ordered, "snapshotId": context["snapshotId"], "coverage": context["coverage"]}
