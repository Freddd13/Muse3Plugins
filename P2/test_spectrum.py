"""Exercise the pinned FFT module in the existing isolated runtime."""
from pathlib import Path
import os, subprocess, sys
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
B=H/'msvc.build_harmony_release_x64'
OUT=R.parent/'P1/out/final-regression'
source=(H/'personal/tools/test_harmony_gui.py').read_text('utf8').replace('timeout=45','timeout=120')
env=dict(os.environ,SPECTRUM_FORMAT_FIXTURES=str(R/'native/mtest/mscore/spectrum/fixtures'),KUMO_SPECTRUM_MODULE=str(B/'mscore/referenceaudio/Release/kumo_referenceaudio.dll'))
raise SystemExit(subprocess.call([sys.executable,'-X','utf8','-c',source,str(B/'mtest/mscore/spectrum/Release/tst_spectrum.exe'),str(I),str(OUT)],env=env))
