from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(path,text):
 p=R/'native'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode())
stage('personal/VERSION','0.53.0\n')
s=(H/'personal/USER_GUIDE.md').read_text(encoding='utf8').replace('当前个人版本：**0.52.0**','当前个人版本：**0.53.0**')
anchor='## 打开功能'
s=s.replace(anchor,'## 0.53 的操作修复\n\n插件管理器的“重载插件”会重新读取插件并恢复打开的面板，保留启用状态和快捷键。录制或拖动结束后继续重载。原曲关联在选音、缩放和重新排版后继续有效；小节或拍号变化后，在关联行修改范围。完整操作见[0.53 说明](docs/REPAIR_053_GUIDE.md)。\n\n'+anchor,1)
stage('personal/USER_GUIDE.md',s)
s=(H/'personal/CHANGELOG.md').read_text(encoding='utf8');s=s.replace('# 个人版本更新日志','# 个人版本更新日志\n\n## 0.53.0 — 2026-10-17\n\n- 复现并修复插件面板打开时重载崩溃；扫描插件信息与运行面板分开使用引擎，关闭时按窗口所有权释放。重载恢复打开的面板，保留启用状态和快捷键。\n- 列表重建期间暂停列表回调，录制与拖动完成后执行等待中的重载。\n- 原曲关联按小节与拍号变化更新，普通播放、选择和排版刷新保持关联。底部面板的紧凑显示由停靠位置决定。\n- 操作和检查：personal/docs/REPAIR_053_GUIDE.md；提交定位：personal-v0.53.0。',1);stage('personal/CHANGELOG.md',s)
stage('personal/docs/REPAIR_053_GUIDE.md',(R/'docs/REPAIR_053_GUIDE.md').read_text(encoding='utf8'))
s=(H/'personal/docs/source-map.tsv').read_text(encoding='utf8');s+='插件重载\tmscore/plugin/pluginManager.cpp\tvoid PluginManager::reloadPluginsClicked()\t366\t保存并恢复打开的插件面板\treloadActiveWorkflowPanels\n原曲结构\tmscore/workflow/referenceworkflow.cpp\tQString ScoreObserver::referenceStructureKey() const\t22\t关联所需的小节拍号信息\trealPanelMouseActions\n';stage('personal/docs/source-map.tsv',s)
print('0.53 guide and version staged')
