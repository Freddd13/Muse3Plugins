"""Read the current in-memory score in host-sized pages and retain task context.

The host owns score identities, mutation checks, playback and undo. This service
keeps JSON values and task progress; it never imports or rewrites the whole score.
"""

from __future__ import annotations

import asyncio
import copy
import json
import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from math import gcd
from typing import Any, Protocol
from uuid import uuid4

logger = logging.getLogger("MuseScoreMCP.Context")


class ScoreClient(Protocol):
    async def send_command(self, action: str, params: dict | None = None) -> dict: ...


class ContextError(ValueError):
    pass


def response(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ContextError("乐谱服务返回了无法读取的结果。")
    if value.get("status") == "error":
        raise ContextError(str(value.get("message", "乐谱操作失败。")))
    result = value.get("result", value)
    if not isinstance(result, dict):
        raise ContextError("乐谱服务返回了无法读取的结果。")
    if result.get("error"):
        raise ContextError(str(result["error"]))
    return result


def quarter_time(tick: int, division: int) -> dict:
    common = gcd(tick, division)
    return {"numerator": tick // common, "denominator": division // common}


@dataclass
class Job:
    id: str
    status: str = "running"
    progress: float = 0.0
    message: str = "正在读取乐谱…"
    result: dict | None = None
    task: asyncio.Task | None = field(default=None, repr=False)

    def state(self) -> dict:
        value = {"taskId": self.id, "status": self.status,
                 "progress": self.progress, "message": self.message}
        if self.result is not None:
            value["result"] = copy.deepcopy(self.result)
        return value


class ContextService:
    """Shared application service. MCP and other local callers use the same instance."""

    def __init__(self, client: ScoreClient):
        self.client = client
        self.contexts: OrderedDict[str, dict] = OrderedDict()
        self.jobs: OrderedDict[str, Job] = OrderedDict()
        self.context_bytes: dict[str, int] = {}

    async def command(self, action: str, params: dict | None = None) -> dict:
        return response(await self.client.send_command(action, params or {}))

    async def capture(self, request: dict | None = None, job: Job | None = None, *, retain: bool = True) -> dict:
        request = dict(request or {})
        state = await self.command("arrangementState", request)
        snapshot_id = state.get("snapshotId")
        if not snapshot_id:
            raise ContextError("请先打开乐谱，再读取要编配的范围。")
        scope = state["scope"]
        start, end = int(scope["start"]), int(scope["end"])
        division = int(state["ticksPerQuarter"])
        if division <= 0 or end <= start:
            raise ContextError("请选择一段包含音符或休止符的乐谱。")
        cursor = start
        tables = {name: [] for name in (
            "notes", "rests", "meters", "harmonies", "hands", "pedals", "parts", "tempos",
            "boundaryRelations", "occurrences",
        )}
        seen = {name: set() for name in ("meters", "parts", "tempos", "pedals")}
        pages = 0
        limit = 64
        maximum_batch_ms = 0.0
        if state.get("playing"):
            cached = next((context for context in reversed(self.contexts.values())
                if context["snapshotId"] == snapshot_id and context["scope"] == scope
                and set(request.get("fields", [])) <= set(context.get("fieldsRead", []))), None)
            if cached is None:
                raise ContextError("请暂停乐谱播放后读取完整声部。已经读取的任务可以继续查看。")
            tables = {name: copy.deepcopy(cached["scoreSnapshot"].get(name, [])) for name in tables}
            cursor = end
        while cursor < end:
            page = await self.command("arrangementRange", {
                "snapshotId": snapshot_id, "scope": scope,
                "fromTick": cursor, "limit": limit,
                "fields": request.get("fields", []),
            })
            if page.get("snapshotId") != snapshot_id:
                raise ContextError("读取期间乐谱发生了变化，请重新读取这一段。")
            elapsed = float(page.get("milliseconds", 0.0))
            maximum_batch_ms = max(maximum_batch_ms, elapsed)
            if elapsed > 2.0:
                limit = max(1, int(limit * 2.0 / elapsed))
            elif elapsed < 1.0:
                limit = min(64, limit + 8)
            for name, rows in tables.items():
                for row in page.get(name, []):
                    if name in seen:
                        key = repr(sorted(row.items()))
                        if key in seen[name]:
                            continue
                        seen[name].add(key)
                    rows.append(row)
            if len(tables["notes"]) + len(tables["rests"]) > 100000:
                raise ContextError("这段乐谱较长，请分段读取；也可以直接逐页查询全谱。")
            pages += 1
            if job:
                job.progress = min(0.99, (page.get("nextTick", end) - start) / (end - start))
                job.message = f"已读取 {len(tables['notes'])} 个音"
            if page.get("done"):
                break
            next_tick = int(page["nextTick"])
            if next_tick <= cursor:
                raise ContextError("这一页的读取位置未前进，请重新读取。")
            cursor = next_tick
            await asyncio.sleep(0)
        current = await self.command("arrangementState", {"scope": scope})
        if current.get("snapshotId") != snapshot_id:
            raise ContextError("乐谱已经更新，请重新读取后比较写法。")
        for note in tables["notes"]:
            note["ref"] = {"snapshotId": snapshot_id, "id": note["id"]}
            note.setdefault("quarterTime", quarter_time(int(note["tick"]), division))
            note.setdefault("quarterDuration", quarter_time(int(note["duration"]), division))
        result = {
            "schemaVersion": "arrangement-context/1",
            "contextId": str(uuid4()),
            **state,
            "scoreSnapshot": {"snapshotId": snapshot_id, "scope": scope, **tables},
            "taskBrief": copy.deepcopy(request.get("taskBrief", {})),
            "fieldsRead": list(request.get("fields", [])),
            "read": {"pages": pages, "notes": len(tables["notes"]), "status": "ready"},
            "timing": {"maximumGuiBatchMs": maximum_batch_ms},
        }
        size = len(json.dumps(result, ensure_ascii=False).encode("utf8"))
        if size > 8 * 1024 * 1024:
            raise ContextError("这份任务资料较多，请缩小选段；全谱可通过分页接口读取。")
        if not retain:
            return result
        context_id = result["contextId"]
        self.contexts[context_id] = copy.deepcopy(result)
        self.context_bytes[context_id] = size
        while len(self.contexts) > 4 or sum(self.context_bytes.values()) > 32 * 1024 * 1024:
            key, _ = self.contexts.popitem(last=False)
            self.context_bytes.pop(key, None)
        return result

    def start_capture(self, request: dict | None = None) -> dict:
        if sum(job.status == "running" for job in self.jobs.values()) >= 4:
            raise ContextError("已有四个任务正在进行，请先完成或取消其中一个。")
        job = Job(str(uuid4()))
        self.jobs[job.id] = job
        while len(self.jobs) > 32:
            oldest = next((key for key, value in self.jobs.items() if value.status != "running"), None)
            if oldest is None:
                break
            self.jobs.pop(oldest)

        async def run():
            try:
                result = await self.capture(request, job)
                job.result = {"contextId": result["contextId"], "snapshotId": result["snapshotId"], "read": result["read"]}
                job.status, job.progress, job.message = "ready", 1.0, "乐谱已读取"
            except asyncio.CancelledError:
                job.status, job.message = "cancelled", "已取消读取"
            except (ContextError, OSError, ValueError, KeyError) as error:
                job.status, job.message = "failed", str(error)
            except Exception as error:
                logger.exception("Score context task failed")
                job.status, job.message = "failed", f"读取未完成：{type(error).__name__}。请重试。"

        job.task = asyncio.create_task(run())
        return job.state()

    def task_state(self, task_id: str, cancel: bool = False) -> dict:
        if task_id not in self.jobs:
            raise ContextError("找不到这个任务，请重新开始读取。")
        job = self.jobs[task_id]
        if cancel and job.status == "running" and job.task:
            job.task.cancel()
            job.status, job.message = "cancelled", "已取消读取"
        return job.state()

    async def store_information(self, snapshot_id: str, information: dict) -> dict:
        return await self.write("storeArrangementInfo", {
            "snapshotId": snapshot_id, "information": information,
            "operationId": str(uuid4()),
        })

    async def submit_options(self, context_id: str, options: list[dict], brief: dict | None = None) -> dict:
        if not 1 <= len(options) <= 3:
            raise ContextError("每次提供一至三种写法，便于逐一比较。")
        context = self.context_result(context_id)
        allowed = context["scope"]
        for option in options:
            scope = option.get("scope", allowed)
            if not (allowed["start"] <= scope.get("start", -1) < scope.get("end", -1) <= allowed["end"]
                    and allowed["firstTrack"] <= scope.get("firstTrack", -1) < scope.get("endTrack", -1) <= allowed["endTrack"]):
                raise ContextError("建议超出了这次读取的范围，请先读取要修改的完整谱段。")
        return await self.write("submitArrangementOptions", {
            "snapshotId": context["snapshotId"], "options": [
                {"scope": allowed, **option} for option in options],
            "taskBrief": {**(brief if brief is not None else context.get("taskBrief", {})), "scope": allowed},
            "operationId": str(uuid4()),
        })

    async def option_action(self, option_id: str, action: str, operation_id: str | None = None) -> dict:
        if action not in {"preview", "performance", "original", "audition", "apply", "variant", "stop"}:
            raise ContextError("请选择试听、采用、存为另一种写法或停止。")
        return await self.write("arrangementOption", {
            "optionId": option_id, "action": action,
            "operationId": operation_id or str(uuid4()),
        })

    async def write(self, action: str, params: dict) -> dict:
        raw = await self.client.send_command(action, params)
        if raw.get("outcomeUnknown"):
            return {**raw, "operationId": params["operationId"],
                    "message": "请查询这次操作的结果，随后继续。"}
        return response(raw)

    async def operation_status(self, operation_id: str) -> dict:
        return await self.command("arrangementOperationStatus", {"operationId": operation_id})

    def context_result(self, context_id: str) -> dict:
        if context_id not in self.contexts:
            matches = [key for key, value in self.contexts.items() if value["snapshotId"] == context_id]
            if len(matches) == 1:
                context_id = matches[0]
            elif len(matches) > 1:
                raise ContextError("这份乐谱有几个不同任务，请使用读取结果中的contextId选择对应任务。")
        if context_id not in self.contexts:
            raise ContextError("这份读取结果已释放，请重新读取这一段。")
        return copy.deepcopy(self.contexts[context_id])
