"""Record the installed release, publish its guide and push the scoped commits."""
from pathlib import Path
import importlib.util
import json
import subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-166'
installed = json.loads((O/'installation.json').read_text('utf8'))
assert installed['version'] == '0.166.0'
message = ('0.166.0已更新原安装目录，个人配置保留。实施提交`' + installed['sourceCommit']
           + '`，程序SHA-256为`' + installed['sha256'] + '`。随包操作说明已更新。')
names = ['personal/docs/ROUND_166_REVIEW.md', 'personal/docs/REWORK_PROGRESS.md', 'personal/CHANGELOG.md']
for base in (N, H):
    for name in names:
        p = base/name
        text = p.read_text('utf8')
        if name.endswith('ROUND_166_REVIEW.md'):
            text = text.replace('编译、安装与提交信息完成后记入本页和更新日志。', message, 1)
        elif name.endswith('REWORK_PROGRESS.md'):
            text = text.replace('当前正在编译与准备发布。', message, 1)
        else:
            text = text.replace('安装与提交信息随后补入。', message, 1)
        p.write_text(text, encoding='utf8', newline='\n')
p = R/'Planning/ROUND_166_REVIEW.md'
p.write_text(p.read_text('utf8')+'\n'+message+'\n', encoding='utf8', newline='\n')
for repo, paths, title in [
    (H, names, 'Document installed 0.166 score fidelity repair and complete review'),
    (R, ['P2/native/'+name for name in names]+['Planning/ROUND_166_REVIEW.md',
         'Repairs/install_166.py', 'Repairs/publish_166.py'], 'Record 0.166 installation and updated user instructions')]:
    assert not subprocess.check_output(['git','diff','--cached','--name-only'], cwd=repo).strip()
    subprocess.run(['git','add','--',*paths], cwd=repo, check=True)
    subprocess.run(['git','diff','--cached','--check'], cwd=repo, check=True)
    subprocess.run(['git','commit','-m',title], cwd=repo, check=True)
spec = importlib.util.spec_from_file_location('release166', R/'P2/package_stable_release.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
print('Installed guide:', publisher.export_committed_guide(H/'msvc.install_repair_current_x64'))
for repo in (H, R):
    subprocess.run(['git','push','origin','HEAD'], cwd=repo, check=True)
subprocess.run(['git','push','origin','personal-v0.166.0'], cwd=H, check=True)
print('0.166 installed, recorded and pushed.')
