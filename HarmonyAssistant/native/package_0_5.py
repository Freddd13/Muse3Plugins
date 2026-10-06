# -*- coding: utf-8 -*-
"""Record committed increment and release hashes; preserve all previous releases."""
from pathlib import Path
import hashlib,json,shutil,subprocess
base=Path(__file__).resolve().parents[1]
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
git=r'E:\Git\cmd\git.exe'
commit=subprocess.check_output([git,'-C',str(repo),'rev-parse','personal-v0.5.0']).decode('ascii').strip()
patch=subprocess.check_output([git,'-C',str(repo),'format-patch','-1','--stdout',commit])
(base/'native/score-observer-0.5.0.patch').write_bytes(patch)
paths=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mscore/plugin/api/scoreobserver.h',
       'mscore/plugin/qmlplugin.cpp','mscore/plugin/qmlplugin.h','mscore/editelement.cpp','mscore/scoreview.cpp','mscore/scoreview.h',
       'mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp',
       'mtest/mscore/scoreobserver/test-exchange.cjs','mtest/mscore/scoreobserver/smoke.qml','personal/tools/test_harmony_gui.py']
for path in paths:
    target=base/'native/v0.5.0'/path;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(str(repo/path),str(target))
names=['HarmonyAssistant_MS3.qml','Harmony.js','Preferences.js','Analysis.js','ConfigurationEditor.qml',
       'SettingsStore.qml','PanelCard.qml','UiLabel.qml','StableLabel.qml','ColorOption.qml','AppearanceEditor.qml','README.md']
locations={'source':base,'repository':repo/'share/plugins/HarmonyAssistant',
           'installed':repo/'msvc.install_harmony_1_3_x64/plugins/HarmonyAssistant',
           'enabledUserCopy':Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')}
manifest={'pluginVersion':'1.3.0','personalVersion':'0.5.0','commit':commit,
          'parent':'9a5ae07ec43b3c6aacd53692c199b8f94ced8e75','files':{}}
for name in names:
    hashes={k:hashlib.sha256((p/name).read_bytes()).hexdigest() for k,p in locations.items()}
    assert len(set(hashes.values()))==1,name
    manifest['files'][name]=hashes['source']
for path in [base/'dist/HarmonyAssistant-1.3.0.zip',repo/'msvc.install_harmony_1_3_x64/bin/MuseScore3Evo.exe']:
    manifest[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(base/'dist/release-1.3.0.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
images=base/'tests/native-gui-1-3';images.mkdir(parents=True,exist_ok=True)
for name in ['ribbon.png','floating-panel.png','score-fixed-label.png','dual-details.png','no-onset-change.png','native-editor-priority.png','gui.txt']:
    shutil.copy2(str(repo/'msvc.build_harmony_release_x64/harmony-gui-1-3'/name),str(images/name))
p=base/'native/RELEASES.md';s=p.read_text(encoding='utf-8')
section='''## 1.3.0 / 原生 0.5.0

当前插件 **1.3.0**，个人主程序 **0.5.0**，标签 `personal-v0.5.0`，提交 `COMMIT`。

- `score-observer-0.5.0.patch` 是父提交 `9a5ae07ec43b3c6aacd53692c199b8f94ced8e75` 之后的完整增量；本机已包含，勿重复应用，其他机器需先有 0.4.0。
- `v0.5.0/` 保留接口/回归快照。和声变化标记与音符颜色分离，支持无新音位置；当前标签避开固定记号，原谱和弦/编辑优先；辅助详情宿主接受同一控件树，不复制观察器/分析。
- 新程序 `msvc.install_harmony_1_3_x64/bin/MuseScore3Evo.exe`；启用副本保存 `.pre-1.3.0.bak`，历史程序和文件保留。
- `../dist/release-1.3.0.json` 保存十二个发布文件和 exe/ZIP 哈希，四份运行源码已核对。
- 验证见主仓库 CHANGELOG 0.5.0，插件 `tests/native-gui-1-3/` 与 `tests/native-smoke-installed-1-3/`。硬件音频/长会话未验收；密集标记可省略，无零开销/硬实时承诺。

'''.replace('COMMIT',commit)
assert '## 1.3.0' not in s
s=s.replace('## 1.2.0 / 原生 0.4.0',section+'## 历史 1.2.0 / 原生 0.4.0',1)
s=s.replace('当前插件 **1.2.0**','历史插件 **1.2.0**',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print(json.dumps({'commit':commit,'patchBytes':len(patch),'matchingRuntimeCopies':4}))
