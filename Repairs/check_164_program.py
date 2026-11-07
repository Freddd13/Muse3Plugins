"""Check the final program against installed 0.163 and the stock round trip."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-164';INSTALL=HOST/'msvc.install_repair_current_x64/bin'
latest=OUT/'checked-MuseScore3Evo.exe';shutil.copy2(HOST/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe',latest)
binary=latest.read_bytes();assert all(name in binary for name in (b'0.164.0',b'Kumo branch',b'Freddd13'))
previous=OUT/'previous-MuseScore3Evo.exe'
if not previous.is_file():previous=INSTALL/'MuseScore3Evo.exe'
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',KUMO_MCP_AUTOSTART='0',PATH=str(INSTALL)+os.pathsep+os.environ['PATH'],QT_PLUGIN_PATH=str(INSTALL),TEMP=str(ROOT/'P2/out/check-temp'),TMP=str(ROOT/'P2/out/check-temp'))
source=HOST/'mtest/mscore/scoreobserver/piano.mscx';report={}
for label,program in (('previous',previous),('new',latest)):
    for suffix in ('mid','pdf'):
        target=OUT/(label+'-ordinary.'+suffix)
        result=subprocess.run([str(program),'-c',str(OUT/(label+'-cli-settings')),'-o',str(target),str(source)],env=env,cwd=INSTALL,capture_output=True,timeout=60)
        (OUT/(label+'-cli-'+suffix+'.txt')).write_bytes(result.stdout+result.stderr)
        if result.returncode or not target.is_file():raise ValueError(str(target)+' export failed')
        report[label+'-'+suffix]={'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
assert report['new-mid']==report['previous-mid'],'Ordinary MIDI changed'
for label,source in (('video',OUT/'score-video-164.mscz'),('stock',ROOT/'P2/out/compat-3.6.2/roundtrip-video164.mscz')):
    for suffix in ('mid','pdf'):
        target=OUT/(label+'-program.'+suffix)
        result=subprocess.run([str(latest),'-c',str(OUT/(label+'-cli-settings')),'-o',str(target),str(source)],env=env,cwd=INSTALL,capture_output=True,timeout=60)
        (OUT/(label+'-cli-'+suffix+'.txt')).write_bytes(result.stdout+result.stderr)
        if result.returncode or not target.is_file():raise ValueError(label+' program export failed')
        report[label+'-'+suffix]={'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
assert report['video-mid']==report['stock-mid'],'Ordinary-version reference roundtrip changed MIDI'
report['version']='0.164.0';report['sha256']=hashlib.sha256(binary).hexdigest()
(OUT/'program-checks.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
