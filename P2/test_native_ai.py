"""Use the packaged exe against the actual built-in bridge and native connection window."""
import asyncio
import json
import os
from pathlib import Path
import shutil
import filecmp
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / "muse3_dev/MuseScore"
REPO = ROOT.parent.parent / "mcp-musescore"
RUNTIME = ROOT.parent / "P1/out/final-regression/runtime"
OUT = ROOT / "out/native-ai-063"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))
from fastmcp import Client


async def exercise(process):
    ready = Path(str(READY_NAME) + ".ready")
    for _ in range(400):
        if ready.exists():
            break
        if process.poll() is not None:
            raise RuntimeError(str(process.returncode)+"\n"+(OUT / "native.txt").read_text("utf8", errors="replace"))
        await asyncio.sleep(.1)
    else:
        raise RuntimeError("native AI window did not become ready")
    exe = RUNTIME / "bin/tools/mcp/MuseScoreMCP.exe"
    app = RUNTIME / "bin/tst_pluginhost.exe"
    env = dict(os.environ, MCP_MUSESCORE_STATE_DIR=str(OUT / "state"), CODEX_HOME=str(OUT / "codex"),
               FASTMCP_CHECK_FOR_UPDATES="off", PYTHONPATH="",
               PATH=os.environ.get("SystemRoot", "C:/Windows") + "/System32")
    async with Client({"mcpServers": {"musescore": {"command": str(exe),
            "args": ["--stdio", "--application", str(app)], "env": env}}}) as client:
        async def tool(name, **kwargs):
            result = await client.call_tool(name, kwargs)
            if result.is_error:
                raise RuntimeError(str(result.content))
            return result.data
        await tool("ping_musescore")
        context = await tool("read_arrangement_context", request={"whole": True})
        snapshot = context["scoreSnapshot"]
        notes = snapshot["notes"]
        assert notes, context
        before = notes[0]
        options = await tool("submit_arrangement_options", context_id=context["contextId"],
            options=[{"title": "独立程序实际采用", "scope": snapshot["scope"],
                      "changes": [{"ref": before["ref"], "velocity": 103}]}])
        option = options["options"][0]["id"]
        await tool("arrangement_option", option_id=option, action="apply", operation_id="native-ai-063")
        status = await tool("arrangement_operation_result", operation_id="native-ai-063")
        assert status["ok"], status
        updated = await tool("read_arrangement_context", request={"whole": True})
        assert updated["scoreSnapshot"]["notes"][0]["velocity"] == 103
        await tool("undo")
        restored = await tool("read_arrangement_context", request={"whole": True})
        assert restored["scoreSnapshot"]["notes"][0]["velocityRaw"] == before["velocityRaw"]
        assert restored["scoreSnapshot"]["notes"][0]["velocityType"] == before["velocityType"]
        report = {"notesRead": len(notes), "packagedServer": True, "nativeBridge": True,
                  "nativeConfigureAndDiagnosis": True, "adoptAndUndo": True,
                  "pythonRemovedFromServerPath": True}
        (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
        print(json.dumps(report, ensure_ascii=False))


def stage(source, destination):
    if not Path(destination).exists() or not filecmp.cmp(source,destination,shallow=False):
        shutil.copy2(source,destination)
    return destination


def main():
    from uuid import uuid4
    done = OUT / ("done-" + uuid4().hex)
    # exercise uses the same chosen name.
    global READY_NAME
    READY_NAME = done
    shutil.copy2(HOST / "msvc.build_harmony_release_x64/mtest/mscore/pluginhost/Release/tst_pluginhost.exe", RUNTIME / "bin/tst_pluginhost.exe")
    shutil.copytree(ROOT / "out/mcp-dist/MuseScoreMCP", RUNTIME / "bin/tools/mcp", dirs_exist_ok=True,copy_function=stage)
    shutil.copytree(HOST / "share/workflow", RUNTIME / "workflow", dirs_exist_ok=True,copy_function=stage)
    shutil.copy2(HOST / "personal/kumo.ini", RUNTIME / "bin/kumo.ini")
    shutil.copytree(HOST / "personal/docs", RUNTIME / "personal/docs", dirs_exist_ok=True,copy_function=stage)
    env = dict(os.environ, P2_NATIVE_AI_DONE=str(done), MCP_MUSESCORE_STATE_DIR=str(OUT / "state"),
               CODEX_HOME=str(OUT / "codex"), KUMO_MCP_AUTOSTART="0", QT_QUICK_BACKEND="software",
               PATH="E:/Git/usr/bin;"+os.environ.get("PATH",""), HARMONY_TEST_ARTIFACTS=str(OUT), P0_TEST_SOUNDFONT=str(HOST / "msvc.install_repair_current_x64/sound/MuseScore_General.sf3"))
    (OUT / "state").mkdir(exist_ok=True)
    with (OUT / "host.log").open("w", encoding="utf8") as log:
        process = subprocess.Popen([str(RUNTIME / "bin/tst_pluginhost.exe"), "nativeAiConnectionAndTransport", "-o", str(OUT / "native.txt")+",txt"],
                                   env=env, cwd=OUT, stdout=log, stderr=subprocess.STDOUT)
        try:
            asyncio.run(exercise(process))
            done.write_text("done")
            assert process.wait(timeout=20) == 0
        finally:
            if process.poll() is None:
                process.terminate(); process.wait(timeout=10)


if __name__ == "__main__":
    main()
