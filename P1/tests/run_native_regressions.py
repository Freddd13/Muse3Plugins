# coding: utf-8
"""Relink host tests against current libraries and reuse one isolated runtime."""
from pathlib import Path
import os,sys,subprocess,json,re
ROOT=Path(__file__).resolve().parents[2];HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
OUT=ROOT/'P1/out/final-regression';OUT.mkdir(parents=True,exist_ok=True)
BUILD=HOST/'msvc.build_harmony_release_x64';INSTALL=HOST/'msvc.install_p1_x64'
MSBUILD=r'C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
CASES=['mscore/p1native','mscore/pluginhost','mscore/scoreobserver','mscore/p0native','mscore/performanceeditor','libmscore/midi','libmscore/readwriteundoreset']
selected='--case' in sys.argv
if selected:
 name=sys.argv[sys.argv.index('--case')+1]
 CASES=[case for case in CASES if case.split('/')[-1]==name]
 if not CASES:raise ValueError('Unknown suite: '+name)
if '--build' in sys.argv:
 for case in CASES:
  name=case.split('/')[-1];project=BUILD/'mtest'/case/('tst_'+name+'.vcxproj')
  with (OUT/(name+'-build.log')).open('wb') as log:
   rc=subprocess.call([MSBUILD,str(project),'/p:Configuration=Release','/p:Platform=x64','/p:BuildProjectReferences=false','/p:ForceImportBeforeCppTargets='+str(ROOT/'P0/tests/NoPch.props'),'/m:1','/v:minimal','/nologo'],cwd=str(HOST),stdout=log,stderr=subprocess.STDOUT)
  print('build',name,rc,flush=True)
  if rc:sys.exit(rc)
 sys.exit(0)
summary=json.loads((OUT/'summary.json').read_text(encoding='utf8')) if selected and (OUT/'summary.json').exists() else {}
env=os.environ.copy();env['P0_TEST_SOUNDFONT']=str(INSTALL/'sound/MuseScore_General.sf3');env['MTEST_DIFF_DIR']=r'E:\Git\usr\bin'
for case in CASES:
 name=case.split('/')[-1];exe=BUILD/'mtest'/case/'Release'/('tst_'+name+'.exe')
 with (OUT/(name+'-runner.log')).open('wb') as log:
  rc=subprocess.call([sys.executable,'-X','utf8',str(HOST/'personal/tools/test_harmony_gui.py'),str(exe),str(INSTALL),str(OUT)],env=env,stdout=log,stderr=subprocess.STDOUT)
 raw=(OUT/'gui.txt').read_bytes() if (OUT/'gui.txt').exists() else b'';(OUT/(name+'-gui.txt')).write_bytes(raw)
 found=re.search(r'Totals: (\d+) passed, (\d+) failed, (\d+) skipped',raw.decode('utf8',errors='replace'))
 summary[name]={'exit':rc,'counts':found.groups() if found else None}
 print(name,summary[name],flush=True)
 if rc:print('\n'.join(raw.decode('utf8',errors='replace').splitlines()[-12:]),flush=True)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
sys.exit(int(any(v['exit'] for v in summary.values())))
