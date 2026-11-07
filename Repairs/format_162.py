from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];formatter='C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/Llvm/x64/bin/clang-format.exe'
style='{BasedOnStyle: LLVM, IndentWidth: 4, ColumnLimit: 100, BreakBeforeBraces: Linux, PointerAlignment: Left, SortIncludes: false}'
for name in ['mscore/referenceaudio/spectrumprojection.cpp','mscore/referenceaudio/spectrumprojection.h','mscore/performanceeditor/spectrumguides.cpp','mtest/mscore/pluginhost/spectrum_162_tests.inc']:
    path=ROOT/'P2/native'/name;data=subprocess.check_output([formatter,'-style='+style],input=path.read_bytes());path.write_bytes(data.replace(b'\r\n',b'\n'))
