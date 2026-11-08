"""Build the application in the existing E-drive directory."""
from pathlib import Path
import os
import subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
O = R / 'P2/out/repair-166'
env = dict(os.environ, _CL_='/MP2', TEMP=str(R/'P2/out/compile-temp'), TMP=str(R/'P2/out/compile-temp'))
build = 'C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe'
log = O / 'build-program.txt'
with log.open('w', encoding='utf8') as stream:
    code = subprocess.call([build, str(H/'msvc.build_harmony_release_x64/main/mscore.vcxproj'),
                            '/nologo', '/m:1', '/p:Configuration=Release', '/p:Platform=x64'],
                           cwd=H, env=env, stdout=stream, stderr=subprocess.STDOUT)
print('\n'.join(line for line in log.read_text('utf8', errors='replace').splitlines()
                if 'error ' in line or '错误' in line)[-3500:])
print('Application build:', code)
raise SystemExit(code)
