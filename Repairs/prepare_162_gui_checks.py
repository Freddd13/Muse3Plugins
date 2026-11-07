"""Register N6 native interaction checks without altering unrelated tests."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-162'
path=OUT/'files.json';files=json.loads(path.read_text('utf8'))
name='mtest/mscore/pluginhost/tst_pluginhost.cpp'
if name not in files:
    data=(HOST/name).read_bytes();files[name]=hashlib.sha256(data).hexdigest()
    (ROOT/'P2/native'/name).write_bytes(data)
target=ROOT/'P2/native'/name;text=target.read_text('utf8')
if 'void spectrumInteraction162();' not in text:
    text=text.replace('      void spectrumInitialSourceAndChoice();','      void spectrumInteraction162();\n      void spectrumSharedTimeline162();\n      void spectrumMidiOverlay162();\n      void spectrumInitialSourceAndChoice();')
    text=text.replace('#include "spectrum_102_tests.inc"','#include "spectrum_102_tests.inc"\n#include "spectrum_162_tests.inc"')
    target.write_text(text,encoding='utf8',newline='\n')
files.setdefault('mtest/mscore/pluginhost/spectrum_162_tests.inc',None)
path.write_text(json.dumps(files,indent=2),encoding='utf8')
