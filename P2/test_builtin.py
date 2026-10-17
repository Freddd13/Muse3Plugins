"""Run native window checks in the existing test runtime."""
from pathlib import Path
import os, subprocess, sys
R=Path(__file__).resolve().parent
P=R.parent
H=P.parent/'muse3_dev/MuseScore'
I=H/'msvc.install_repair_current_x64'
B=H/'msvc.build_harmony_release_x64'
OUT=P/'P1/out/final-regression'
env=dict(os.environ,P0_TEST_SOUNDFONT=str(I/'sound/MuseScore_General.sf3'),MTEST_DIFF_DIR='E:/Git/usr/bin')
source=(H/'personal/tools/test_harmony_gui.py').read_text('utf8').replace('timeout=45','timeout=180')
if sys.argv[1:]:source=source.replace("[str(target), '-o', str(log) + ',txt']",repr(['__TEST_TARGET__']+sys.argv[1:])+" + ['-o', str(log) + ',txt']").replace("'__TEST_TARGET__'",'str(target)')
raise SystemExit(subprocess.call([sys.executable,'-X','utf8','-c',source,str(B/'mtest/mscore/pluginhost/Release/tst_pluginhost.exe'),str(I),str(OUT)],env=env))
