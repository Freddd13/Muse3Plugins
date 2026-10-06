"""Document the additive 0.3.0 observer / overlay / dock contracts."""
from pathlib import Path
R=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def write(name, text):
    with (R/name).open('w',encoding='utf-8',newline='\n') as f:f.write(text)
def amend(name, old, new):
    s=(R/name).read_text(encoding='utf-8');assert old in s,name;write(name,s.replace(old,new,1))
write('personal/VERSION','0.3.0\n')
amend('personal/docs/README.md','个人版本 0.2.0 增加通用播放观察与屏幕临时配色','个人版本 0.3.0 提供通用播放观察、踏板/时序快照、屏幕临时颜色/标注和自适应停靠')
amend('personal/docs/01-architecture.md','详见 [10](10-score-observer.md)。','0.3.0 的 QmlPlugin 暴露停靠位置/悬浮状态；ScoreObserver 扩展踏板/时序快照、分批分析帧、两个屏幕层和原子文本/配置读写。谱面解释、交换格式和颜色规则仍在插件；不扩展音频线程或文件格式。详见 [10](10-score-observer.md)。')
amend('personal/docs/04-feature-map.md','验证为 `mtest/mscore/scoreobserver` 和相邻 `mtest/libmscore/note`。','踏板保持与有限琶音窗口、全谱配色/文字、JSON/CSV 分析交换和配置在插件及通用 API；QmlPlugin 停靠桥接暴露实际位置/悬浮状态。验证为 `mtest/mscore/scoreobserver`、实际 Widgets/QML 宿主 `mtest/mscore/pluginhost` 和相邻 `mtest/libmscore/note`。')
amend('personal/docs/05-piano-development.md','踏板声学残响不纳入当前和弦。','0.3.0 的 contextSnapshot 另提供记谱踏板区间保持音及限小节/休止截断的短时聚合；它模拟踏板状态，不估计声音衰减。即时音列表和推断上下文分开。')
p=R/'personal/docs/10-score-observer.md';s=p.read_text(encoding='utf-8').replace('个人版本 0.2.0','个人版本 0.3.0').replace('除新增四个插件运行文件，没有修改其他插件。','新增运行组件仅属于 HarmonyAssistant，没有修改其他插件。');s += '''
## 0.3.0：上下文、全谱图层、配置与停靠

`contextSnapshot(tick, firstTrack, endTrack, pedal, windowTicks, sounding)` 保留原 snapshot 的 notes，另返回 analysisNotes 与 fingerprint。延音线沿 tie 链延长；踏板 windows 从 Pedal/Spanner 得到，作用于所属乐器全部 track；抬踏板移除已结束音。非踏板窗口最多 1920 ticks，限当前小节、声部休止截断。同音高保留最近定位/拼写，播放真实 NoteEvent 优先。这是记谱状态解释，不是声学衰减或 Synthesia 算法复刻。

`analysisFrames(fromTick, limit, firstTrack, endTrack, pedal, windowTicks)` 按事件起止、踏板端点和小节边界返回最多 128 帧，nextTick=-1 表示结束。插件实际每 12 ms 分批最多 32 帧；播放时不重新分析全谱。fingerprint 是当前范围的数值音符定位/时值/调号与踏板摘要 SHA256，用于阻止导入结果应用到不匹配的谱面。音乐检测继续由 ES5 插件完成，使用预计算十二位掩码模板；新增配置和交换逻辑分别在 Preferences.js、Analysis.js。

`setScorePreview(descriptors)` 提供独立的全谱底层；`setNotePreviewColors` 保留当前层用途并支持 label/chord/active。`clearNotePreviewColors` 仅清当前层，`clearAllPreviews` 清两层；隐藏、停用、换谱、销毁都清全部。文字用 note 为锚点，在 page 空间索引里避让记谱元素与同批标签；和弦位于乐器顶谱表上方。拥挤时省略，不能保证每种特殊排版都能放下所有文字。屏幕标签不修改布局、undo 或保存内容，打印/foto 不显示。GUI 播放高亮用浅蓝底，复用未改变的底层几何，不开启动画 timer。

临时层使用 Element 指针作不透明键；ScoreView::onElementDestruction 必须只比较地址。回调来自 Element 析构，调用 e->isNote()/type() 会触发纯虚函数终止；这是 0.2.0 的崩溃根因，Windows 转储与链接函数映射定位到此调用链。实际插件宿主测试会在 native ScoreView 存在时创建 QML ScoreView、触发 doLayout，再弹出菜单、加载插件、顶部/侧边/悬浮切换和反复关闭。

QmlPlugin::attachPanelDock 只持有已有 QDockWidget 的 QPointer；panelPlacement/panelFloating 和 setPanelFloating 供插件自适应。可选 QML preferredRibbonHeight 提示只作用于声明该属性的插件，顶部/底部调整高度；其他插件延续原行为。PluginManager 的递归 QDirIterator 本来已遍历子目录，移除额外递归调用，扫描结果保持一致而避免重复加载成本。

ScoreObserver 的 loadConfiguration/saveConfiguration 按无路径分隔符的名字存 JSON，跟随应用 dataPath（包括 -c 和便携模式）。writeTextFile 用 QSaveFile 原子写入，readTextFile 限 16 MiB、接受本地 file URL。乐谱交换格式/schema/指纹/值范围校验全部在插件，主程序不承担和弦 JSON 语义。

性能边界：上下文小节起点用数字索引二分查找；超过 64 音符的预览批次一次扫描 segments 建局部解析表，防止 tick2measure 逐音线性扫描。临时原生指针不跨这次 GUI 调用缓存。首次索引、全谱检测和初始标注仍有成本，播放/隐藏/插件未开启时不运行全谱任务；不能承诺所有工程零开销或 DAW 硬实时。

新增回归：tst_scoreobserver 的踏板起落/范围、分批帧、琶音/休止、原子配置；tst_pluginhost 的真实主窗口/插件菜单/停靠/析构。测试采用独立目录、关闭硬件音序器，Qt Windows 渲染用于布局截图；不能替代实际音频/MIDI 设备和长时间编辑验收。最终测量与通过项见 CHANGELOG。
''';write('personal/docs/10-score-observer.md',s)
# Refresh anchors from source, not stale line numbers, and add the new maintenance entry points.
p=R/'personal/docs/source-map.tsv';lines=p.read_text(encoding='utf-8').splitlines()
lines += [
    '踏板/琶音上下文\tmscore/plugin/api/scoreobserver.cpp\tQVariantMap ScoreObserver::contextSnapshot(\t0\t即时音/上下文分离，小节/休止/踏板边界\tmtest/mscore/scoreobserver',
    '谱面屏幕标注\tmscore/plugin/api/scoreobserver.cpp\tvoid ScoreObserver::applyPreview(\t0\t数值定位、碰撞避让、全谱/当前层\tmtest/mscore/pluginhost',
    '插件停靠状态\tmscore/plugin/qmlplugin.cpp\tvoid QmlPlugin::attachPanelDock(\t0\t实际区域/悬浮通知，可选横条高度\tmtest/mscore/pluginhost',
    '插件菜单/析构回归\tmtest/mscore/pluginhost/tst_pluginhost.cpp\tclass TestPluginHost\t0\t真实 Qt 主窗口、菜单、重排和停靠\tmtest/mscore/pluginhost']
for i,line in enumerate(lines):
    parts=line.split('\t')
    if len(parts)<4 or not (R/parts[1]).is_file():continue
    content=(R/parts[1]).read_text(encoding='utf-8-sig').splitlines()
    matches=[n+1 for n,text in enumerate(content) if parts[2] in text]
    if matches:parts[3]=str(matches[0]);lines[i]='\t'.join(parts)
write('personal/docs/source-map.tsv','\n'.join(lines)+'\n')
