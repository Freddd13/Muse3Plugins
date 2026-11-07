from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
names=['mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/pluginhost/timing_161_tests.inc','personal/VERSION']
for name in names:
    target=HOST/name
    if name not in files:files[name]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
test=NATIVE/names[0];text=test.read_text('utf8')
if 'void performanceTimingPersistence161();' not in text:text=text.replace('      void midiTracksPersistence160();','      void performanceTimingPersistence161();\n      void performanceTimingOrnaments161_data();\n      void performanceTimingOrnaments161();\n      void performanceTimingEditor161();\n      void midiTracksPersistence160();',1)
if '#include "timing_161_tests.inc"' not in text:text=text.replace('#include "miditracks_160_tests.inc"','#include "miditracks_160_tests.inc"\n#include "timing_161_tests.inc"',1)
test.write_bytes(text.encode('utf8'))
(NATIVE/'personal/VERSION').write_bytes(b'0.161.0\n')
record.write_text(json.dumps(files,indent=2),encoding='utf8')
runner=ROOT/'Repairs/run_161_checks.py'
runner.write_bytes((ROOT/'Repairs/run_160_checks.py').read_text('utf8').replace('repair-160','repair-161').encode('utf8'))
print('Prepared timing checks and version 0.161.0')
