"""Update the existing program and its committed instructions."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
O = R / 'P2/out/repair-166'
I = H / 'msvc.install_repair_current_x64'
source = H / 'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
target = I / 'bin/MuseScore3Evo.exe'
sys.stdout.reconfigure(encoding='utf8', errors='replace')
checked = json.loads((O/'program-checks.json').read_text('utf8'))
assert hashlib.sha256(source.read_bytes()).hexdigest() == checked['sha256']
processes = subprocess.check_output(['powershell','-NoProfile','-Command',
    'Get-Process MuseScore3Evo -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path; exit 0'], text=True)
if str(target).lower() in processes.lower():
    print('MuseScore is still using the installed program. Installation remains ready.')
    raise SystemExit(2)
config = I / 'bin/kumo.ini'
before = config.read_bytes()
backup = O / 'previous-MuseScore3Evo.exe'
if not backup.exists():
    shutil.copy2(target, backup)
shutil.copy2(source, target)
assert hashlib.sha256(target.read_bytes()).hexdigest() == checked['sha256']
spec = importlib.util.spec_from_file_location('release166', R/'P2/package_stable_release.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
guides = publisher.export_committed_guide(I)
assert config.read_bytes() == before
report = dict(version=checked['version'], program=str(target), sha256=checked['sha256'],
              guide=guides, sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=H,text=True).strip())
(O/'installation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(report, ensure_ascii=False, indent=2))
