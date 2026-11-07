from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1]
formatter='C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/Llvm/x64/bin/clang-format.exe'
style='{BasedOnStyle: LLVM, IndentWidth: 4, ColumnLimit: 100, BreakBeforeBraces: Linux, PointerAlignment: Left, SortIncludes: false}'
names=list((R/'P2/native/mscore/scorevideo').glob('*'))+list((R/'P2/native/mscore/referenceaudio').glob('mediaexport*'))+[R/'P2/native/mtest/mscore/pluginhost/scorevideo_164_tests.inc',R/'P2/native/mtest/mscore/pluginhost/reference_163_tests.inc']
for path in names:
    path.write_bytes(subprocess.check_output([formatter,'-style='+style],input=path.read_bytes()).replace(b'\r\n',b'\n'))
