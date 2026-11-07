from pathlib import Path
import hashlib
import json
import os
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
INSTALL=HOST/"msvc.install_repair_current_x64"
OUT=ROOT/"P2/out/repair-159"
source=HOST/"mtest/mscore/scoreobserver/piano.mscx"
environment=dict(os.environ,QT_QPA_PLATFORM="offscreen",KUMO_MCP_AUTOSTART="0")
environment["PATH"]=str(INSTALL/"bin")+os.pathsep+environment["PATH"]
environment["QT_PLUGIN_PATH"]=str(INSTALL/"bin")
outputs={}
for name,program in (("previous",OUT/"previous-MuseScore3Evo.exe"),("installed",INSTALL/"bin/MuseScore3Evo.exe")):
    for extension in ("mid","pdf"):
        output=OUT/(name+"-ordinary."+extension)
        result=subprocess.run([str(program),"-c",str(OUT/(name+"-settings")),"-o",str(output),str(source)],
                              cwd=INSTALL/"bin",env=environment,capture_output=True,timeout=60)
        (OUT/(name+"-"+extension+".txt")).write_bytes(result.stdout+result.stderr)
        if result.returncode or not output.is_file():raise RuntimeError(str(output)+" failed")
        outputs[name+"-"+extension]=dict(bytes=output.stat().st_size,sha256=hashlib.sha256(output.read_bytes()).hexdigest())
if outputs["previous-mid"]!=outputs["installed-mid"]:raise RuntimeError("Default MIDI output changed")
outputs["installedVersion"]=(INSTALL/"personal/VERSION").read_text("utf8").strip()
(OUT/"installed-checks.json").write_text(json.dumps(outputs,indent=2),encoding="utf8")
print(json.dumps(outputs,indent=2))
