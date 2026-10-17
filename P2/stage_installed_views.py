"""Update only this batch's installed shared views."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
assert (I/'bin/MuseScore3Evo.exe').is_file()
for folder in ('HarmonyAssistant','PerformanceExpression','WorkflowCommon'):
 target=I/'plugins'/folder
 target.mkdir(parents=True,exist_ok=True)
 for p in (R.parent/folder).iterdir():
  if p.is_file() and p.suffix in ('.qml','.js','.md'):
   shutil.copyfile(p,target/p.name)
print('已更新现有安装中的本批界面')
