"""Build the checked startup repair in the existing E-drive build."""
from pathlib import Path
import os
import subprocess

R=Path(__file__).resolve().parents[1]
H=R.parent/'muse3_dev/MuseScore'
O=R/'P2/out/usability-167'
build='C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe'
env=dict(os.environ,_CL_='/MP2',TEMP=str(R/'P2/out/compile-temp'),TMP=str(R/'P2/out/compile-temp'))
with (O/'build-program.txt').open('w',encoding='utf8') as stream:
    result=subprocess.call([build,str(H/'msvc.build_harmony_release_x64/main/mscore.vcxproj'),
        '/nologo','/m:1','/p:Configuration=Release','/p:Platform=x64'],cwd=H,env=env,
        stdout=stream,stderr=subprocess.STDOUT)
print('\n'.join(line for line in (O/'build-program.txt').read_text('utf8',errors='replace').splitlines()
                if 'error ' in line or '错误' in line)[-2500:])
print('Application build:',result)
raise SystemExit(result)
