"""Install the verified executable and published guide in the existing program folder."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
OUT=ROOT/"P2/out/repair-160"
INSTALL=HOST/"msvc.install_repair_current_x64"
SOURCE=HOST/"msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe"
TARGET=INSTALL/"bin/MuseScore3Evo.exe"
if (HOST/"personal/VERSION").read_text("utf8").strip()!="0.160.0":raise ValueError("Expected version 0.160.0")
processes=subprocess.check_output(["powershell","-NoProfile","-Command","Get-Process MuseScore3Evo -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path; exit 0"],text=True)
if str(TARGET).lower() in processes.lower():raise ValueError("The target program is currently running")
binary=SOURCE.read_bytes()
if not all(text in binary for text in (b"0.160.0",b"Kumo branch",b"Freddd13")):raise ValueError("Executable branding/version differs")
checked=json.loads((OUT/"program-checks.json").read_text("utf8"))
if hashlib.sha256(binary).hexdigest()!=checked["sha256"]:raise ValueError("Executable differs from the checked program")
config=INSTALL/"bin/kumo.ini";before=config.read_bytes()
backup=OUT/"previous-MuseScore3Evo.exe"
if not backup.exists():shutil.copy2(str(TARGET),str(backup))
shutil.copy2(str(SOURCE),str(TARGET))
if TARGET.read_bytes()!=binary:raise ValueError("Installed executable differs")
spec=importlib.util.spec_from_file_location("release160",ROOT/"P2/package_stable_release.py")
publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
guides=publisher.export_committed_guide(INSTALL)
if config.read_bytes()!=before:raise ValueError("Personal feature configuration changed")
report=dict(version="0.160.0",program=str(TARGET),sha256=hashlib.sha256(binary).hexdigest(),guide=guides,sourceCommit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HOST,text=True).strip())
(OUT/"installation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(report,ensure_ascii=False,indent=2))
