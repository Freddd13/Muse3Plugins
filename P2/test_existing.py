from pathlib import Path
import os, re, subprocess, sys, json
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64';B=H/'msvc.build_harmony_release_x64';OUT=P/'P1/out/final-regression'
source=(H/'personal/tools/test_harmony_gui.py').read_text('utf8').replace('timeout=45','timeout=180')
env=dict(os.environ,P0_TEST_SOUNDFONT=str(I/'sound/MuseScore_General.sf3'),MTEST_DIFF_DIR='E:/Git/usr/bin',PERFORMANCE_NO_SYSTEM_CLIPBOARD='1')
batch=os.environ.get('P2_TEST_BATCH','059')
if os.environ.get('P2_TEST_SPECTRUM'):
 source=source.replace("# Qt's style loader","stage_file(Path("+repr(str(B/'mscore/referenceaudio/Release/kumo_referenceaudio.dll'))+"),runtime/'bin/kumo_referenceaudio.dll')\n# Qt's style loader")
summary=R/('out/'+batch+'-existing.json')
results=json.loads(summary.read_text('utf8')) if summary.exists() else {}
for name in (sys.argv[1:] or ('p1native','performanceeditor')):
 if name not in ('p1native','performanceeditor'):raise ValueError(name)
 log=R/('out/'+batch+'-'+name+'-run.txt')
 with log.open('wb') as stream:
  code=subprocess.call([sys.executable,'-X','utf8','-c',source,str(B/('mtest/mscore/'+name+'/Release/tst_'+name+'.exe')),str(I),str(OUT)],env=env,stdout=stream,stderr=subprocess.STDOUT)
 content=log.read_text('utf8',errors='replace');counts=re.search(r'Totals: (\d+) passed, (\d+) failed, (\d+) skipped',content)
 results[name]={'exit':code,'counts':list(counts.groups()) if counts else None}
 print(name,results[name],flush=True)
summary.write_text(json.dumps(results,indent=2),'utf8')
raise SystemExit(int(any(r['exit'] for r in results.values())))
