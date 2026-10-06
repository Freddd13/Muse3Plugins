"""Write reviewed documentation and synchronize the plugin into the native repository.

The plugin workspace is the editing source; share/plugins contains its release snapshot.
No other plugin or previous artifact is removed.
"""
from pathlib import Path
import csv, shutil

base = Path(__file__).resolve().parents[1]
repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')

readme = '''# 和声助手 1.0.0

MuseScore 3 Evolution 钢琴编曲面板。完整版搭配个人主程序版本 `0.2.0` 使用；界面与和弦算法仍是独立插件，主程序仅新增通用观察和临时绘色接口。

## 开始使用

本机新程序：`E:\\programming\\funcodes\\muse3_dev\\MuseScore\\msvc.install_harmony_release_x64\\bin\\MuseScore3Evo.exe`。

插件已放入新程序的 `plugins/HarmonyAssistant/`。启动新程序，在「插件 → 插件管理器」勾选 `HarmonyAssistant_MS3.qml`，然后运行「插件 → Harmony Assistant」。选择钢琴谱上的音符即可；普通空格播放自动跟随。

单独安装插件时，将 `HarmonyAssistant_MS3.qml`、`Harmony.js`、`PanelCard.qml`、`UiLabel.qml` 四个文件放在同一目录。标准 MuseScore 3 仍可使用选区分析；没有原生接口时不能准确跟随播放，也没有独立的屏幕配色层。

## 已实现功能

- 当前和弦、罗马级数、转位、实际音名与八度，以及歧义候选。
- `1 / 3 / 5 / 7 / 9 / 11 / 13` 功能格，区分实际音、缺音和未使用音；挂音保留 `2 / 4`，六和弦保留 `6`，♯11 与 ♭5 分别显示。
- 29 种和弦模板：三和弦、七和弦、挂音、六和弦、加九、九/十一/十三、♭9、♯9、♯11、小大七等。弱双音不强行判为完整和弦。
- 默认合并当前乐器全部谱表与声部，并包括持续音；可切换全谱。
- 手动根音和类型、大小调、读取调号、键盘、刷新和恢复原色均保留。键盘及设置可折叠，280 px 窄面板可滚动。
- 播放时读取音序器已激活的 NoteEvent；跟随真实音符启停、反复和跳转，不用墙钟推算乐谱进度。
- 新主程序默认开启屏幕临时配色：空拍、取消选区、切文件、隐藏/关闭面板时清除。音符原色、撤销记录、乐谱保存和导出内容不被改写。编辑时原生选中颜色保留；播放标记显示为细线。

## 调性与分析语义

自动主音取当前位置调号，包括中途调号变化；调号不能区分关系大小调，请自行选择。手动设置主音后不再自动覆盖，「读调号」恢复自动读取。级数使用平行大调基准，例如 A 小调中的 C 大三和弦是 ♭III，E 大三和弦是 V。

实际音名保留谱面 TPC 拼写；主音菜单在 C♭ 等边界调性使用等音替代。停播时按记谱时值读取持续音，播放时按 NoteEvent 发声音高读取。踏板下 Note-off 后的声学残响不计入和弦，避免将整段踏板内的旧音全部堆成当前和弦。和弦识别是辅助建议，音高集合本身不能唯一决定上下文和根音。

## 兼容旧程序

检测到 `newScoreObserver()` 后自动使用原生路径。旧程序默认只显示面板颜色；手动打开谱面配色会通过标准 API 修改颜色属性并产生撤销记录，保存/导出前需恢复原色。此兼容模式的撤销可能重新带回历史颜色；撤销后自动暂停配色，避免回调写谱。完整版没有这些限制。

`HarmonyAssistant_MS3.original.qml.bak` 保留最初原稿。`evolution-playback-api.patch` 保留旧的两个属性方案，已由 `native/score-observer.patch` 替代，不能叠加应用。`native/prepare_patch.py` 和 `finalize_native.py` 是本次开发的基线迁移记录，不能对已更新的源码重复运行。

## 维护边界

- `Harmony.js`：ES5 音乐逻辑，不依赖 Qt/MuseScore 对象。
- 主 QML：选区、调性、显示状态与宿主适配；`PanelCard.qml`、`UiLabel.qml` 负责基础排版。
- 主程序 `ScoreObserver`：GUI 线程真实位置、数值快照、按内容版本失效的声部索引。
- `NotePreviewLayers`：视图内独立颜色层；模型、音频回调、文件格式不承担和弦功能。

本目录是插件编辑源。发布时将四个运行文件及本 README 同步到主仓库 `share/plugins/HarmonyAssistant/`，主仓库已有的递归安装规则会打包它们；不要单独修改那份发布快照。主程序架构/API/合并点详见其 `personal/docs/10-score-observer.md`。

## 验证与性能

在插件工作区运行：

```powershell
node HarmonyAssistant/test-harmony.cjs
python HarmonyAssistant/tests/render_and_check.py
python HarmonyAssistant/tests/run_native_smoke.py <新程序exe> <独立测试目录>
```

前两项分别验证和弦逻辑，以及 Qt 5 的持续音、颜色恢复、撤销、模拟播放、隐藏恢复和 280/360/460 px 排版。第三项用真实 Release 程序、独立设置和测试谱验证原生接口、Cmaj13、原色不变和缓存复用。

主程序新增 `tst_scoreobserver`，检查持续音与范围、保存字节一致、预览/普通绘制区别、撤销失效、颜色层隔离及 1000 小节/6000 音符性能；既有 `tst_note` 用于相关回归。最终实测数字和结果见主程序个人更新日志。尚未对实际音频设备、长时间播放、踏板声学残响和所有谱面特殊写法作完整实机验收，不能声称达到 DAW 硬实时保证。

播放位置来自原程序 GUI 侧约 20 ms 心跳；插件最多合并等待 16 ms，再按有效音集合变化识别和绘色。普通选区合并 55 ms；持续音集合不变时不重复识别。首次/编辑后构建当前范围索引，随后每声部二分查询；隐藏原生面板停止计时和更新。
'''
base.joinpath('README.md').write_text(readme, encoding='utf-8')

