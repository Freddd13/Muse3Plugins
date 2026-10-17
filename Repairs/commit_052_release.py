"""Commit the verified batch to both repositories and publish personal-v0.52.0."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / 'Repairs'
HOST = ROOT.parent / 'muse3_dev/MuseScore'
BUILD = HOST / 'msvc.build_harmony_release_x64'

def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo).decode('utf8').strip()

for name, count in [('p1native', 49), ('performanceeditor', 62), ('p0native', 23)]:
    path = R / f'out/repair-052-final-{name}/gui.txt'
    assert f'Totals: {count} passed, 0 failed' in path.read_text(encoding='utf8', errors='replace')
    assert path.stat().st_mtime >= (BUILD / f'mtest/mscore/{name}/Release/tst_{name}.exe').stat().st_mtime
for repo in [HOST, ROOT]:
    assert not git(repo, 'diff', '--cached', '--name-only'), '暂存区已有内容，请先检查。'
    git(repo, 'fetch', 'origin')
    upstream = git(repo, 'rev-parse', '--abbrev-ref', '@{upstream}')
    assert git(repo, 'rev-list', '--count', 'HEAD..' + upstream) == '0', '远端有新提交，先合并。'

paths = set(git(HOST, 'diff', '--name-only').splitlines() + git(HOST, 'ls-files', '--others', '--exclude-standard').splitlines())
paths.discard('AGENTS.md')
assert all((R / 'native' / p).is_file() or p.startswith('personal/') or p == 'mscore/CMakeLists.txt' for p in paths), paths
git(HOST, 'add', '--', *sorted(paths))
git(HOST, 'diff', '--cached', '--check')
print(git(HOST, 'commit', '-m', 'Add regional writing comparison and editable MIDI release preview'), flush=True)
git(HOST, 'tag', 'personal-v0.52.0')
native = git(HOST, 'rev-parse', '--short=9', 'HEAD')

path = ROOT / 'Planning/REPAIR_2026_10_SECOND_PASS.md'
text = path.read_text(encoding='utf8')
text += f'\n第五批提交：{native}，personal-v0.52.0。安装：msvc.install_repair_0_52_x64。全部五批已完成，操作说明、截图和各项问题答复随0.52保存。\n'
path.write_text(text, encoding='utf8', newline='\n')
paths = set(git(ROOT, 'diff', '--name-only').splitlines() + git(ROOT, 'ls-files', '--others', '--exclude-standard').splitlines())
paths.discard('p0-test-results.txt')
assert all(p.startswith(('Repairs/', 'Planning/')) for p in paths), paths
git(ROOT, 'add', '--', *sorted(paths))
git(ROOT, 'diff', '--cached', '--check')
print(git(ROOT, 'commit', '-m', 'Finish writing and MIDI comparisons with complete operation guides'), flush=True)
git(HOST, 'push', 'origin', '3.x')
git(HOST, 'push', 'origin', 'personal-v0.52.0')
git(ROOT, 'push', 'origin', 'main')
print('Native ' + native + '; plugins ' + git(ROOT, 'rev-parse', '--short=9', 'HEAD'), flush=True)
