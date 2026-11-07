from pathlib import Path
import hashlib,importlib.util,json,subprocess
R=Path(__file__).resolve().parents[1];H=R.parent/'muse3_dev/MuseScore';N=R/'P2/native';O=R/'P2/out/repair-164'
record=json.loads((O/'installation.json').read_text('utf8'));assert hashlib.sha256(Path(record['program']).read_bytes()).hexdigest()==record['sha256']
commit=record['sourceCommit'];count=record['guide']['documents']
updates={'personal/docs/REWORK_PROGRESS.md':('正在更新程序目录。',f'0.164.0已安装到原程序目录，{count}份随包说明已更新。'),
'personal/docs/SCORE_VIDEO_164_CHECKS.md':('当前准备更新原安装目录。',f'0.164.0已更新原程序目录、媒体组件、视频编码工具及{count}份说明，个人配置保持。实施提交{commit}。'),
'personal/CHANGELOG.md':('发布定位personal-v0.164.0。',f'发布定位personal-v0.164.0；实施提交{commit}，已安装并更新{count}份说明。')}
for name,(old,new) in updates.items():
    path=N/name;raw=path.read_bytes();assert (H/name).read_bytes()==raw;data=raw.decode('utf8');assert old in data;data=data.replace(old,new,1).encode('utf8');path.write_bytes(data);(H/name).write_bytes(data)
p=R/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';t=p.read_text('utf8').replace('0.164原生谱表、声音、预览、换行、保存及两种容器已检查，正在更新程序目录','0.164原生谱表、声音、预览、换行、保存及两种容器已检查并安装',1);p.write_bytes(t.encode('utf8'))
p=R/'Planning/SCORE_VIDEO_164_DESIGN.md';t=p.read_text('utf8').replace('当前准备安装0.164','0.164已安装到原程序目录');p.write_bytes(t.encode('utf8'))
subprocess.run(['git','add','--',*updates],cwd=H,check=True);subprocess.run(['git','commit','-m','Record installed 0.164 score video and completed N1 N9 delivery'],cwd=H,check=True)
subprocess.run(['git','add','--',*['P2/native/'+name for name in updates],'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','Planning/SCORE_VIDEO_164_DESIGN.md','Repairs/record_164_install.py'],cwd=R,check=True);subprocess.run(['git','commit','-m','Record installed N8 and the full round delivery status'],cwd=R,check=True)
spec=importlib.util.spec_from_file_location('publish164',R/'P2/package_stable_release.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher);print(publisher.export_committed_guide(H/'msvc.install_repair_current_x64'))
