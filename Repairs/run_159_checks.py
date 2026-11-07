"""Run the newly built checks in the existing isolated E-drive runtime."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent / "muse3_dev/MuseScore"
suite = sys.argv[1]
if suite not in ("pluginhost", "performanceeditor", "mxml_io"):
    raise ValueError(suite)
directory = "musicxml/io" if suite == "mxml_io" else "mscore/" + suite
binary = HOST / "msvc.build_harmony_release_x64/mtest" / directory / "Release" / ("tst_" + suite + ".exe")
runtime = ROOT / "P1/out/final-regression/runtime"
if not (runtime / "bin/Qt5Core.dll").is_file():
    raise RuntimeError("The existing isolated Qt runtime is missing")
target = runtime / "bin" / binary.name
shutil.copy2(str(binary), str(target))
output = ROOT / "P2/out/repair-159"
output.mkdir(parents=True, exist_ok=True)
log = output / (suite + ".txt")
environment = dict(os.environ, QT_QPA_PLATFORM=os.environ.get("REPAIR_159_QPA", "offscreen"),
                   QT_QUICK_BACKEND="software", QML_DISABLE_DISK_CACHE="1", KUMO_MCP_AUTOSTART="0",
                   HARMONY_TEST_ARTIFACTS=str(output), PERFORMANCE_NO_SYSTEM_CLIPBOARD="1",
                   P0_TEST_SOUNDFONT=str(HOST / "msvc.install_repair_current_x64/sound/MuseScore_General.sf3"),
                   KUMO_KAWAI_SF2="E:/music_fonts/[GD] Kawai ES100 Concert Grand 1 [V3].sf2")
arguments = sys.argv[2:] or ["velocityPeekHold159", "keyboardPointer159", "graceSpacing159", "nativeReverbSend159", "kawaiReverbSend159"]
result = subprocess.run([str(target), *arguments, "-o", str(log) + ",txt"], env=environment,
                        cwd=str(runtime / "bin"), timeout=240)
for line in log.read_text("utf8", errors="replace").splitlines():
    if line.startswith(("PASS", "FAIL", "QFATAL", "QINFO", "Totals:", "********")):
        print(line)
print(json.dumps({"suite": suite, "arguments": arguments, "exit": result.returncode,
                  "binary": str(binary), "log": str(log)}, ensure_ascii=False))
raise SystemExit(result.returncode)
