"""Update the existing E-drive installation, retaining the preceding program."""
from pathlib import Path
import filecmp, hashlib, shutil, subprocess

def copy_changed(source, destination):
 if Path(destination).is_file() and filecmp.cmp(source, destination, shallow=False):return destination
 return shutil.copy2(source, destination)
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
source=H/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
target=I/'bin/MuseScore3Evo.exe'
assert source.is_file() and target.is_file()
# Check the running executable before updating any files in the installation.
try:
 with target.open('r+b'):pass
except PermissionError:
 raise SystemExit('请先关闭当前 MuseScore 窗口，再更新程序。安装目录尚未更改：'+str(target))
backup=R/('out/before-'+(H/'personal/VERSION').read_text('utf8').strip()+'/MuseScore3Evo.exe')
if not backup.exists():
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
media=H/'msvc.build_harmony_release_x64/mscore/referenceaudio/Release/kumo_referenceaudio.dll'
if media.is_file() and (H/'mscore/referenceaudio/spectrum.cpp').exists():
 previous=R/'out/before-spectrum';previous.mkdir(parents=True,exist_ok=True)
 for current in (target,I/'bin/kumo_referenceaudio.dll'):
  if current.exists() and not (previous/current.name).exists():shutil.copy2(current,previous/current.name)
 shutil.copy2(media,I/'bin/kumo_referenceaudio.dll')
# Dynamic QML imports need their matching runtime dependency.
qt=H/'dependencies/qt5.15.2/msvc2019_64/bin'
if (qt/'Qt5WebSockets.dll').exists():
 assert hashlib.sha256((qt/'Qt5Core.dll').read_bytes()).digest()==hashlib.sha256((I/'bin/Qt5Core.dll').read_bytes()).digest()
 shutil.copy2(qt/'Qt5WebSockets.dll',I/'bin/Qt5WebSockets.dll')
helper=H/'msvc.build_harmony_release_x64/audio/vst/Release/MuseScoreVstHost.exe'
assert helper.is_file(),'请先编译 VST 辅助程序'
copy_changed(helper,I/'bin/MuseScoreVstHost.exe')
for name,license_name in [('kumo-vst3','LICENSE.txt'),('kumo-vestige','COPYING')]:
 folder=I/'licenses'/name;folder.mkdir(parents=True,exist_ok=True)
 for leaf in (license_name,'source.json'):copy_changed(H/'thirdparty'/name/leaf,folder/leaf)
shutil.copy2(source,target)
for folder in ('HarmonyAssistant','PerformanceExpression','WorkflowCommon','ArrangementAssistant'):
 destination=I/'plugins'/folder;destination.mkdir(parents=True,exist_ok=True)
 for p in (R.parent/folder).iterdir():
  if p.name in {'HarmonyAssistant_MS3.qml','HarmonyAssistant.view.qml','PerformanceExpression_MS3.qml','PerformanceExpression.view.qml'}:continue
  if p.is_file() and p.suffix in ('.qml','.js','.md'):shutil.copyfile(p,destination/p.name)
shutil.copytree(H/'share/workflow',I/'workflow',dirs_exist_ok=True)
for translation in (H/'share/locale').glob('*.qm'):
 copy_changed(translation,I/'locale'/translation.name)
package=R/'out/mcp-dist/MuseScoreMCP'
assert (package/'MuseScoreMCP.exe').is_file(), '请先运行 P2/build_mcp.py'
shutil.copytree(package,I/'bin/tools/mcp',dirs_exist_ok=True,copy_function=copy_changed)
configuration=I/'bin/kumo.ini'
if not configuration.exists():shutil.copy2(H/'personal/kumo.ini',configuration)
# Retire only the six known files previously shipped by this project. A changed
# file is retained for inspection; plugin discovery already omits its old entry.
retired=[]
for folder in ('HarmonyAssistant','PerformanceExpression','ReferencePlayer'):
 for name in (folder+'_MS3.qml',folder+'.view.qml'):
  current=I/'plugins'/folder/name
  if not current.is_file():continue
  resolved=current.resolve()
  assert resolved.is_relative_to((I/'plugins').resolve()), '清理路径超出插件安装目录'
  known=[]
  source_file=R.parent/folder/name
  if source_file.is_file():known.append(source_file.read_bytes())
  historical=subprocess.run(['git','show','personal-v0.62.0:share/plugins/'+folder+'/'+name],cwd=H,capture_output=True)
  if historical.returncode==0:known.append(historical.stdout)
  if current.read_bytes() not in known:
   print('保留有个人修改的旧文件：',current);continue
  saved=R/'out/retired-063'/folder/name;saved.parent.mkdir(parents=True,exist_ok=True)
  if not saved.exists():shutil.copy2(current,saved)
  current.unlink();retired.append(str(current))
for p in (R/'native/personal').rglob('*'):
 if not p.is_file():continue
 destination=I/'personal'/p.relative_to(R/'native/personal');destination.parent.mkdir(parents=True,exist_ok=True)
 maintained=H/'personal/USER_GUIDE.md' if p.relative_to(R/'native/personal').as_posix()=='USER_GUIDE.md' else p
 shutil.copyfile(maintained,destination)
print('已更新现有程序：',target)
print('SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
print('旧入口已备份并整理：',len(retired))
print('扩展配置已保留：',configuration)
