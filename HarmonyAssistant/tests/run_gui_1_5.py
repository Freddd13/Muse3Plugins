"""Isolated native GUI runner; avoid copying validation outputs into the runtime."""
from pathlib import Path
import sys
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
script=(repo/'personal/tools/test_harmony_gui.py').read_text(encoding='utf-8')
installed=Path(sys.argv[2]).resolve();output=Path(sys.argv[3]).resolve()
assert installed not in output.parents,'Test output must be outside installation'
script=script.replace('for source in installed.iterdir():','for source in installed.iterdir():\n    if source.name=="validation":continue',1)
exec(compile(script,str(repo/'personal/tools/test_harmony_gui.py'),'exec'))
