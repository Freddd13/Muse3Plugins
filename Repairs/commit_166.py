"""Commit only this repair; preserve unrelated native documentation edits."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-166'
sys.stdout.reconfigure(encoding='utf8', errors='replace')

def git(repo, *args, data=None):
    result = subprocess.run(['git', *args], cwd=repo, input=data, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf8', errors='replace'))
    return result.stdout

def blob(name, content):
    value = git(H, 'hash-object', '-w', '--stdin', data=content).decode().strip()
    git(H, 'update-index', '--cacheinfo', '100644,' + value + ',' + name)

files = json.loads((O / 'release-files.json').read_text('utf8'))
checked = json.loads((O / 'program-checks.json').read_text('utf8'))
assert hashlib.sha256((H/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe').read_bytes()).hexdigest() == checked['sha256']
assert not git(H, 'diff', '--cached', '--name-only').strip()
assert not git(R, 'diff', '--cached', '--name-only').strip()
for name in files:
    source = N / name
    if source.suffix != '.png':
        source.write_bytes(source.read_bytes().replace(b'\r\n', b'\n'))
    if name != 'personal/USER_GUIDE.md':
        native = (H/name).read_bytes()
        if source.suffix != '.png':
            native = native.replace(b'\r\n', b'\n')
        assert native == source.read_bytes(), name
git(H, 'add', '--', *[name for name in files if name != 'personal/USER_GUIDE.md'])
blob('personal/USER_GUIDE.md', (N/'personal/USER_GUIDE.md').read_bytes())
agents = git(H, 'show', 'HEAD:AGENTS.md').decode('utf8')
section = (O/'agents-addition.md').read_text('utf8')
anchor = '以上作为当前执行原则，指导后文的检查记录；每次工作按实际需要取舍。'
assert section.strip() not in agents and agents.count(anchor) == 1
blob('AGENTS.md', agents.replace(anchor, section + '\n' + anchor, 1).encode('utf8'))
assert set(git(H,'diff','--cached','--name-only').decode().splitlines()) == set(files+['AGENTS.md'])
git(H, 'diff', '--cached', '--check')
print(git(H, 'diff', '--cached', '--stat').decode('utf8'))
print(git(H, 'commit', '-m', 'Fix 0.166 native score fidelity in video and AI images').decode('utf8'))
git(H, 'tag', 'personal-v0.166.0')
native = git(H, 'rev-parse', 'HEAD').decode().strip()
for name in files:
    assert git(H, 'show', 'HEAD:'+name) == (N/name).read_bytes(), name
paths = ['AGENTS.md'] + ['P2/native/'+name for name in files]
paths += ['Planning/ROUND_166_REVIEW.md', 'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
paths += ['Repairs/'+name for name in ['prepare_166.py','sync_166.py','review_166.py',
    'review_166_workflows.py','document_166.py','finish_166.py','build_166.py','commit_166.py']]
git(R, 'add', '--', *paths)
git(R, 'diff', '--cached', '--check')
print(git(R, 'commit', '-m', 'Review N1-N9 and preserve native score typography in video').decode('utf8'))
(O/'commits.json').write_text(json.dumps({'native':native,
    'plugins':git(R,'rev-parse','HEAD').decode().strip()}, indent=2), encoding='utf8')