guide = '''# 10 通用乐谱观察与临时音符预览（个人版本 0.2.0）

和声助手采用插件 + 最小原生接口。纯插件可完成和弦解释、级数、功能标签和界面，但标准 API 没有逐拍播放信号和独立临时色层；反复写 Note.color 会影响撤销、保存与排版。因此原生侧只提供可供其他插件复用的查询/预览能力，音乐解释留在独立 QML/JS。

## 模块与合并点

新增 [scoreobserver.h](../../mscore/plugin/api/scoreobserver.h)、[scoreobserver.cpp](../../mscore/plugin/api/scoreobserver.cpp)，由 `PluginAPI::newScoreObserver()` 创建并以插件为 QObject parent。[notepreview.h](../../mscore/notepreview.h) 是无模型修改的图层助手。已有文件只接入插件工厂/CMake、ScoreView 的屏幕绘制与清理、Note 的可指定颜色 draw 重载；默认 draw 仍沿原路径。

插件发布快照位于 [share/plugins/HarmonyAssistant](../../share/plugins/HarmonyAssistant/README.md)，由现有 share 的递归安装规则安装；独立插件工作区是日常编辑源。除新增四个插件运行文件，没有修改其他插件。核心未新增颜色属性、序列化字段或音频线程职责。后续合并上游优先复核 `Note::draw`、`ScoreView::drawElements/setScore/onElementDestruction` 和插件工厂的少量接线。

## 接口约定

```qml
var observer = newScoreObserver()
observer.score = curScore
var data = observer.snapshot(tick, firstTrack, endTrack, false)
// data.notes 中的描述符复制后添加 color，交给屏幕预览。
observer.setNotePreviewColors(coloredDescriptors)
observer.clearNotePreviewColors()
```

`score`、`enabled` 可写；`tick`、`playing`、`surfaceVisible`、`indexBuildCount`、`indexBuildMilliseconds` 只读。位置通过 `positionChanged` 通知。tick 是记谱 tick，track 范围是半开区间，边界自动限于当前 score。返回 notes、keySignature、bar、beat、tick；bar/beat 从 1 开始。描述符为 tick/track/index/pitch/tpc/writtenPitch/writtenTpc 数值，不缓存插件 Note 包装指针。

`snapshot(..., false)` 使用按 MasterScore 内容状态及范围失效的每声部索引，二分求当前位置持续音。`snapshot(..., true)` 在播放时读取 Seq 已有 GUI 侧 `activeNoteEvents()`；支持 NoteEvent 音高偏移，并把主谱音符投射到当前分谱。NoteEvent 对应的当前原音用 writtenPitch/TPC 校验后才能着色。Note-off 后的踏板声学残响不纳入集合；算法本身由插件解释。

连接 Seq 的 GUI 心跳、started/stopped 和 MasterScore 的 posChanged，不新增音频锁、计时器或 Driver 调用。隐藏 QQuickWindow 自动清层并停止位置通知，surfaceVisible 通知插件停止自己的计时。插件销毁/换谱、视图换谱、音符销毁均安全清理；QPointer 保护先关闭的谱面/视图。

## 屏幕预览

颜色图层按 owner 隔离，后注册层优先。相同描述符不会重复重绘，只重绘旧/新音符包围框的并集。原生编辑选中颜色、不可见音符和音域提示继续保留；播放标记另用细线。打印/PDF/图片导出沿默认 draw，截图模式也禁用色层。用户音符颜色、score 内容状态和 undo 不变，不需要保存前恢复。

## 验证与复现

新增 [tst_scoreobserver.cpp](../../mtest/mscore/scoreobserver/tst_scoreobserver.cpp) 及小谱例，使用完整 mscoreapp 测试库。测试包含 1000 小节/6000 音符、索引计时与缓存查询；预览前后 MSCX 字节一致，Note 默认绘制不变，撤销后数值索引变化并恢复。相邻 `tst_note` 验证原有音符行为。

Windows 回归需先构建共享 PCH（独立 mtest.sln 不自动构建它），再编译目标：

```powershell
cmake --build msvc.build_harmony_release_x64 --config Release --target ms_pch --parallel 1
# 使用 VS2019 的 MSBuild（Build Tools shell 或 vswhere 查到的路径）
MSBuild msvc.build_harmony_release_x64/mtest/mtest.sln /t:tst_scoreobserver`;tst_note /p:Configuration=Release /p:Platform=x64 /m:1
```

运行时把 SDK 的 `bin` 加入当前进程 PATH，并设置 `QT_QPA_PLATFORM=offscreen`、`QT_PLUGIN_PATH=<QtSDK>/plugins`；直接运行各目标的 `Release/*.exe` 或使用 CTest。完整 Qt 测试运行时与构建配置需一致，不能混用 Debug 与 Release Qt DLL。新增 `testutils -> freetype` 仅解决 testutils 直接包含 sym.h 的头依赖；`tst_note` 的 Windows Chord 名称保护扩展到 MSVC，没有改变应用行为。

真实程序的插件加载/缓存/颜色属性隔离用独立设置、CLI `-p` 和测试插件验证。最终通过项、性能、未验证的实际设备及运行环境限制以 [更新日志](../CHANGELOG.md) 为准。源码检查/模拟事件/邻近测试不能替代全部实际音频和编辑交互验收。
'''
repo.joinpath('personal/docs/10-score-observer.md').write_text(guide, encoding='utf-8')

