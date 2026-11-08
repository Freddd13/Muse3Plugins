"""Record the actual installation, then republish the committed guide."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
O = R / 'P2/out/repair-165'
N = R / 'P2/native'
sys.stdout.reconfigure(encoding='utf8', errors='replace')
record = json.loads((O / 'installation.json').read_text('utf8'))
names = ['personal/CHANGELOG.md', 'personal/docs/REWORK_PROGRESS.md', 'personal/docs/ROUND_165_REVIEW.md']
details = '0.165.0已更新原安装目录，个人配置保留。实施提交`' + record['sourceCommit'] + '`，主程序SHA-256为`' + record['sha256'] + '`。随包说明与截图已更新。'
for name in names:
    p = N / name
    text = p.read_text('utf8')
    if name.endswith('CHANGELOG.md'):
        anchor = '发布定位personal-v0.165.0。'
        text = text.replace(anchor, anchor + '\n- ' + details, 1)
    elif name.endswith('REWORK_PROGRESS.md'):
        anchor = '## 2026-11-08：0.165入口返工与整轮重新审视\n'
        text = text.replace(anchor, anchor + '\n' + details + '\n', 1)
    else:
        text = text.replace('本次发布定位：`personal-v0.165.0`。安装与提交信息在发布后补入更新日志。', '本次发布定位：`personal-v0.165.0`。' + details, 1)
    p.write_text(text, encoding='utf8', newline='\n')
    (H / name).write_text(text, encoding='utf8', newline='\n')
subprocess.run(['git', 'add', '--', *names], cwd=H, check=True)
subprocess.run(['git', 'commit', '-m', 'Record 0.165 installation and complete workflow review'], cwd=H, check=True)
subprocess.run(['git', 'add', '--', *['P2/native/' + name for name in names], 'Repairs/record_165_install.py'], cwd=R, check=True)
subprocess.run(['git', 'commit', '-m', 'Record installed 0.165 repair and published instructions'], cwd=R, check=True)
spec = importlib.util.spec_from_file_location('release165', R / 'P2/package_stable_release.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
print(publisher.export_committed_guide(H / 'msvc.install_repair_current_x64'))
