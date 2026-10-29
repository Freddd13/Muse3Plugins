"""Codex-facing tools for the common score-context service."""
from fastmcp.exceptions import ToolError
from typing import Annotated
from ..context.service import ContextError, ContextService


def setup_arrangement_tools(mcp, service: ContextService):
    async def call(operation):
        try:
            return await operation
        except ContextError as error:
            raise ToolError(str(error)) from error

    @mcp.tool(description="Read the current in-memory score selection in bounded host pages. Includes exact quarter-unit timing, voices, spelling, ties, hands, velocity, repeat occurrences, available harmonic interpretation and supplied materials. request: scope {start,end,firstTrack,endTrack}, whole, firstMeasure/lastMeasure, purpose analysis/performance/engraving; fields ['geometry','performance'], taskBrief. Read first before submitting options.",
              tags={"arrangement", "score"}, annotations={"readOnlyHint": True})
    async def read_arrangement_context(request: Annotated[dict | None, "范围、可选字段和本次编配要求"] = None):
        return await call(service.capture(request))

    @mcp.tool(description="Start a cancellable score-context read. Poll arrangement_task until ready, then get_arrangement_context with its contextId.",
              tags={"arrangement", "score"}, annotations={"readOnlyHint": True})
    async def start_arrangement_read(request: Annotated[dict | None, "范围、可选字段和本次编配要求"] = None):
        try:
            return service.start_capture(request)
        except ContextError as error:
            raise ToolError(str(error)) from error

    @mcp.tool(description="Read progress or cancel an active context task.", tags={"arrangement"})
    async def arrangement_task(task_id: Annotated[str, "读取任务的taskId"], cancel: Annotated[bool, "结束这个读取任务"] = False):
        try:
            return service.task_state(task_id, cancel)
        except ContextError as error:
            raise ToolError(str(error)) from error

    @mcp.tool(description="Retrieve a completed immutable task context by contextId.", tags={"arrangement"}, annotations={"readOnlyHint": True})
    async def get_arrangement_context(context_id: Annotated[str, "读取结果中的contextId"]):
        try:
            return service.context_result(context_id)
        except ContextError as error:
            raise ToolError(str(error)) from error

    @mcp.tool(description="Refresh a retained task after score edits. Keeps its original score, range, purpose and requirements while reading current notes, material sources and requested performance. Ordinary browsing selection stays unchanged.",
              tags={"arrangement"}, annotations={"readOnlyHint": True})
    async def refresh_arrangement_context(context_id: Annotated[str, "要继续的contextId"], task_brief: Annotated[dict | None, "补充本次编配要求"] = None):
        return await call(service.refresh(context_id, task_brief))

    @mcp.tool(description="Read one native page directly. Use arrangementState via get_arrangement_state, then pass its snapshotId and scope, fromTick and limit (1-64). Useful for large scores.",
              tags={"arrangement"}, annotations={"readOnlyHint": True})
    async def get_arrangement_page(request: Annotated[dict, "原生页的snapshotId、scope和fromTick"]):
        return await call(service.command("arrangementRange", request))

    @mcp.tool(description="Read score version, exact scope, available fields and saved musical information without changing selection.",
              tags={"arrangement"}, annotations={"readOnlyHint": True})
    async def get_arrangement_state(request: Annotated[dict | None, "范围、可选字段和本次编配要求"] = None):
        return await call(service.command("arrangementState", request))

    @mcp.tool(description="Save user-supplied assertions, materials and alignments in the score. Preserve existing entries when extending. Each assertion/material records origin, target coverage and status. One native undo. Explicit user intent to save information is required.",
              tags={"arrangement"})
    async def save_arrangement_information(snapshot_id: Annotated[str, "已读取的snapshotId"], information: Annotated[dict, "保留来源和作用范围的资料集合"]):
        return await call(service.store_information(snapshot_id, information))

    @mcp.tool(description="Submit 1-3 local score options for in-score comparison. Each: title, summary, scope, changes [{ref:{snapshotId,id},pitch,tpc1,tpc2,velocity,finger,hand,handEnd}], voices [{track,events:[{quarterDuration:{numerator,denominator},pitches:[{pitch,tpc1,tpc2}]}]}]. Voices cover the complete scope including rests (empty pitches). Defaults preserve track 0 melody and harmonic pitch classes. task_brief preserveTracks/preserveNotes, allowMelodyChanges and preserveHarmony record the user's instructions. Host prepares copies before offering them in View > 编配建议. Source score stays available for comparison.",
              tags={"arrangement"})
    async def submit_arrangement_options(context_id: Annotated[str, "读取结果中的contextId"], options: Annotated[list[dict], "一至三种完整的局部写法"], task_brief: Annotated[dict | None, "本次允许修改的范围和保留条件"] = None):
        return await call(service.submit_options(context_id, options, task_brief))

    @mcp.tool(description="Operate a submitted option: preview (score difference overlay), performance (original and proposed rendered MIDI attacks), original/audition (same-range playback), apply (one undo), variant (save as regional writing), stop. Apply within the user's requested scope; stale options require a fresh read. operation_id may be reused to query/recover one logical operation.",
              tags={"arrangement"})
    async def arrangement_option(option_id: Annotated[str, "原生面板返回的写法id"], action: Annotated[str, "preview、performance、original、audition、apply、variant或stop"], operation_id: Annotated[str | None, "这一次操作的唯一id"] = None):
        return await call(service.option_action(option_id, action, operation_id))

    @mcp.tool(description="Query a native operation result by operationId after a lost connection. A known operation is returned without executing it again.",
              tags={"arrangement"}, annotations={"readOnlyHint": True})
    async def arrangement_operation_result(operation_id: Annotated[str, "要查询的operationId"]):
        return await call(service.operation_status(operation_id))
