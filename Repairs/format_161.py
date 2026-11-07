"""Format the new N5 implementation files only."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
formatter=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/Llvm/x64/bin/clang-format.exe')
style='{BasedOnStyle: LLVM, IndentWidth: 4, ColumnLimit: 100, BreakBeforeBraces: Linux, PointerAlignment: Left, SortIncludes: false}'
files=['libmscore/performancetiming.cpp','libmscore/performancetiming.h','mscore/performanceeditor/timingeditor.cpp','mscore/performanceeditor/timingeditor.h','mtest/mscore/pluginhost/timing_161_tests.inc']
for name in files:
    path=ROOT/'P2/native'/name
    result=subprocess.run([str(formatter),'-style='+style],input=path.read_bytes(),capture_output=True,check=True)
    path.write_bytes(result.stdout.replace(b'\r\n',b'\n'))
print('Formatted',len(files),'new N5 files')
