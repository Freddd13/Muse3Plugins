"""Build the repaired application using the existing build directory."""
from pathlib import Path
import os, subprocess
R=Path(__file__).resolve().parents[1]; H=R.parent/'muse3_dev/MuseScore'; O=R/'P2/out/repair-165'
msbuild='C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe'
env=dict(os.environ,_CL_='/MP2',TEMP=str(R/'P2/out/compile-temp'),TMP=str(R/'P2/out/compile-temp'))
log=O/'build.txt'
with log.open('w',encoding='utf8') as stream:
    result=subprocess.run([msbuild,str(H/'msvc.build_harmony_release_x64/main/mscore.vcxproj'),'/nologo','/m:1','/p:Configuration=Release','/p:Platform=x64'],env=env,cwd=H,stdout=stream,stderr=subprocess.STDOUT)
lines=log.read_text('utf8',errors='replace').splitlines()
print('\n'.join(line for line in lines if 'error ' in line or '错误' in line)[-4500:])
print('Application build:',result.returncode,str(log))
raise SystemExit(result.returncode)
