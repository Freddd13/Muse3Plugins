"""Update the existing installation without creating another full runtime."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent / "muse3_dev/MuseScore"
SOURCE = HOST / "msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe"
INSTALL = HOST / "msvc.install_repair_current_x64"
TARGET = INSTALL / "bin/MuseScore3Evo.exe"
version = (HOST / "personal/VERSION").read_text("utf8").strip()
if version != "0.159.0":
    raise RuntimeError("This installer belongs to 0.159.0")
processes = subprocess.check_output(["powershell", "-NoProfile", "-Command",
    "Get-Process MuseScore3Evo -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path; exit 0"], text=True)
if str(TARGET).lower() in processes.lower():
    raise RuntimeError("MuseScore is still running from the destination")
binary = SOURCE.read_bytes()
if not all(value in binary for value in (b"0.159.0", b"Kumo branch", b"Freddd13")):
    raise RuntimeError("The executable identity does not match")
configuration = INSTALL / "bin/kumo.ini"
config_before = configuration.read_bytes()
backup = ROOT / "P2/out/repair-159/previous-MuseScore3Evo.exe"
if not backup.exists():
    shutil.copy2(str(TARGET), str(backup))
shutil.copy2(str(SOURCE), str(TARGET))
if SOURCE.read_bytes() != TARGET.read_bytes():
    raise RuntimeError("Installed program differs")
spec = importlib.util.spec_from_file_location("package159", ROOT / "P2/package_stable_release.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
guides = publisher.export_committed_guide(INSTALL)
if configuration.read_bytes() != config_before:
    raise RuntimeError("Feature configuration changed")
result = dict(version=version, program=str(TARGET), sha256=hashlib.sha256(binary).hexdigest(),
              guide=guides, sourceCommit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HOST, text=True).strip())
(ROOT / "P2/out/repair-159/installation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf8")
print(json.dumps(result, ensure_ascii=False, indent=2))
