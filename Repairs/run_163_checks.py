"""Actual Widgets checks, with the N7 media DLL in the isolated runtime."""
from pathlib import Path
import os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';BUILD=HOST/'msvc.build_harmony_release_x64';OUT=ROOT/'P2/out/repair-163';runtime=ROOT/'P1/out/final-regression/runtime/bin'
suite=sys.argv[1];target=runtime/('tst_'+suite+'.exe')
shutil.copy2(BUILD/('mtest/mscore/'+suite+'/Release/'+target.name),target)
shutil.copy2(BUILD/'mscore/referenceaudio/Release/kumo_referenceaudio.dll',runtime/'kumo_referenceaudio.dll')
panel='workflow/panels/ReferencePlayer/ReferencePlayer.view.qml'
backup=OUT/'previous-ReferencePlayer.view.qml'
if not backup.is_file():shutil.copy2(runtime.parent/panel,backup)
shutil.copy2(HOST/'share'/panel,runtime.parent/panel)
env=dict(os.environ,QT_QPA_PLATFORM='windows',QT_QUICK_BACKEND='software',QML_DISABLE_DISK_CACHE='1',KUMO_MCP_AUTOSTART='0',HARMONY_TEST_ARTIFACTS=str(OUT),PERFORMANCE_NO_SYSTEM_CLIPBOARD='1',P0_TEST_SOUNDFONT=str(HOST/'msvc.install_repair_current_x64/sound/MuseScore_General.sf3'),P2_REFERENCE_LONG_AUDIO=str(ROOT/'P2/out/repair-162/long-audio'),TEMP=str(ROOT/'P2/out/check-temp'),TMP=str(ROOT/'P2/out/check-temp'))
log=OUT/(suite+'-'+sys.argv[2]+'.txt');result=subprocess.run([str(target),*sys.argv[2:],'-o',str(log)+',txt'],cwd=runtime,env=env,timeout=240)
for line in log.read_text('utf8',errors='replace').splitlines():
    if line.startswith(('PASS','FAIL','QFATAL','Totals:')):print(line,flush=True)
print('exit',result.returncode,'log',log,flush=True);raise SystemExit(result.returncode)