append = {
 'README.md':'\n## 个人扩展：和声辅助\n\n个人版本 0.2.0 增加通用播放观察与屏幕临时配色，和声解释仍在独立插件；入口与边界见 [10 通用观察/预览](10-score-observer.md)。\n',
 '01-architecture.md':'\n## 通用插件观察与屏幕预览\n\n`mscore/plugin/api/scoreobserver.*` 在 GUI 线程提供数值快照与 Seq 位置事件；`mscore/notepreview.h` 在 ScoreView 内维护临时图层。核心 Note 只增加 draw 重载，默认绘制/文件格式/音频回调保持原语义。插件发布快照在 `share/plugins/HarmonyAssistant/`。详见 [10](10-score-observer.md)。\n',
 '04-feature-map.md':'\n## 和声辅助入口\n\n当前和弦、罗马级数、功能音和键盘在 `share/plugins/HarmonyAssistant/`；真实播放观察在 `mscore/plugin/api/scoreobserver.*`；屏幕配色在 `mscore/notepreview.h` 与 ScoreView，颜色不写模型。验证为 `mtest/mscore/scoreobserver` 和相邻 `mtest/libmscore/note`。接口与合并点见 [10](10-score-observer.md)。\n',
 '05-piano-development.md':'\n## 和弦观察与实时配色\n\n个人 0.2.0 的 ScoreObserver 提供按声部持续音和 Seq activeNoteEvents；插件实现和弦识别。播放音高与 writtenPitch/TPC 分开，跨分谱投射，踏板声学残响不纳入当前和弦。ScoreView 色层只作用屏幕，不影响撤销/保存/导出；保留编辑选中颜色及播放标记。参考 [10](10-score-observer.md)。\n',
 '06-build-and-test.md':'\n## 观察器回归（0.2.0）\n\n新增 `tst_scoreobserver` 使用完整 mscoreapp，覆盖持续音、撤销、保存和屏幕预览隔离、长谱缓存。Windows 测试需独立构建 `ms_pch` 后编译 mtest.sln；Release 运行时配置见 [10](10-score-observer.md)。相关 `tst_note` 的 Win32 Chord 名称保护已扩展到 MSVC。\n',
}
for name, text in append.items():
    file = repo / 'personal/docs' / name
    file.write_text(file.read_text(encoding='utf-8') + text, encoding='utf-8')

