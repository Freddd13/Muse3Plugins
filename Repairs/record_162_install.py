from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162'
record=json.loads((OUT/'installation.json').read_text('utf8'));assert hashlib.sha256(Path(record['program']).read_bytes()).hexdigest()==record['sha256']
commit=record['sourceCommit'];count=record['guide']['documents']
updates={'personal/docs/REWORK_PROGRESS.md':('正在更新程序目录。',f'0.162.0已安装到原程序目录，{count}份随包说明已更新。'),
'personal/docs/SPECTRUM_162_CHECKS.md':('当前准备编译发布程序并更新原安装目录。',f'0.162.0已更新原程序目录、媒体组件及{count}份说明；普通MIDI与0.161一致，PDF正常，个人配置保留。实施提交{commit}。'),
'personal/CHANGELOG.md':('发布定位personal-v0.162.0。',f'发布定位personal-v0.162.0；实施提交{commit}，已安装并更新{count}份说明。')}
for name,(old,new) in updates.items():
    file=NATIVE/name;raw=file.read_bytes();assert (HOST/name).read_bytes()==raw
    text=raw.decode('utf8');assert old in text;data=text.replace(old,new,1).encode('utf8');file.write_bytes(data);(HOST/name).write_bytes(data)
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('0.162已检查整轨准备、三格式长音频、琴键／倍频、设置与MIDI对照，正在更新程序目录','0.162已检查并安装：整轨准备、三格式长音频、琴键／倍频、设置与MIDI对照',1);plan.write_bytes(text.encode('utf8'))
subprocess.run(['git','add','--',*updates],cwd=HOST,check=True);subprocess.run(['git','commit','-m','Record installed 0.162 spectrum and next association controls'],cwd=HOST,check=True)
subprocess.run(['git','add','--',*['P2/native/'+name for name in updates],'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','Repairs/record_162_install.py'],cwd=ROOT,check=True);subprocess.run(['git','commit','-m','Record installed N6 and continue N7 association controls'],cwd=ROOT,check=True)
