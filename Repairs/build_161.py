"""Build selected targets in the existing E-drive build directory."""
from pathlib import Path
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/'muse3_dev/MuseScore'
BUILD=HOST/'msvc.build_harmony_release_x64'
MSBUILD=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe')
env=dict(os.environ,_CL_='/MP2')
env['TEMP']=env['TMP']=str(ROOT/'P2/out/compile-temp')
props=ROOT/'P2/out/NoTestPch161.props'
props.write_text('<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><ItemDefinitionGroup><ClCompile><PrecompiledHeader>NotUsing</PrecompiledHeader></ClCompile></ItemDefinitionGroup></Project>',encoding='utf8')
targets={
 'app':('mscore/mscoreapp.vcxproj',True),
 'testlib':('mtest/testutils_mscoreapp.vcxproj',False),
 'tests':('mtest/mscore/pluginhost/tst_pluginhost.vcxproj',False),
 'editor-tests':('mtest/mscore/performanceeditor/tst_performanceeditor.vcxproj',False),
 'exe':('main/mscore.vcxproj',True),
}
for target in sys.argv[1:]:
    project,refs=targets[target]
    args=[str(MSBUILD),str(BUILD/project),'/nologo','/m:1','/p:Configuration=Release','/p:Platform=x64','/p:BuildProjectReferences='+str(refs).lower()]
    if target in ('testlib','tests','editor-tests'):args.append('/p:ForceImportBeforeCppTargets='+str(props))
    log=ROOT/('P2/out/161-'+target+'-build.txt')
    with log.open('w',encoding='utf8') as stream:
        result=subprocess.run(args,cwd=HOST,env=env,stdout=stream,stderr=subprocess.STDOUT)
    lines=log.read_text('utf8',errors='replace').splitlines()
    print('\n'.join([line for line in lines if 'error ' in line or '错误' in line][-25:]),flush=True)
    print(target,result.returncode,str(log),flush=True)
    if result.returncode:raise SystemExit(result.returncode)
