"""Record the installed repair and publish the scoped commits."""
from pathlib import Path
import importlib.util
import json
import subprocess

R=Path(__file__).resolve().parents[1]
H=R.parent/'muse3_dev/MuseScore'
N=R/'P2/native'
O=R/'P2/out/usability-167'
installed=json.loads((O/'installation.json').read_text('utf8'))
assert installed['version']=='0.167.0'
message=('0.167.0已更新原安装目录，个人配置保留。实施提交`'+installed['nativeCommit']
    +'`；程序SHA-256为`'+installed['sha256']+'`。累计功能说明与本轮完整检查已随程序更新。')
names=['personal/docs/CURRENT_FEATURE_CHECK_167.md','personal/docs/REWORK_PROGRESS.md','personal/CHANGELOG.md']
for base in (N,H):
    for name in names:
        p=base/name
        text=p.read_text('utf8').replace('安装和提交信息随发布补入本页。',message,1)
        text=text.replace('安装与提交信息随后补入。',message,1)
        p.write_text(text,encoding='utf8',newline='\n')
(R/'Planning/CURRENT_FEATURE_CHECK_167.md').write_text((N/names[0]).read_text('utf8'),encoding='utf8',newline='\n')
for repo,paths,title in [(H,names,'Record installed 0.167 workflow repair and full feature inspection'),
    (R,['P2/native/'+name for name in names]+['Planning/CURRENT_FEATURE_CHECK_167.md'],
     'Record 0.167 installation and cumulative workflow results')]:
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo).strip()
    subprocess.run(['git','add','--',*paths],cwd=repo,check=True)
    subprocess.run(['git','diff','--cached','--check'],cwd=repo,check=True)
    subprocess.run(['git','commit','-m',title],cwd=repo,check=True)
spec=importlib.util.spec_from_file_location('release167',R/'P2/package_stable_release.py')
publisher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)
print('Updated installed guide:',publisher.export_committed_guide(H/'msvc.install_repair_current_x64'))
for repo in (H,R):subprocess.run(['git','push','origin','HEAD'],cwd=repo,check=True)
subprocess.run(['git','push','origin','personal-v0.167.0'],cwd=H,check=True)
print(message)
