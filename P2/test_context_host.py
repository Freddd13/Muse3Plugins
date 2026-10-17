"""Exercise the real QML transport and MCP facade in an isolated MuseScore."""
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / "muse3_dev/MuseScore"
MCP = ROOT.parent.parent / "mcp-musescore"
OUT = ROOT / "out/context-060"
OUT.mkdir(parents=True, exist_ok=True)
RUNTIME = ROOT.parent / "P1/out/final-regression/runtime"
# Existing dependency runtime; update only the tested executable.
EXE = RUNTIME / "bin/tst_pluginhost.exe"
shutil.copy2(HOST / "msvc.build_harmony_release_x64/mtest/mscore/pluginhost/Release/tst_pluginhost.exe", EXE)
import hashlib
qt = HOST / "dependencies/qt5.15.2/msvc2019_64/bin"
assert hashlib.sha256((qt/"Qt5Core.dll").read_bytes()).digest() == hashlib.sha256((RUNTIME/"bin/Qt5Core.dll").read_bytes()).digest()
shutil.copy2(qt/"Qt5WebSockets.dll", RUNTIME/"bin/Qt5WebSockets.dll")
bridge = OUT / "bridge.qml"
bridge.write_text((MCP / "musescore-mcp-websocket.qml").read_text("utf8").replace("port: 8765", "port: 48765"), encoding="utf8")
sys.path.insert(0, str(MCP))
import server
from fastmcp import Client

server.client.uri = "ws://127.0.0.1:48765"
server.client.timeout = 8


async def exercise():
    for _ in range(40):
        if process.poll() is not None:
            raise RuntimeError(f"测试宿主提前结束：{process.returncode}")
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", 48765), .5)
            writer.close()
            await writer.wait_closed()
            if await server.client.connect():
                break
        except (OSError, asyncio.TimeoutError):
            pass
        await asyncio.sleep(.15)
    else:
        raise RuntimeError("测试宿主未启动本地连接")
    async with Client(server.mcp) as mcp:
        async def tool(name, **kwargs):
            result = await mcp.call_tool(name, kwargs)
            if result.is_error:
                raise RuntimeError(str(result.content))
            return result.data

        if os.environ.get("P2_CONTEXT_MINIMAL") == "ping":
            await tool("ping_musescore")
            await server.client.close()
            return {"status": "passed", "pingOnly": True}
        capabilities = await tool("get_capabilities")
        assert capabilities["arrangementContext"] == "arrangement-context/1", capabilities
        if os.environ.get("P2_CONTEXT_MINIMAL"):
            await server.client.close()
            return {"status": "passed", "readOnlyConnection": True}
        context = await tool("read_arrangement_context", request={"whole": True})
        notes = context["scoreSnapshot"]["notes"]
        assert len(notes) == 6
        bass = next(n for n in notes if n["writtenPitch"] == 36)
        option = {"title": "左手轻一些", "summary": "低音力度改为57，右手保持原样。",
                  "changes": [{"ref": bass["ref"], "velocity": 57}]}
        submitted = await tool("submit_arrangement_options", context_id=context["contextId"], options=[option])
        choice = submitted["options"][0]
        await tool("arrangement_option", option_id=choice["id"], action="preview")
        applied = await tool("arrangement_option", option_id=choice["id"], action="apply", operation_id="test-context-apply")
        assert applied["ok"], applied
        status = await tool("arrangement_operation_result", operation_id="test-context-apply")
        assert status == applied, status
        updated = await tool("read_arrangement_context", request={"whole": True})
        now = next(n for n in updated["scoreSnapshot"]["notes"] if n["writtenPitch"] == 36)
        assert now["velocity"] == 57 and now["velocityType"] != bass["velocityType"], now
        structured = await tool("get_score_data", first_measure=1, last_measure=1)
        assert structured["snapshotId"] == updated["snapshotId"]
        assert structured["measures"][0]["elements"]["staff1"][0]["notes"][0]["pitchMidi"] == 36
        await tool("arrangement_option", option_id=choice["id"], action="stop")
        await server.client.send_command("undo")
        restored = await tool("read_arrangement_context", request={"whole": True})
        original = next(n for n in restored["scoreSnapshot"]["notes"] if n["writtenPitch"] == 36)
        assert original["velocityRaw"] == bass["velocityRaw"]
        assert original["velocityType"] == bass["velocityType"]
        RESTART.write_text("reload", encoding="utf8")
        for _ in range(100):
            if Path(str(RESTART)+".ready").exists():
                break
            await asyncio.sleep(.05)
        else:
            raise RuntimeError("本地桥未完成重载")
        reply = await server.client.send_command("getCapabilities")
        assert reply["result"]["arrangementContext"] == "arrangement-context/1"

        return {"status": "passed", "notes": len(notes), "readPages": context["read"]["pages"],
                "tools": ["read_arrangement_context", "submit_arrangement_options", "arrangement_option",
                          "arrangement_operation_result", "get_score_data"],
                "adoptionUndoRestoredVelocity": True, "liveBridgeReload": True}


# Give each run its own result file; previous successful reports stay available.
from uuid import uuid4
DONE = OUT / ("client-" + str(uuid4()) + ".json")
RESTART = OUT / ("reload-" + str(uuid4()) + ".request")
env = dict(os.environ, QT_QUICK_BACKEND="software", QML_DISABLE_DISK_CACHE="1",
           P2_CONTEXT_BRIDGE=str(bridge), P2_CONTEXT_DONE=str(DONE), P2_CONTEXT_RELOAD=str(RESTART))
env.pop("QT_QPA_PLATFORM", None)
command = [str(EXE), "arrangementMcpTransport", "-o", str(OUT / "native.txt") + ",txt"]
with (OUT / "host.log").open("wb") as log:
    process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        result = asyncio.run(exercise())
        DONE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
        process.wait(timeout=8)
        assert process.returncode == 0, str(process.returncode) + "\n" + (OUT / "native.txt").read_text("utf8", errors="replace")
        (OUT / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
        print(json.dumps(result, ensure_ascii=False))
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
