"""Run native window checks in the existing test runtime."""
from pathlib import Path
import os, re, shutil, subprocess, sys
R=Path(__file__).resolve().parent
P=R.parent
H=P.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
B=H/'msvc.build_harmony_release_x64'
OUT=P/'P1/out/final-regression'
TEMP=OUT/'tmp';TEMP.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,TEMP=str(TEMP),TMP=str(TEMP),KUMO_MCP_AUTOSTART="0",P0_TEST_SOUNDFONT=str(I/'sound/MuseScore_General.sf3'),MTEST_DIFF_DIR='E:/Git/usr/bin')
source=(H/'personal/tools/test_harmony_gui.py').read_text('utf8').replace('timeout=45','timeout=180')
if os.environ.get('P2_TEST_NATIVE_RENDER'):
 env.pop('QT_QUICK_BACKEND',None)
 source=source.replace("QT_QUICK_BACKEND='software',",'')
if os.environ.get('P2_TEST_OFFSCREEN'):
 source=source.replace("env.pop('QT_QPA_PLATFORM', None)", "env['QT_QPA_PLATFORM']='offscreen'")
source=source.replace("# Qt's style loader", "for folder in ('HarmonyAssistant','ArrangementAssistant','ArrangementVariants','PerformanceExpression','WorkflowCommon'):\n for p in (Path("+repr(str(P))+ ")/folder).iterdir():\n  if p.is_file() and p.suffix in ('.qml','.js','.md'):stage_file(p,runtime/'plugins'/folder/p.name)\n# Qt's style loader")
source=source.replace("# Qt's style loader", "for p in Path("+repr(str(H/'share/workflow'))+").rglob('*'):\n if p.is_file():\n  destination=runtime/'workflow'/p.relative_to(Path("+repr(str(H/'share/workflow'))+"))\n  destination.parent.mkdir(parents=True,exist_ok=True)\n  stage_file(p,destination)\nstage_file(Path("+repr(str(H/'personal/kumo.ini'))+"),runtime/'bin/kumo.ini')\n# Qt's style loader")
source=source.replace("# Qt's style loader", "stage_file(Path("+repr(str(B/'audio/vst/Release/MuseScoreVstHost.exe'))+"),runtime/'bin/MuseScoreVstHost.exe')\n# Qt's style loader")
if os.environ.get('P2_TEST_SPECTRUM'):
 source=source.replace("# Qt's style loader","stage_file(Path("+repr(str(B/'mscore/referenceaudio/Release/kumo_referenceaudio.dll'))+"),runtime/'bin/kumo_referenceaudio.dll')\n# Qt's style loader")
if os.environ.get('P2_TEST_GUIDE'):
 source=source.replace("# Qt's style loader", "subprocess.run([sys.executable,'-X','utf8',"+repr(str(H/'personal/tools/package_user_guide.py'))+",str(runtime)],check=True)\n# Qt's style loader")
if os.environ.get('P2_TEST_MCP'):
 source=source.replace("# Qt's style loader", "for p in Path("+repr(str(R/'out/mcp-dist/MuseScoreMCP'))+").rglob('*'):\n if p.is_file():\n  destination=runtime/'bin/tools/mcp/test-current'/p.relative_to(Path("+repr(str(R/'out/mcp-dist/MuseScoreMCP'))+"))\n  destination.parent.mkdir(parents=True,exist_ok=True)\n  stage_file(p,destination)\n(runtime/'bin/tools/mcp/current.json').write_text('{\"directory\":\"test-current\"}',encoding='utf8')\n# Qt's style loader")
 if os.environ.get('P2_MCP_PACKAGE'):
  source=source.replace(str(R/'out/mcp-dist/MuseScoreMCP'),str(Path(os.environ['P2_MCP_PACKAGE'])))
if os.environ.get('P2_FEATURE_GATE_OFF'):
 source=source.replace("# Qt's style loader", "(runtime/'bin/kumo.ini').write_text('[features]\\nenable_exp_feature=false\\n',encoding='ascii')\n# Qt's style loader")
if sys.argv[1:]:source=source.replace("[str(target), '-o', str(log) + ',txt']",repr(['__TEST_TARGET__']+sys.argv[1:])+" + ['-o', str(log) + ',txt']").replace("'__TEST_TARGET__'",'str(target)')
code=subprocess.call([sys.executable,'-X','utf8','-c',source,str(B/'mtest/mscore/pluginhost/Release/tst_pluginhost.exe'),str(I),str(OUT)],env=env)
batch=os.environ.get('P2_TEST_BATCH','')
if batch:
 if not re.fullmatch(r'[A-Za-z0-9_-]+',batch):raise ValueError('P2_TEST_BATCH must be a file label')
 log=OUT/'gui.txt'
 if log.is_file():shutil.copy2(log,R/'out'/f'{batch}-pluginhost.txt')
raise SystemExit(code)
