"""Copy the scoped 0.166 repair to the native workspace."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-166'
names = ['mscore/scorevideo/scorevideo.h', 'mscore/scorevideo/scorevideo.cpp',
         'mscore/scorevideo/scorevideoframe.cpp', 'mscore/workflow/arrangementimages.cpp',
         'mtest/mscore/pluginhost/scorevideo_166_review.inc']
p = N / 'mtest/mscore/pluginhost/tst_pluginhost.cpp'
t = p.read_text('utf8')
if 'void scoreVideoFidelity166();' not in t:
    t = t.replace('      void scoreVideoWorkspace164();',
                  '      void scoreVideoFidelity166();\n      void scoreVideoWorkspace164();', 1)
    t = t.replace('#include "scorevideo_164_tests.inc"',
                  '#include "scorevideo_164_tests.inc"\n#include "scorevideo_166_review.inc"', 1)
    p.write_text(t, encoding='utf8', newline='\n')
names.append('mtest/mscore/pluginhost/tst_pluginhost.cpp')
for name in names:
    target = H / name
    if target.exists() and not (O / 'sync-files.json').exists():
        result = subprocess.run(['git', 'diff', '--quiet', '--', name], cwd=H)
        assert result.returncode == 0, name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(N / name, target)
section = (O / 'agents-addition.md').read_text('utf8')
agents = H / 'AGENTS.md'
t = agents.read_text('utf8')
at = '以上作为当前执行原则，指导后文的检查记录；每次工作按实际需要取舍。'
if section not in t:
    assert at in t
    agents.write_text(t.replace(at, section + '\n' + at, 1), encoding='utf8', newline='\n')
(O / 'sync-files.json').write_text(json.dumps(names, indent=2), encoding='utf8')
print('Synced native image repair and comparison workflow.')
