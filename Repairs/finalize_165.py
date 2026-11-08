"""Commit this repair while leaving unrelated native edits in the working tree."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-165'
files = list(json.loads((O / 'files.json').read_text('utf8')))
sys.stdout.reconfigure(encoding='utf8', errors='replace')

def git(repo, *args, data=None):
    result = subprocess.run(['git', *args], cwd=repo, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf8', errors='replace'))
    return result.stdout

def stage_blob(name, data):
    blob = git(H, 'hash-object', '-w', '--stdin', data=data).decode().strip()
    git(H, 'update-index', '--cacheinfo', '100644,' + blob + ',' + name)

assert not git(H, 'diff', '--cached', '--name-only').strip()
assert not git(R, 'diff', '--cached', '--name-only').strip()
assert 'PASS   : TestPluginHost::scoreVideoWorkspace164()' in (O / 'startup-workspace.txt').read_text('utf8', errors='replace')
checked = json.loads((O / 'program-checks.json').read_text('utf8'))
assert hashlib.sha256((H / 'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe').read_bytes()).hexdigest() == checked['sha256']

for name in files:
    source = N / name
    if source.suffix.lower() != '.png':
        raw = source.read_bytes()
        source.write_bytes(raw.replace(b'\r\n', b'\n'))
    if name != 'personal/USER_GUIDE.md':
        assert (H / name).read_bytes() == source.read_bytes(), name
git(H, 'add', '--', *[name for name in files if name != 'personal/USER_GUIDE.md'])
stage_blob('personal/USER_GUIDE.md', (N / 'personal/USER_GUIDE.md').read_bytes())
original_agents = git(H, 'show', 'HEAD:AGENTS.md').decode('utf8')
section = (O / 'agents-section.md').read_text('utf8')
assert '## 先理解用途，再设计和实现（2026-11-08）' not in original_agents
title = '# 个人分支开发入口\n\n'
assert original_agents.startswith(title)
stage_blob('AGENTS.md', original_agents.replace(title, title + section, 1).encode('utf8'))
assert set(git(H, 'diff', '--cached', '--name-only').decode().splitlines()) == set(files + ['AGENTS.md'])
git(H, 'diff', '--cached', '--check')
print(git(H, 'diff', '--cached', '--stat').decode('utf8', errors='replace'))
print(git(H, 'commit', '-m', 'Fix 0.165 score video startup actions and legacy workspace entry').decode('utf8', errors='replace'))
git(H, 'tag', 'personal-v0.165.0')
native_commit = git(H, 'rev-parse', 'HEAD').decode().strip()

for name in files:
    assert git(H, 'show', 'HEAD:' + name) == (N / name).read_bytes(), name
helpers = ['reflect_165.py', 'prepare_165.py', 'sync_165.py', 'build_165.py', 'stage_165_review.py', 'refine_165.py', 'check_165_workspace.py', 'document_165.py', 'finish_165_docs.py', 'record_165_review.py', 'finalize_165.py', 'install_165.py']
paths = ['AGENTS.md'] + ['P2/native/' + name for name in files] + ['Repairs/' + name for name in helpers] + ['Planning/ROUND_165_REVIEW.md', 'Planning/SCORE_VIDEO_165_REWORK.md', 'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
git(R, 'add', '--', *paths)
git(R, 'diff', '--cached', '--check')
print(git(R, 'commit', '-m', 'Review N1-N9 workflows and repair published score video entry').decode('utf8', errors='replace'))
(O / 'commits.json').write_text(json.dumps({'native': native_commit, 'plugins': git(R, 'rev-parse', 'HEAD').decode().strip()}, indent=2), encoding='utf8')
