"""Update the existing E-drive installation, retaining the preceding program."""
from pathlib import Path
import hashlib, shutil
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
source=H/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
target=I/'bin/MuseScore3Evo.exe'
assert source.is_file() and target.is_file()
backup=R/'out/before-p2/MuseScore3Evo.exe'
if not backup.exists():
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
media=H/'msvc.build_harmony_release_x64/mscore/referenceaudio/Release/kumo_referenceaudio.dll'
if media.is_file() and (H/'mscore/referenceaudio/spectrum.cpp').exists():
 previous=R/'out/before-spectrum';previous.mkdir(parents=True,exist_ok=True)
 for current in (target,I/'bin/kumo_referenceaudio.dll'):
  if current.exists() and not (previous/current.name).exists():shutil.copy2(current,previous/current.name)
 shutil.copy2(media,I/'bin/kumo_referenceaudio.dll')
shutil.copy2(source,target)
for folder in ('HarmonyAssistant','PerformanceExpression','WorkflowCommon'):
 destination=I/'plugins'/folder;destination.mkdir(parents=True,exist_ok=True)
 for p in (R.parent/folder).iterdir():
  if p.is_file() and p.suffix in ('.qml','.js','.md'):shutil.copyfile(p,destination/p.name)
for p in (R/'native/personal').rglob('*'):
 if not p.is_file():continue
 destination=I/'personal'/p.relative_to(R/'native/personal');destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,destination)
print('已更新现有程序：',target)
print('SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
