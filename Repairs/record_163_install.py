from pathlib import Path
import hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';N=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-163'
record=json.loads((OUT/'installation.json').read_text('utf8'));assert hashlib.sha256(Path(record['program']).read_bytes()).hexdigest()==record['sha256']
commit=record['sourceCommit'];count=record['guide']['documents']
updates={'personal/docs/REWORK_PROGRESS.md':('正在更新程序目录。',f'0.163.0已安装到原程序目录，{count}份随包说明已更新。'),
'personal/docs/REFERENCE_CONTROLS_163_CHECKS.md':('当前准备更新原安装目录。',f'0.163.0已更新原程序目录、原曲页面、媒体组件及{count}份说明，个人配置保持。实施提交{commit}。'),
'personal/CHANGELOG.md':('发布定位personal-v0.163.0。',f'发布定位personal-v0.163.0；实施提交{commit}，已安装并更新{count}份说明。')}
for name,(old,new) in updates.items():
    path=N/name;raw=path.read_bytes();assert (HOST/name).read_bytes()==raw;text=raw.decode('utf8');assert old in text;data=text.replace(old,new,1).encode('utf8');path.write_bytes(data);(HOST/name).write_bytes(data)
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('0.163分体播放、实际范围、移位显隐及撤销保存已检查，正在更新程序目录','0.163分体播放、实际范围、移位显隐及撤销保存已检查并安装',1);plan.write_bytes(text.encode('utf8'))
subprocess.run(['git','add','--',*updates],cwd=HOST,check=True);subprocess.run(['git','commit','-m','Record installed 0.163 reference controls and continue score video'],cwd=HOST,check=True)
subprocess.run(['git','add','--',*['P2/native/'+name for name in updates],'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','Repairs/record_163_install.py'],cwd=ROOT,check=True);subprocess.run(['git','commit','-m','Record installed N7 and dynamic score video next'],cwd=ROOT,check=True)
spec=importlib.util.spec_from_file_location('publish163',ROOT/'P2/package_stable_release.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher);print(publisher.export_committed_guide(HOST/'msvc.install_repair_current_x64'))
