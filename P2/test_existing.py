from pathlib import Path
import os, re, subprocess, sys, json
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64';B=H/'msvc.build_harmony_release_x64';OUT=P/'P1/out/final-regression'
TEMP=OUT/'tmp';TEMP.mkdir(parents=True,exist_ok=True)
source=(H/'personal/tools/test_harmony_gui.py').read_text('utf8').replace('timeout=45','timeout=180')
env=dict(os.environ,TEMP=str(TEMP),TMP=str(TEMP),KUMO_MCP_AUTOSTART="0",P0_TEST_SOUNDFONT=str(I/'sound/MuseScore_General.sf3'),MTEST_DIFF_DIR='E:/Git/usr/bin',PERFORMANCE_NO_SYSTEM_CLIPBOARD='1')
if os.environ.get('P2_TEST_OFFSCREEN'):
 source=source.replace("env.pop('QT_QPA_PLATFORM', None)", "env['QT_QPA_PLATFORM']='offscreen'")
batch=os.environ.get('P2_TEST_BATCH','059')
if os.environ.get('P2_TEST_SPECTRUM'):
 source=source.replace("# Qt's style loader","stage_file(Path("+repr(str(B/'mscore/referenceaudio/Release/kumo_referenceaudio.dll'))+"),runtime/'bin/kumo_referenceaudio.dll')\n# Qt's style loader")
source=source.replace("# Qt's style loader", "for p in Path("+repr(str(H/'share/workflow'))+").rglob('*'):\n if p.is_file():\n  destination=runtime/'workflow'/p.relative_to(Path("+repr(str(H/'share/workflow'))+"))\n  destination.parent.mkdir(parents=True,exist_ok=True)\n  stage_file(p,destination)\nstage_file(Path("+repr(str(H/'personal/kumo.ini'))+"),runtime/'bin/kumo.ini')\n# Qt's style loader")
for folder in ('HarmonyAssistant','PerformanceExpression','WorkflowCommon','ArrangementAssistant','ArrangementVariants'):
 source=source.replace("# Qt's style loader", "for p in Path("+repr(str(P/folder))+").iterdir():\n if p.is_file() and p.suffix in ('.qml','.js'):\n  destination=runtime/'plugins'/"+repr(folder)+"/p.name\n  destination.parent.mkdir(parents=True,exist_ok=True)\n  stage_file(p,destination)\n# Qt's style loader")
slots=os.environ.get('P2_EXISTING_SLOTS','').split()
if slots:
 source=source.replace("[str(target), '-o', str(log) + ',txt']",repr(['__TEST_TARGET__']+slots)+" + ['-o', str(log) + ',txt']").replace("'__TEST_TARGET__'",'str(target)')
summary=R/('out/'+batch+'-existing.json')
results=json.loads(summary.read_text('utf8')) if summary.exists() else {}
for name in (sys.argv[1:] or ('p1native','performanceeditor')):
 if name not in ('p0native','p1native','performanceeditor','nativeui'):raise ValueError(name)
 log=R/('out/'+batch+'-'+name+'-run.txt')
 # The normal-window suite uses the same renderer as the released application.
 test_source=source.replace("QT_QUICK_BACKEND='software'", "QT_QUICK_BACKEND=''") if name=='nativeui' else source
 with log.open('wb') as stream:
  code=subprocess.call([sys.executable,'-X','utf8','-c',test_source,str(B/('mtest/mscore/'+name+'/Release/tst_'+name+'.exe')),str(I),str(OUT)],env=env,stdout=stream,stderr=subprocess.STDOUT)
 content=log.read_text('utf8',errors='replace');counts=re.search(r'Totals: (\d+) passed, (\d+) failed, (\d+) skipped',content)
 results[name]={'exit':code,'counts':list(counts.groups()) if counts else None}
 print(name,results[name],flush=True)
summary.write_text(json.dumps(results,indent=2),'utf8')
raise SystemExit(int(any(r['exit'] for r in results.values())))
