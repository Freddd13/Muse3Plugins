"""Check the real startup actions and legacy menu restoration in one workflow."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf8', errors='replace')

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
B = H / 'msvc.build_harmony_release_x64'
O = R / 'P2/out/repair-165'
runtime = R / 'P1/out/final-regression/runtime/bin'
msbuild = 'C:/Program Files/Microsoft Visual Studio/2022/Community/MSBuild/Current/Bin/MSBuild.exe'
env = dict(os.environ, _CL_='/MP2', TEMP=str(R / 'P2/out/compile-temp'), TMP=str(R / 'P2/out/compile-temp'))
props = O / 'no-test-pch.props'
props.write_text('<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003"><ItemDefinitionGroup><ClCompile><PrecompiledHeader>NotUsing</PrecompiledHeader></ClCompile></ItemDefinitionGroup></Project>', encoding='utf8')
for name, project in [('app', 'mscore/mscoreapp.vcxproj'), ('testlib', 'mtest/testutils_mscoreapp.vcxproj'), ('workspace', 'mtest/mscore/pluginhost/tst_pluginhost.vcxproj')]:
    log = O / ('build-' + name + '.txt')
    with log.open('w', encoding='utf8') as stream:
        args = [msbuild, str(B / project), '/nologo', '/m:1', '/p:Configuration=Release', '/p:Platform=x64', '/p:BuildProjectReferences=false']
        if name != 'app':
            args.append('/p:ForceImportBeforeCppTargets=' + str(props))
        code = subprocess.call(args, cwd=H, env=env, stdout=stream, stderr=subprocess.STDOUT)
    if code:
        print('\n'.join(line for line in log.read_text('utf8', errors='replace').splitlines() if 'error ' in line or '错误' in line)[-4000:])
        raise SystemExit(code)
    print(name, 'built', flush=True)

target = runtime / 'tst_pluginhost.exe'
shutil.copy2(B / 'mtest/mscore/pluginhost/Release/tst_pluginhost.exe', target)
env.update(QT_QPA_PLATFORM='windows', QT_QUICK_BACKEND='software', QML_DISABLE_DISK_CACHE='1', KUMO_MCP_AUTOSTART='0', HARMONY_TEST_ARTIFACTS=str(O), PERFORMANCE_NO_SYSTEM_CLIPBOARD='1', P0_TEST_SOUNDFONT=str(H / 'msvc.install_repair_current_x64/sound/MuseScore_General.sf3'))
log = O / 'startup-workspace.txt'
code = subprocess.call([str(target), 'scoreVideoWorkspace164', '-o', str(log) + ',txt'], cwd=runtime, env=env, timeout=90)
for line in log.read_text('utf8', errors='replace').splitlines():
    if line.startswith(('PASS', 'FAIL', 'QFATAL', 'Totals:', 'QINFO')):
        print(line, flush=True)
raise SystemExit(code)
