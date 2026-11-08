"""Start the built application with a copy of the existing workspace."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
R=Path(__file__).resolve().parents[1]; H=R.parent/'muse3_dev/MuseScore'; O=R/'P2/out/repair-165'
runtime=R/'P1/out/final-regression/runtime'; binary=runtime/'bin/MuseScore3Evo.exe'
source=H/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
shutil.copy2(source,binary)
config=O/'workspace'; (config/'MuseScore').mkdir(parents=True,exist_ok=True)
settings=Path('C:/Users/Fred/AppData/Roaming/MuseScore/MuseScore3Evo.ini')
shutil.copy2(settings,config/'MuseScore/MuseScore3Evo.ini')
workspaces=Path('C:/Users/Fred/AppData/Local/MuseScore/MuseScore3Evo/workspaces')
shutil.copytree(workspaces,config/'workspaces',dirs_exist_ok=True)
score=O/'动态乐谱操作检查.mscz'
if not score.exists():shutil.copy2(R/'P2/out/repair-164/score-video-164.mscz',score)
env=dict(os.environ,KUMO_MCP_AUTOSTART='0',TEMP=str(R/'P2/out/check-temp'),TMP=str(R/'P2/out/check-temp'))
log=(O/'application.txt').open('w',encoding='utf8')
process=subprocess.Popen([str(binary),'-c',str(config),str(score)],cwd=binary.parent,env=env,stdout=log,stderr=subprocess.STDOUT)
result={'pid':process.pid,'program':str(binary),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'workspaceSource':str(workspaces/'kumo.workspace'),'settingsSource':str(settings),'score':str(score)}
(O/'review-program.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
