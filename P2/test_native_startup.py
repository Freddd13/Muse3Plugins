"""Start the real program with isolated settings and test its automatic MCP service."""
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / "muse3_dev/MuseScore"
REPO = ROOT.parent.parent / "mcp-musescore"
INSTALLED = "--installed" in sys.argv
AUTOMATIC = "--no-auto" not in sys.argv
RUNTIME = HOST / "msvc.install_repair_current_x64" if INSTALLED else ROOT.parent / "P1/out/final-regression/runtime"
VERSION = (HOST / 'personal/VERSION').read_text('utf8').strip()
OUT = ROOT / ('out/native-startup-' + VERSION.replace('.', '')) / uuid4().hex[:8]
sys.path.insert(0, str(REPO))
from fastmcp import Client


async def read_score():
    if not AUTOMATIC:
        await asyncio.sleep(6)
        assert process.poll() is None, 'Program closed during startup check'
        assert not list((OUT / 'state').glob('instance-*.json')), 'AI started despite the saved choice'
        report = {'automaticStartup': False, 'staysStopped': True, 'version': VERSION,
                  'realProgram': True, 'settingsIsolated': True, 'installedPackage': INSTALLED}
        (OUT/'report.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        print(json.dumps(report)); return
    for _ in range(300):
        found = list((OUT / "state").glob("instance-*.json"))
        if found:
            try:
                instance = json.loads(found[0].read_text("utf8"))
            except (FileNotFoundError, PermissionError, json.JSONDecodeError):
                # QSaveFile replaces the discovery record while the program loads.
                instance = None
            if instance and instance["score"] not in ("尚未打开乐谱", ""):
                break
        if process.poll() is not None:
            raise RuntimeError("Native program stopped: " + str(process.returncode))
        await asyncio.sleep(.1)
    else:
        raise RuntimeError("Automatic connection did not become ready")
    assert instance["pid"] == process.pid
    assert instance["version"] == VERSION, instance
    environment = dict(os.environ, PATH=os.environ.get("SystemRoot", "C:/Windows") + "/System32",
                       MCP_MUSESCORE_STATE_DIR=str(OUT / "state"), FASTMCP_CHECK_FOR_UPDATES="off")
    mcp = RUNTIME / 'bin/tools/mcp'
    pointer = mcp / 'current.json'
    executable = mcp/'MuseScoreMCP.exe'
    if pointer.exists():executable = mcp/json.loads(pointer.read_text('utf8'))['directory']/'MuseScoreMCP.exe'
    async with Client({"mcpServers": {"musescore": {
            "command": str(executable),
            "args": ["--stdio", "--application", str(RUNTIME / "bin/MuseScore3Evo.exe")], "env": environment}}}) as client:
        result = await client.call_tool("read_arrangement_context", {"request": {"whole": True}})
        assert not result.is_error, result
        notes = result.data["scoreSnapshot"]["notes"]
        assert len(notes) == 6, result.data
    report = {"automaticStartup": True, "version": instance["version"], "notesRead": len(notes),
              "realProgram": True, "settingsIsolated": True, "installedPackage": INSTALLED}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps(report))


def main():
    global process
    OUT.mkdir(parents=True)
    # MuseScore accepts --config-folder only when the directory already exists.
    (OUT / "settings").mkdir()
    settings = OUT / "settings/MuseScore"
    settings.mkdir()
    (settings / "MuseScore3Evo.ini").write_text(
        "[application]\nstartup\\firstStart=false\n"
        "[ui]\napplication\\startup\\showTours=false\n" +
        ("[workflow]\naiAutostart=false\n" if not AUTOMATIC else ""), encoding="utf8")
    if not INSTALLED:
        shutil.copy2(HOST / "msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe", RUNTIME / "bin/MuseScore3Evo.exe")
        shutil.copytree(HOST / "share/workflow", RUNTIME / "workflow", dirs_exist_ok=True)
        shutil.copy2(HOST / "personal/kumo.ini", RUNTIME / "bin/kumo.ini")
    environment = dict(os.environ, MCP_MUSESCORE_STATE_DIR=str(OUT / "state"), KUMO_MCP_AUTOSTART="1",
                       QT_QUICK_BACKEND="software", QML_DISABLE_DISK_CACHE="1", QT_QPA_PLATFORM="offscreen")
    (OUT / "state").mkdir()
    info = subprocess.STARTUPINFO() if sys.platform == "win32" else None
    if info:
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = 0
    with (OUT / "program.log").open("w", encoding="utf8") as log:
        process = subprocess.Popen([str(RUNTIME / "bin/MuseScore3Evo.exe"), "-c", str(OUT / "settings"),
            str(HOST / "mtest/mscore/scoreobserver/piano.mscx")], env=environment, cwd=OUT,
            startupinfo=info, stdout=log, stderr=subprocess.STDOUT)
        try:
            asyncio.run(read_score())
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    main()
