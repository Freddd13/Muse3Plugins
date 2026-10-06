# -*- coding: utf-8 -*-
"""Record the committed 0.4 increment and hashes without replacing older releases."""
from pathlib import Path
import hashlib,json,shutil,subprocess
base=Path(__file__).resolve().parents[1]
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
git=r'E:\Git\cmd\git.exe'
commit=subprocess.check_output([git,'-C',str(repo),'rev-parse','personal-v0.4.0']).decode('ascii').strip()
patch=subprocess.check_output([git,'-C',str(repo),'format-patch','-1','--stdout',commit])
(base/'native/score-observer-0.4.0.patch').write_bytes(patch)
paths=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mscore/plugin/api/scoreobserver.h',
       'mscore/plugin/qmlplugin.cpp','mscore/plugin/qmlplugin.h','mscore/events.cpp','mscore/scoreview.cpp','mscore/scoreview.h',
       'mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp',
       'mtest/mscore/scoreobserver/test-exchange.cjs','mtest/mscore/scoreobserver/smoke.qml','personal/tools/test_harmony_gui.py']
for path in paths:
    target=base/'native/v0.4.0'/path;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(str(repo/path),str(target))
names=['HarmonyAssistant_MS3.qml','Harmony.js','Preferences.js','Analysis.js','ConfigurationEditor.qml',
       'SettingsStore.qml','PanelCard.qml','UiLabel.qml','StableLabel.qml','ColorOption.qml','AppearanceEditor.qml','README.md']
locations={'source':base,'repository':repo/'share/plugins/HarmonyAssistant',
           'installed':repo/'msvc.install_harmony_1_2_x64/plugins/HarmonyAssistant',
           'enabledUserCopy':Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')}
manifest={'pluginVersion':'1.2.0','personalVersion':'0.4.0','commit':commit,
          'parent':'a818d9a7009306a721363b17a2aab4ee3178ab09','files':{}}
for name in names:
    hashes={k:hashlib.sha256((p/name).read_bytes()).hexdigest() for k,p in locations.items()}
    assert len(set(hashes.values()))==1,name
    manifest['files'][name]=hashes['source']
for path in [base/'dist/HarmonyAssistant-1.2.0.zip',repo/'msvc.install_harmony_1_2_x64/bin/MuseScore3Evo.exe']:
    manifest[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(base/'dist/release-1.2.0.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
images=base/'tests/native-gui-1-2';images.mkdir(parents=True,exist_ok=True)
for name in ['ribbon.png','floating-panel.png','score-fixed-label.png','gui.txt','gui-production-qt.txt']:
    shutil.copy2(str(repo/'msvc.build_harmony_release_x64/harmony-gui-1-2'/name),str(images/name))
p=base/'native/RELEASES.md';s=p.read_text(encoding='utf-8')
section='''## 1.2.0 / 原生 0.4.0

当前插件 **1.2.0**，个人主程序 **0.4.0**，标签 `personal-v0.4.0`，提交 `COMMIT`。

- `score-observer-0.4.0.patch` 是父提交 `a818d9a7009306a721363b17a2aab4ee3178ab09` 之后的完整增量。只能在已经含 0.3.0 的合适基线上应用；本机已包含，勿重复应用。
- `v0.4.0/` 保留提交后的原生接口与回归快照。固定记号、高亮索引和双击为通用宿主接口；和声/UI/离调规则仍在插件。
- 新程序 `msvc.install_harmony_1_2_x64/bin/MuseScore3Evo.exe`；启用目录旧文件备份 `.pre-1.2.0.bak`，旧安装和所有历史文件保留。
- `../dist/release-1.2.0.json` 记录十二个发布文件、程序/ZIP 哈希；编辑源、主仓库、独立安装、已启用副本四份已核对。
- 测试与可复现日志见主仓库 `personal/CHANGELOG.md` 的 0.4.0，以及插件 `tests/native-gui-1-2/`、`tests/native-smoke-installed-1-2/`。实际硬件音频和长会话未验收。

## 历史 1.1.0 / 原生 0.3.0

'''.replace('COMMIT',commit)
assert '## 1.2.0' not in s
s=s.replace('当前插件为 **1.1.0**',section+'历史插件为 **1.1.0**',1)
with p.open('w',encoding='utf-8',newline='\n') as stream:stream.write(s)
print(json.dumps({'commit':commit,'patchBytes':len(patch),'matchingRuntimeCopies':4}))
