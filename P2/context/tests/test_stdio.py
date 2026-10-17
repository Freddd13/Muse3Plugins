"""Exercise the subprocess stdio transport used by Codex, not just in-memory MCP."""

import asyncio
from pathlib import Path
import sys

from fastmcp import Client
from mock_musescore import running_mock, demo_score


def test_stdio_initialization_and_real_websocket_roundtrip():
    async def scenario():
        repo = Path(__file__).resolve().parents[1]
        async with running_mock(demo_score()) as mock:
            port = mock.uri.rsplit(":", 1)[1]
            config = {"mcpServers": {"musescore": {
                "command": sys.executable, "args": [str(repo / "server.py")],
                "env": {"MCP_MUSESCORE_HOST": "127.0.0.1", "MCP_MUSESCORE_PORT": port},
            }}}
            async with Client(config) as client:
                names = [t.name for t in await client.list_tools()]
                assert len(names) == 40
                assert {"read_arrangement_context", "submit_arrangement_options", "arrangement_option", "arrangement_operation_result"}.issubset(names)
                ping = next(n for n in names if n.endswith("ping_musescore"))
                read = next(n for n in names if n.endswith("get_score_data"))
                assert "pong" in str(await client.call_tool(ping, {}))
                result = await client.call_tool(read, {"first_measure": 2, "last_measure": 2})
                assert result.data["measures"][0]["measure"] == 2
                assert mock.commands[-1]["action"] == "getScore"
    asyncio.run(scenario())
