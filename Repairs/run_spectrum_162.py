from pathlib import Path
import os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';BUILD=HOST/'msvc.build_harmony_release_x64';OUT=ROOT/'P2/out/repair-162'
runtime=ROOT/'P1/out/final-regression/runtime/bin';target=runtime/'tst_spectrum.exe'
shutil.copy2(BUILD/'mtest/mscore/spectrum/Release/tst_spectrum.exe',target)
module=BUILD/'mscore/referenceaudio/Release/kumo_referenceaudio.dll'
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',KUMO_SPECTRUM_MODULE=str(module),SPECTRUM_FORMAT_FIXTURES=str(HOST/'mtest/mscore/spectrum/fixtures'),P2_REFERENCE_LONG_AUDIO=str(OUT/'long-audio'),HARMONY_TEST_ARTIFACTS=str(OUT),KUMO_MCP_AUTOSTART='0',TEMP=str(ROOT/'P2/out/check-temp'),TMP=str(ROOT/'P2/out/check-temp'))
log=OUT/'spectrum-checks.txt'
result=subprocess.run([str(target),*sys.argv[1:],'-o',str(log)+',txt'],cwd=runtime,env=env,timeout=180)
for line in log.read_text('utf8',errors='replace').splitlines():
    if line.startswith(('PASS','FAIL','QINFO','QFATAL','Totals:')):print(line,flush=True)
print('exit',result.returncode,'log',log);raise SystemExit(result.returncode)
