from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
record=json.loads((OUT/'installation.json').read_text('utf8'))
assert hashlib.sha256(Path(record['program']).read_bytes()).hexdigest()==record['sha256']
updates={
'personal/docs/REWORK_PROGRESS.md':('正在更新程序目录。','0.161.0已安装到原程序目录，246份随包说明已更新。'),
'personal/docs/PERFORMANCE_TIMING_161_CHECKS.md':('当前准备更新原安装目录，安装结果随后记入本页。','0.161.0已更新原程序目录及246份说明，个人配置保持；实施提交f52909cc70bb913d0dd6cdf4f35988db9d0e6174。'),
'personal/CHANGELOG.md':('发布定位personal-v0.161.0。','发布定位personal-v0.161.0；实施提交f52909cc70bb913d0dd6cdf4f35988db9d0e6174，已安装并更新246份说明。')}
for name,(old,new) in updates.items():
    path=NATIVE/name;original=path.read_bytes()
    if (HOST/name).read_bytes()!=original:raise ValueError('Separate edit '+name)
    text=original.decode('utf8')
    if old not in text:raise ValueError('Expected '+name)
    data=text.replace(old,new,1).encode('utf8');path.write_bytes(data);(HOST/name).write_bytes(data)
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('0.161谱面轨实际起止、恢复、保存与撤销已检查','0.161谱面轨实际起止、恢复、保存与撤销已检查并安装',1);plan.write_bytes(text.encode('utf8'))
subprocess.run(['git','add','--',*updates],cwd=HOST,check=True)
subprocess.run(['git','commit','-m','Record installed 0.161 performance timing and continue N6'],cwd=HOST,check=True)
paths=['P2/native/'+name for name in updates]+['Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','Repairs/record_161_install.py']
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','Record installed 0.161 and frequency work next'],cwd=ROOT,check=True)
