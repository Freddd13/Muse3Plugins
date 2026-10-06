# -*- coding: utf-8 -*-
"""Archive the verified release without deleting previous versions."""
from pathlib import Path
import subprocess,shutil,hashlib,json,zipfile
base=Path(__file__).resolve().parents[1]
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
commit=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'rev-parse','HEAD']).decode().strip()
assert commit=='77cced440634309690e44962d8b76df4f981d75a'
parent=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'rev-parse','HEAD^']).decode().strip()
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as out:out.write(text)
files=['mscore/events.cpp','mscore/notepreview.h','mscore/scoreview.cpp','mscore/plugin/api/scoreobserver.cpp','mscore/plugin/api/scoreobserver.h',
    'mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp','mtest/mscore/scoreobserver/smoke.qml',
    'personal/VERSION','personal/CHANGELOG.md','personal/docs/10-score-observer.md']
for name in files:
    dest=base/'native/v0.8.0'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(str(repo/name),str(dest))
patch=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'format-patch','-1','HEAD','--stdout'])
(base/'native/score-observer-0.8.0.patch').write_bytes(patch)
for source,name in [('harmony-gui-1-4-final','native-gui-1-4'),('harmony-observer-1-4-final','native-observer-1-4'),('harmony-note-1-4-final','native-note-1-4'),('harmony-smoke-installed-1-4','native-smoke-installed-1-4')]:
    dest=base/'tests'/name;dest.mkdir(exist_ok=True)
    for p in (repo/'msvc.build_personal_0_6_x64'/source).iterdir():
        if p.is_file() and p.suffix in ('.png','.txt','.json','.log'):shutil.copy2(str(p),str(dest/p.name))
empty=base/'tests/range-drag-log.txt'
if empty.exists():
    dest=base/'native/next-1.4/range-drag-attempt.txt';assert not dest.exists();shutil.move(str(empty),str(dest))
p=base/'native/RELEASES.md';s=p.read_text(encoding='utf-8')
entry='''## 1.4.0 / 原生 0.8.0

当前插件 **1.4.0**，个人主程序 **0.8.0**，标签 `personal-v0.8.0`，提交 `COMMIT`，父提交 `PARENT`。

- `score-observer-0.8.0.patch` 是已含 0.7.1 的本次增量，本机已包含，勿重复应用；其他机器优先检出标签。只修改五个原生生产文件，音乐/人工区间仍在插件。
- `v0.8.0/` 是最终提交的宿主/回归/日志快照。`next-1.4/` 与本目录 `_1_4.py` 为一次性开发中间记录，可能未含后续修正，不能用来覆盖软件；最终运行源在插件根目录和仓库 share/plugins。
- 新程序 `msvc.install_harmony_1_4_x64/bin/MuseScore3Evo.exe`；启用副本逐文件 `.pre-1.4.0.bak`，插件旧源在 `../backups/1.3.0/`，所有历史程序/源/包保留。
- `../dist/release-1.4.0.json` 记录十四个文件与 exe/ZIP 哈希，四份运行源一致。原生 16、宿主 10、既有音符 11 项全部通过；日志在 `tests/native-*-1-4/`，范围拖动和纯 JS 在同目录测试脚本。真实安装连续启动恢复人工区间和样式。
- 范围模型按指纹保存，编辑谱面后需复核；六条避让行仍可能省略。初始分析/绘制非零成本，硬件音频与用户实谱长期使用尚需验收。

'''.replace('COMMIT',commit).replace('PARENT',parent)
s=s.replace('## 1.3.0 / 原生 0.5.0',entry+'## 历史 1.3.0 / 原生 0.5.0',1).replace('当前插件 **1.3.0**','历史插件 **1.3.0**',1);write(p,s)
runtime=sorted(p for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md')
assert len(runtime)==14
archive=base/'dist/HarmonyAssistant-1.4.0.zip'
assert not archive.exists()
with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as z:
    for p in runtime:z.write(str(p),'HarmonyAssistant/'+p.name)
with zipfile.ZipFile(str(archive)) as z:
    assert z.testzip() is None
    for p in runtime:assert z.read('HarmonyAssistant/'+p.name)==p.read_bytes()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest={'pluginVersion':'1.4.0','personalVersion':'0.8.0','commit':commit,'parent':parent,'files':{p.name:sha(p) for p in runtime},archive.name:sha(archive),
    'MuseScore3Evo.exe':sha(repo/'msvc.install_harmony_1_4_x64/bin/MuseScore3Evo.exe'),
    'executable':str(repo/'msvc.install_harmony_1_4_x64/bin/MuseScore3Evo.exe'),
    'tests':{'scoreobserver':16,'pluginhost':10,'note':11,'failed':0,'skipped':0,'restartPersistence':True,'rangePointerDrag':True}}
write(base/'dist/release-1.4.0.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Packaged release 1.4.0 / 0.8.0, ZIP verified, history retained')