target = repo / 'share/plugins/HarmonyAssistant'
target.mkdir(parents=True, exist_ok=True)
for name in ['HarmonyAssistant_MS3.qml','Harmony.js','PanelCard.qml','UiLabel.qml','README.md']:
    shutil.copy2(base / name, target / name)

rows = list(csv.DictReader((repo/'personal/docs/source-map.tsv').open(encoding='utf-8',newline=''), delimiter='\t'))
rows += [
 dict(topic='插件实时观察',path='mscore/plugin/api/scoreobserver.cpp',symbol='ScoreObserver::ScoreObserver(',line='0',role='GUI 心跳与生命周期；不修改音频回调',tests='mtest/mscore/scoreobserver'),
 dict(topic='持续音缓存',path='mscore/plugin/api/scoreobserver.cpp',symbol='void ScoreObserver::ensureIndex(',line='0',role='内容状态/范围失效，每声部二分持续音',tests='mtest/mscore/scoreobserver'),
 dict(topic='屏幕临时音符颜色',path='mscore/scoreview.cpp',symbol='void ScoreView::setNotePreviewColors(',line='0',role='按 owner 隔离的屏幕色层，旧新局部重绘',tests='mtest/mscore/scoreobserver'),
 dict(topic='和声辅助插件',path='share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml',symbol='    function followNativePosition()',line='0',role='插件音乐解释、级数、功能音和 GUI 播放合并',tests='mtest/mscore/scoreobserver'),
]
for row in rows:
    lines = (repo / row['path']).read_text(encoding='utf-8').splitlines()
    hits = [str(index+1) for index,line in enumerate(lines) if row['symbol'] in line]
    assert hits, row
    row['line'] = hits[0]
with (repo/'personal/docs/source-map.tsv').open('w',encoding='utf-8',newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
print('Plugin release snapshot and native maintenance guides synchronized')
