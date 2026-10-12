"""Build and run selected music-model cases with the existing isolated Qt runner."""
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
BUILD=HOST/'msvc.build_harmony_release_x64'
MSBUILD=r'C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
case=sys.argv[1]
if case not in ['inputrhythm','beam','readwriteundoreset','midi']:raise ValueError('Unknown case')
out=ROOT/'Repairs/out'/case;out.mkdir(parents=True,exist_ok=True)
if '--build' in sys.argv:
 with (out/'build.log').open('wb') as log:
  subprocess.run([MSBUILD,str(BUILD/'mtest/libmscore'/case/('tst_'+case+'.vcxproj')),'/p:Configuration=Release','/p:Platform=x64','/p:BuildProjectReferences=false','/p:ForceImportBeforeCppTargets='+str(ROOT/'P0/tests/NoPch.props'),'/m:1','/v:minimal','/nologo'],cwd=HOST,stdout=log,stderr=subprocess.STDOUT,check=True)
env=os.environ.copy();env['MTEST_DIFF_DIR']=r'E:\Git\usr\bin';env['P0_TEST_SOUNDFONT']=str(HOST/'msvc.install_p1_x64/sound/MuseScore_General.sf3')
with (out/'runner.log').open('wb') as log:
 result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'Repairs/tests/run_gui_cases.py'),str(BUILD/'mtest/libmscore'/case/'Release'/('tst_'+case+'.exe')),str(HOST/'msvc.install_p1_x64'),str(out)],env=env,stdout=log,stderr=subprocess.STDOUT)
import re
raw=(out/'gui.txt').read_text(encoding='utf8',errors='replace') if (out/'gui.txt').exists() else ''
count=re.search(r'Totals:.*',raw)
print(case,count.group() if count else '没有得到测试结果',flush=True)
if result.returncode:print('\n'.join(raw.splitlines()[-15:]),flush=True)
sys.exit(result.returncode)
