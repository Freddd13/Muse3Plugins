from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];formatter='C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/Llvm/x64/bin/clang-format.exe'
style='{BasedOnStyle: LLVM, IndentWidth: 4, ColumnLimit: 100, BreakBeforeBraces: Linux, PointerAlignment: Left, SortIncludes: false}'
for name in ['mscore/workflow/referencecontrols.cpp','mscore/workflow/referencecontrols.h','mtest/mscore/pluginhost/reference_163_tests.inc']:
    path=ROOT/'P2/native'/name;path.write_bytes(subprocess.check_output([formatter,'-style='+style],input=path.read_bytes()).replace(b'\r\n',b'\n'))
