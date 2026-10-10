# -*- coding: utf-8 -*-
"""Archive exact committed native changes and verified runtime; retain all history."""
from pathlib import Path
import subprocess,hashlib,json,zipfile,shutil
base=Path(__file__).resolve().parents[1];repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def git(*args):return subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo)]+list(args))
commit=git('rev-parse','HEAD').decode().strip();parent=git('rev-parse','HEAD^').decode().strip()
assert commit=='4c04ca7116d7204493fb2a33b71214d108fb63c1'
assert parent=='3dc1d38c837875befe292c7a73f4eecd82dd03cb'
def write(p,s):p.write_bytes((s.rstrip()+'\n').encode('utf-8'))
names=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp',
 'mtest/mscore/scoreobserver/tst_scoreobserver.cpp','mtest/mscore/scoreobserver/high-treble.mscx',
 'personal/VERSION','personal/CHANGELOG.md','personal/USER_GUIDE.md','personal/docs/04-feature-map.md',
 'personal/docs/10-score-observer.md','personal/docs/README.md','personal/docs/source-map.tsv']
for name in names:
    target=base/'native/v0.22.0'/name;target.parent.mkdir(parents=True,exist_ok=True)
    assert not target.exists();target.write_bytes(git('show','HEAD:'+name))
patch=base/'native/score-observer-0.22.0.patch'
assert not patch.exists();patch.write_bytes(git('format-patch','-1','HEAD','--stdout'))
p=base/'native/RELEASES.md';s=p.read_text(encoding='utf-8')
entry='''## 1.5.0 / 原生 0.22.0

当前插件 **1.5.0**，个人主程序 **0.22.0**，原生提交 `COMMIT`，父提交 `PARENT`，标签 `personal-v0.22.0`。

- 继承最新 0.21.0 与后续字体说明，不回退其他个人功能。原生生产改动仅两处：notepreview.h 的纯几何空位搜索与 ScoreObserver 的屏幕布局／待排字段；音乐逻辑仍在插件，不改音频或谱面模型。
- `score-observer-0.22.0.patch` 是相对上述父提交的增量；本机已包含，勿重复应用。其他机器优先检出版本标签。`v0.22.0/` 是实际 commit 的源码／测试／文档快照，未包含其他任务的未提交说明。
- 新程序 `msvc.install_harmony_1_5_x64/bin/MuseScore3Evo.exe`；启用副本旧文件逐个 `.pre-1.5.0.bak`，编辑源旧版本在 `../backups/1.4.0/`；所有历史文件／旧程序保留。
- `../dist/HarmonyAssistant-1.5.0.zip` 含 20 个 QML/JS 与 README，manifest 记录每文件、ZIP、EXE、patch SHA256，四份运行副本一致。观察器 17／真实宿主 12 项全部通过；明暗真实控件、列表定位、固定／双面板及 JS 检查通过，正式安装连续两次恢复样式和人工区间。小量日志及目视截图在 `../tests/native-*-1-5/`。
- 新记号按实际障碍边界上移且保持 x；页面确实没有安全空间时「记号」列表明确待排。同一和弦默认只标起点，原谱优先开关保留。首批分析／避让有成本，播放沿用缓存；真实声卡长期压力未验收，不承诺零开销。
- 本目录 `_1_5.py` 及 baseline-1.5 是一次性任务记录，不要当作可重复迁移工具；最终源以根目录 runtime 与原生标签为准。用户／并行的 AGENTS 和 USER_GUIDE 未提交增量保留在软件工作区。

'''.replace('COMMIT',commit).replace('PARENT',parent)
assert '## 1.5.0 /' not in s
write(p,s.replace('## 1.4.0 / 原生 0.8.0',entry+'## 历史 1.4.0 / 原生 0.8.0',1).replace('当前插件 **1.4.0**','历史插件 **1.4.0**',1))
runtime=sorted(p for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md')
assert len(runtime)==21
installed=repo/'msvc.install_harmony_1_5_x64';enabled=Path('C:/Users/Fred/Documents/MuseScore3/插件/HarmonyAssistant')
for p in runtime:
    for folder in (repo/'share/plugins/HarmonyAssistant',installed/'plugins/HarmonyAssistant',enabled):
        assert p.read_bytes()==(folder/p.name).read_bytes(),str(folder/p.name)
archive=base/'dist/HarmonyAssistant-1.5.0.zip';assert not archive.exists()
with zipfile.ZipFile(str(archive),'w',zipfile.ZIP_DEFLATED) as output:
    for p in runtime:output.write(str(p),'HarmonyAssistant/'+p.name)
with zipfile.ZipFile(str(archive)) as output:
    assert output.testzip() is None
    for p in runtime:assert output.read('HarmonyAssistant/'+p.name)==p.read_bytes()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exe=installed/'bin/MuseScore3Evo.exe'
assert sha(exe)==sha(repo/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe')
manifest={'pluginVersion':'1.5.0','personalVersion':'0.22.0','nativeCommit':commit,'nativeParent':parent,'pluginTag':'harmony-v1.5.0',
 'files':{p.name:sha(p) for p in runtime},archive.name:sha(archive),'nativePatchSHA256':sha(patch),'MuseScore3Evo.exe':sha(exe),'executable':str(exe),
 'checks':{'scoreobserver':17,'pluginhost':12,'failed':0,'skipped':0,'restarts':2,'persistedCorrection':'Am/C','lightDarkPointerControls':True,'completeListClick':True,'fourCopiesIdentical':True},
 'knownLimits':['Finite page space can still require pending markers.','No real audio device long-session test.','Existing Qt warnings and three pre-existing external guide links remain.']}
write(base/'dist/release-1.5.0.json',json.dumps(manifest,ensure_ascii=False,indent=2))
shutil.copy2(str(base/'dist/release-1.5.0.json'),str(installed/'validation/release-1.5.0.json'))
print('Packaged 1.5.0 / 0.22.0; ZIP content and four runtime copies verified; history retained')
