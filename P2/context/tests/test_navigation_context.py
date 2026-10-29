"""Navigation reports the real selection; it never presents an empty score sketch."""
import asyncio
import copy
import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError
from src.context.service import ContextService
from src.tools.navigation import setup_navigation_tools


class Navigation:
    def __init__(self):
        self.calls=[]; self.error=None
        self.scope={"start":1920,"end":5760,"firstTrack":0,"endTrack":8,"firstMeasure":2,"lastMeasure":3}

    async def send_command(self, action, params=None):
        self.calls.append((action,copy.deepcopy(params)))
        if action=="arrangementState":
            if self.error:return {"status":"error","message":self.error}
            return {"scope":self.scope,"snapshotId":"score:2","identity":{"displayTitle":"实际谱面标题"}}
        return {"success":True,"currentSelection":{"startTick":1920,"startStaff":0,"endStaff":1,"elements":[]}}


def test_native_navigation_returns_authoritative_scope_and_identity():
    async def run():
        native=Navigation(); mcp=FastMCP("navigation")
        setup_navigation_tools(mcp,native,ContextService(native))
        async with Client(mcp) as client:
            for tool,args in [("select_custom_range",dict(start_tick=1920,end_tick=5760,start_staff=0,end_staff=1)),("go_to_measure",{"measure":2}),("get_cursor_info",{})]:
                result=(await client.call_tool(tool,args)).data
                assert result["scope"]==native.scope
                assert result["identity"]["displayTitle"]=="实际谱面标题"
                assert result["snapshotId"]=="score:2"
            assert all(action!="arrangementRange" for action,_ in native.calls)
    asyncio.run(run())


def test_navigation_propagates_actual_read_error():
    async def run():
        native=Navigation();native.error="连接已断开，请重新连接。";mcp=FastMCP("navigation")
        setup_navigation_tools(mcp,native,ContextService(native))
        async with Client(mcp) as client:
            with pytest.raises(ToolError,match="连接已断开"):
                await client.call_tool("go_to_measure",{"measure":2})
    asyncio.run(run())


def test_old_bridge_keeps_its_note_text_response():
    async def run():
        native=Navigation();native.error="Unknown command: arrangementState";mcp=FastMCP("navigation")
        setup_navigation_tools(mcp,native,ContextService(native))
        async with Client(mcp) as client:
            result=await client.call_tool("go_to_measure",{"measure":2})
            text="".join(part.text for part in result.content if part.type=="text")
            assert "[位置]" in text and "LilyPond" in text
    asyncio.run(run())
