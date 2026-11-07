"""Compare ordinary exports and reopen the official 3.6.2 round trip."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
OUT=ROOT/"P2/out/repair-160"
INSTALL=HOST/"msvc.install_repair_current_x64/bin"
latest=OUT/"checked-MuseScore3Evo.exe"
shutil.copy2(str(HOST/"msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe"),str(latest))
binary=latest.read_bytes()
assert all(name in binary for name in (b"0.160.0",b"Kumo branch",b"Freddd13"))
env=dict(os.environ,QT_QPA_PLATFORM="offscreen",KUMO_MCP_AUTOSTART="0",PATH=str(INSTALL)+os.pathsep+os.environ["PATH"],QT_PLUGIN_PATH=str(INSTALL),TEMP=str(ROOT/"P2/out/check-temp"),TMP=str(ROOT/"P2/out/check-temp"))
source=HOST/"mtest/mscore/scoreobserver/piano.mscx"
report={}
for label,program in (("previous",INSTALL/"MuseScore3Evo.exe"),("new",latest)):
    for suffix in ("mid","pdf"):
        target=OUT/(label+"-ordinary."+suffix)
        result=subprocess.run([str(program),"-c",str(OUT/(label+"-cli-settings")),"-o",str(target),str(source)],env=env,cwd=INSTALL,capture_output=True,timeout=60)
        (OUT/(label+"-cli-"+suffix+".txt")).write_bytes(result.stdout+result.stderr)
        if result.returncode or not target.is_file():raise ValueError(str(target)+" export failed")
        report[label+"-"+suffix]={"bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
assert report["new-mid"]==report["previous-mid"],"Ordinary MIDI export changed"
stock=ROOT/"P2/out/compat-3.6.2/roundtrip-midi160.mscz"
for suffix in ("mid","pdf"):
    target=OUT/("official-roundtrip."+suffix)
    result=subprocess.run([str(latest),"-c",str(OUT/"roundtrip-settings"),"-o",str(target),str(stock)],env=env,cwd=INSTALL,capture_output=True,timeout=60)
    if result.returncode or not target.is_file():raise ValueError("Official round trip could not reopen")
    report["roundtrip-"+suffix]={"bytes":target.stat().st_size}
report["version"]="0.160.0"
report["sha256"]=hashlib.sha256(binary).hexdigest()
(OUT/"program-checks.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(report,indent=2))
