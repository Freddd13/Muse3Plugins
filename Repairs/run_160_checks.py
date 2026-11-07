"""Run native checks with live output and separate E-drive artifacts."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore'
suite=sys.argv[1]
if suite not in ('pluginhost','performanceeditor'):raise ValueError(suite)
binary=HOST/('msvc.build_harmony_release_x64/mtest/mscore/'+suite+'/Release/tst_'+suite+'.exe')
runtime=ROOT/'P1/out/final-regression/runtime/bin'
target=runtime/binary.name;shutil.copy2(str(binary),str(target))
output=ROOT/'P2/out/repair-160';output.mkdir(exist_ok=True)
temporary=ROOT/'P2/out/check-temp';temporary.mkdir(exist_ok=True)
env=dict(os.environ,QT_QPA_PLATFORM=os.environ.get('REPAIR_QPA','windows'),QT_QUICK_BACKEND='software',QML_DISABLE_DISK_CACHE='1',KUMO_MCP_AUTOSTART='0',
 HARMONY_TEST_ARTIFACTS=str(output),PERFORMANCE_NO_SYSTEM_CLIPBOARD='1',
 P0_TEST_SOUNDFONT=str(HOST/'msvc.install_repair_current_x64/sound/MuseScore_General.sf3'),
 KUMO_KAWAI_SF2='E:/music_fonts/[GD] Kawai ES100 Concert Grand 1 [V3].sf2',TEMP=str(temporary),TMP=str(temporary))
log=output/(suite+'-'+sys.argv[2]+'.txt')
process=subprocess.run([str(target),*sys.argv[2:],'-o',str(log)+',txt'],cwd=runtime,env=env,timeout=180)
code=process.returncode
data=log.read_bytes()
try:decoded=data.decode('utf8')
except UnicodeDecodeError:decoded=data.decode('gb18030',errors='replace')
for text in decoded.splitlines():
    if text.startswith(('PASS','FAIL','QINFO','QFATAL','Totals:','********')):print(text,flush=True)
print('exit:',code,'log:',log,flush=True)
raise SystemExit(code)
