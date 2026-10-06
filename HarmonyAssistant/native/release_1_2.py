# -*- coding: utf-8 -*-
"""One-time 1.2 deployment and documentation; preserve prior files and releases."""
from pathlib import Path
import csv, hashlib, shutil, subprocess, zipfile

base=Path(__file__).resolve().parents[1]
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
install=repo/'msvc.install_harmony_1_2_x64'
user=Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')
git=r'E:\Git\cmd\git.exe'
parent='a818d9a7009306a721363b17a2aab4ee3178ab09'
names=['HarmonyAssistant_MS3.qml','Harmony.js','Preferences.js','Analysis.js','ConfigurationEditor.qml',
       'SettingsStore.qml','PanelCard.qml','UiLabel.qml','StableLabel.qml','ColorOption.qml','AppearanceEditor.qml','README.md']
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as stream:stream.write(text)

# Verify all existing enabled files before making any replacement.
for name in names:
    target=user/name
    if not target.exists():continue
    previous=subprocess.check_output([git,'-C',str(repo),'show',parent+':share/plugins/HarmonyAssistant/'+name])
    assert target.read_bytes().replace(b'\r\n',b'\n')==previous.replace(b'\r\n',b'\n'),name
for name in names:
    target=user/name
    if target.exists():
        backup=user/(name+'.pre-1.2.0.bak')
        if backup.exists():assert backup.read_bytes()==target.read_bytes(),backup
        else:shutil.copy2(str(target),str(backup))

p=base/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('# 和声助手 1.1.0','# 和声助手 1.2.0',1).replace('个人主程序版本 `0.3.0`','个人主程序版本 `0.4.0`',1)
s=s.replace('msvc.install_harmony_1_1_x64','msvc.install_harmony_1_2_x64').replace('`.pre-1.1.0.bak`','`.pre-1.2.0.bak`',1)
s=s.replace('`PanelCard.qml`、`UiLabel.qml`。标准','`PanelCard.qml`、`UiLabel.qml`、`StableLabel.qml`、`ColorOption.qml`、`AppearanceEditor.qml`。标准',1)
section='''## 1.2 显示与交互

- 顶部横条默认居中，可在右侧直接切换左 / 中 / 右；设置中的「横条位置」还支持 0–100% 自定义位置，并给右侧按钮留出空间。位置自动保存。横条的详细面板和悬浮功能保留。
- 「谱面外观与位置」选择和弦 / 级数 / 两者，以及和弦在左、级数在左、和弦在上、级数在上。可设置字号 60–200%、正常文字色、当前高亮文字和背景色。
- 默认使用当前谱样式的和弦字体（通常 Edwin），也可选择 Edwin 或 Arial。紧凑字距使用真实字体度量；这是屏幕文本，不会创建或解析原生 Harmony 对象的专用后缀字形。
- 新主程序在写入音符的位置生成固定和弦记号，和声变化时生成新标记，有新音的小节起点也会重复显示。播放仅改变当前固定记号的高亮，不让和弦文字跟着当前音移动，不添加缩放动画或持续动画计时器。
- 同一系统、同一乐器统一使用一行位置；在四条邻近行中选择较能容纳标记的一行。水平位置始终对应节拍锚点；冲突时省略，避免个别记号上下漂移和遮住原有谱面。过大字号或极密集记谱可能不能放下全部标记。
- 双击固定和弦 / 级数记号会聚焦面板；停止时选择该位置的所属乐器并显示分析，顶部横条会打开详情窗口。播放中聚焦面板，不改变播放位置。
- 侧栏的匹配、候选、告警和音程区保留固定空间，键盘位置不会随和弦文字长短跳动。过长内容截断显示，悬停查看全文；调整面板宽度仍会正常切换布局。
- 新增「离调和弦强调」及独立强调色，作用于面板和固定记号；原有功能音配色保留。依据所选和弦模板是否含调外音判断，小调常见 V / 导音和弦允许升七级；这不是唯一的功能和声判定，关闭开关可取消强调。
- 每个功能色和谱面样式色都有可点击色块和「选色」按钮；颜色对话框与十六进制输入同时可用。新设置兼容旧配置，每次加载自动读取，也随配置 JSON 一起导入导出。

以上固定记号、高亮索引和双击需要主程序 0.4.0；旧主程序保留兼容路径。

'''
s=s.replace('## 1.1 新功能',section+'## 1.1 新功能',1)
s=s.replace('`SettingsStore.qml`、`PanelCard.qml`、`UiLabel.qml` 负责配置与排版。','`SettingsStore.qml`、`PanelCard.qml`、`UiLabel.qml`、`StableLabel.qml` 负责配置与稳定排版；`AppearanceEditor.qml`、`ColorOption.qml` 负责样式与选色。')
s=s.replace('上述八个运行文件','上述十一个运行文件')
s=s.replace('python HarmonyAssistant/tests/test_modern_panel.py','python HarmonyAssistant/tests/test_modern_panel.py\npython HarmonyAssistant/tests/test_fixed_panel.py',1)
s=s.replace('`tst_scoreobserver` 11 项','`tst_scoreobserver` 13 项',1)
s=s.replace('检查原生 QML 窗口截图。','检查原生 QML 窗口截图；本轮另验证同一行固定记号、真实鼠标双击、低音锚点跳转和真实颜色对话框。',1)
s=s.replace('1000 小节/6000 音符实测：首次索引 24.34 ms，1000 次原生缓存查询 2.07 ms，1000 次踏板/时序上下文查询 5.37 ms；6000 音符的数值分析帧 20.20 ms、全谱色层定位 23.23 ms。真实 QML 跨接口 1000 次查询约 10 ms，上下文约 19 ms。','1000 小节/6000 音符本轮实测：首次索引 24.03 ms，1000 次原生缓存查询 1.68 ms，1000 次踏板/时序上下文查询 4.26 ms；6000 音符的数值分析帧 16.03 ms、全谱色层定位 16.12 ms。6000 音符 / 1000 固定标记的索引测试中，1000 次高亮切换共 0.716 ms，此数值不包含实际屏幕重绘；只查询每乐器的有序标记并更新旧/新包围框，不复制全谱颜色表。真实安装 QML 跨接口 1000 次查询约 8 ms，上下文约 19 ms。')
s+='\n本轮真实安装宿主在同一隔离设置目录连续启动两次，验证仅级数、上下顺序、140% 字号、颜色、横条右对齐和功能名能自动恢复。Windows 部署补齐同 SDK 的 Qt5QmlModels.dll / Qt5QmlWorkerScript.dll；旧安装保留。\n'
write(p,s)
for directory in [repo/'share/plugins/HarmonyAssistant',install/'plugins/HarmonyAssistant',user]:
    directory.mkdir(parents=True,exist_ok=True)
    for name in names:
        shutil.copy2(str(base/name),str(directory/name))
        assert (directory/name).read_bytes()==(base/name).read_bytes(),name
for source,destination in [('run_native_gui.py','test_harmony_gui.py')]:
    shutil.copy2(str(base/'tests'/source),str(repo/'personal/tools'/destination))
smoke=(base/'tests/native-smoke.qml').read_text(encoding='utf-8')
write(repo/'mtest/mscore/scoreobserver/smoke.qml',smoke.replace('../HarmonyAssistant_MS3.qml','../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml'))
write(repo/'personal/VERSION','0.4.0\n')
entry='''## 0.4.0 — 2026-10-05

- 类型：和声助手 1.2.0 显示与交互完善；上游应用仍为 3.7.0，数据格式不变。
- 插件需求：顶部横条默认居中、可选左右及百分比位置；谱面只和弦/只级数/同时显示、四种排列、字体/字号/颜色及离调强调；稳定侧栏区域、悬停全文、实际颜色对话框。设置 schema 1 向后兼容并自动保存加载，原分析/配色/交换/手动/键盘功能保留。
- 原生修改：mscore/notepreview.h 添加固定文字布局、每乐器有序标记索引和小型活动集合；mscore/plugin/api/scoreobserver.h/.cpp 提供 setActiveScorePreview、previewActivated、受限样式描述符、同系统/乐器统一四行避让。播放切换只改活动集合和旧/新标记脏区域，不复制全谱 QHash。
- 视图接线：mscore/scoreview.h/.cpp 在屏幕 paint 单独绘制固定记号，避免依赖当前音符绘制；mscore/events.cpp 双击命中标记时通知所属观察器，非命中沿原处理；mscore/plugin/qmlplugin.h/.cpp 增加 focusPanel。弱 QObject 接收目标，析构仍只比较不透明 Element 地址。
- 解耦：界面、配置、音乐解释/离调模板规则都在 share/plugins/HarmonyAssistant；新增 StableLabel/ColorOption/AppearanceEditor，共十一个运行文件及 README。原生仅提供泛用屏幕标记、时间索引和交互。没有修改 libmscore 数据、序列化、Seq、Driver 或音频回调。
- 排版边界：固定文字锚定写入音符/节拍；同系统/乐器统一行，最多四个邻近候选，冲突省略。默认取谱样式的和弦字体（Edwin），不是 Harmony 原生后缀渲染。太密或太大文字不能保证全部放下；只作用屏幕，不写入 MSCX/PDF/undo。离调强调基于模板含调外音，小调 V/导音允许升七级，不保证唯一功能解释。
- 验证：Release 主程序和测试编译/链接成功；tst_scoreobserver 13、既有 tst_note 11、真实 tst_pluginhost 3 项通过，0 失败/跳过。JS 和 Qt5 面板通过，验证旧配置/样式限值/离调规则、播放不重建底层、左右居中和侧栏固定位置；GUI 验证菜单崩溃路径、固定记号同一行、真实鼠标双击、低音锚点整乐器跳转、选色器写入、顶栏/悬浮/停靠/关闭重开。截图已检查。
- 安装：独立 msvc.install_harmony_1_2_x64/bin/MuseScore3Evo.exe；补齐同 Qt SDK 的 Qt5QmlModels.dll / Qt5QmlWorkerScript.dll，解决独立启动缺库。旧程序/目录/备份保留。用户启用副本逐个与父提交比较后保存 .pre-1.2.0.bak，再同步十二个发布文件。
- 实际安装 smoke：独立 -c 设置连续两次启动，通过 Cmaj13/6 持续音、原色不变、配置保存/再读取、空拍清空、分析帧与索引复用；第二次自动恢复仅级数、级数在上、字号 140%、颜色 #224466、横条右对齐和功能名 third。
- 性能：1000 小节/6000 音符首次索引 24.031 ms；1000 次缓存 snapshot 1.678 ms、context 4.262 ms；数值帧 16.030 ms、全谱色层几何 16.123 ms。6000 音符/1000 标记的索引单测中，1000 次高亮切换共 0.716 ms（不含实际重绘）；安装 QML 跨接口 snapshot 约 8 ms、context 19 ms。初始检测/布局有成本，不承诺所有工程零开销或 DAW 硬实时。
- 测试夹具修正：固定标记使用实际写入 tick480 的锚点，不误用持续低音；搜索范围按实际 spatium 扩展至乐器上方，缩放取整后用文字框内部坐标双击。没有为测试改谱面排版或生产导入路径。运行时完整 staging 防止缺 DLL 导致测试无法启动。
- 未验收：实际音频/MIDI 设备、长时间会话和全部特殊谱法；原有延音/踏板语义未改变。实际 GUI fixture 关闭硬件音序器，不控制用户已打开的应用。
- 日志：msvc.build_harmony_release_x64/harmony-1-2-build.log、harmony-1-2-install.log、harmony-observer-1-2/gui.txt、harmony-note-1-2/gui.txt、harmony-gui-1-2/gui.txt 和截图；插件 tests/native-smoke-installed-1-2。更新相关指南、源码索引，基线快照保留。
- Git 父提交：a818d9a7009306a721363b17a2aab4ee3178ab09。
- Git 提交主题：feat(plugins): align fixed harmony annotations and configurable display。
- 提交定位：personal-v0.4.0 标签指向本条提交，git rev-parse personal-v0.4.0 查询 SHA；核对远端后普通 push origin/3.x 与标签，不强推。

'''
p=repo/'personal/CHANGELOG.md';s=p.read_text(encoding='utf-8');assert '## 0.4.0' not in s;write(p,s.replace('## 0.3.0',entry+'## 0.3.0',1))
p=repo/'personal/docs/10-score-observer.md';s=p.read_text(encoding='utf-8').replace('（个人版本 0.3.0）','（个人版本 0.4.0）',1)
s+='''
## 0.4.0：固定记号、样式与点击

描述符可含 chord / degree、chordTick / chordUntil（半开区间）、chordOrder（0–3）、chordScale（0.6–2）、chordFont、chordColor / highlightColor / highlightBackground。输入长度和数值范围受限，空字体采用 score 的 chordSymbolAFontFace。同系统/乐器用共同顶部行；固定标记在 ScoreView::paint 独立绘制，不依赖当前 Note 的 draw，不改模型排版。音旁 label 保留原有避让规则。过密标注省略，不无限上移。

setActiveScorePreview(tick) 在每乐器有序标记索引二分查当前区间，仅改变小型 QSet，重绘旧/新标记；tick=-1 清高亮。不要把当前 chord 重复附到每个活动音符。固定 base 层与当前音符层分别维护；打印/foto 沿原语义。

命中 ScoreView::activateNotePreview 后向弱 QObject 接收者调用 activatePreview，发出 previewActivated(tick, partStartTrack)。events.cpp 仅在左键双击命中时消费事件。插件 focusPanel() 聚焦已有停靠窗口，不强制悬浮；和声插件决定停止时选位置、横条打开详情，播放中不改变播放位置。QPointer 防止销毁回调；Element 键仍禁止解引用。

真实 GUI suite 验证固定行、普通鼠标双击、低音锚点整乐器跳转和颜色对话框。新增 fixedMarkerHighlightAndStyle / fixedMarkerHighlightPerformance；已测性能与边界以 CHANGELOG 0.4.0 为准。
''';write(p,s)
additions={
'01-architecture.md':'\n0.4.0 固定标记的几何和活动索引留在 NotePreviewLayers，ScoreView::paint 屏幕绘制，events.cpp 双击转发与 QmlPlugin::focusPanel 为局部接线。音乐模板、离调强调与样式配置仍在插件；没有新增模型/音频依赖。\n',
'04-feature-map.md':'\n0.4.0 和声显示入口：share/plugins/HarmonyAssistant/AppearanceEditor.qml 配置位置/顺序/颜色/字体，ColorOption.qml 选色，StableLabel.qml 固定行高与全文提示。原生固定记号、高亮和双击见 scoreobserver.*、notepreview.h、ScoreView::paint / activateNotePreview、events.cpp；真实交互测试为 tst_pluginhost。\n',
'05-piano-development.md':'\n0.4.0 和弦/级数记号固定在乐器顶谱表上方同一行，播放仅高亮；低音锚点双击以 Part::startTrack 聚焦整乐器。小调 V/导音允许升七级的离调强调规则属于插件，不能视为新的声音识别/踏板算法。\n',
'06-build-and-test.md':'\n0.4.0 使用 msvc.install_harmony_1_2_x64 独立安装，另需同 SDK Qt5QmlModels.dll / Qt5QmlWorkerScript.dll。GUI staging 测试可能从 SDK PATH 找到 DLL，最终必须脱离该 PATH 运行实际安装 smoke；同一 -c 目录运行两次验证配置恢复。Qt GUI fixture 关闭硬件音序器，不能替代设备验收。\n'}
for name,addition in additions.items():
    p=repo/'personal/docs'/name;write(p,p.read_text(encoding='utf-8')+addition)
p=repo/'personal/docs/README.md';write(p,p.read_text(encoding='utf-8').replace('个人版本 0.3.0 提供','个人版本 0.4.0 提供',1))
p=repo/'personal/docs/source-map.tsv';rows=list(csv.DictReader(p.open(encoding='utf-8',newline=''),delimiter='\t'))
new=[('mscore/plugin/api/scoreobserver.cpp','ScoreObserver::setActiveScorePreview','固定区间高亮，不复制全谱色表'),
     ('mscore/scoreview.cpp','ScoreView::activateNotePreview','固定记号点击命中与弱目标转发'),
     ('mscore/plugin/qmlplugin.cpp','QmlPlugin::focusPanel','聚焦已有插件窗口，保留停靠状态')]
for path,symbol,role in new:rows.append(dict(topic='plugin-preview',path=path,symbol=symbol,line='',role=role,tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'))
for row in rows:
    lines=(repo/row['path']).read_text(encoding='utf-8-sig').splitlines()
    hits=[str(i+1) for i,line in enumerate(lines) if row['symbol'] in line];assert hits,row
    row['line']=hits[0]
with p.open('w',encoding='utf-8',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
with zipfile.ZipFile(str(base/'dist/HarmonyAssistant-1.2.0.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
    for name in names:archive.write(str(base/name),'HarmonyAssistant/'+name)
print('1.2.0 runtime copies and backups verified; personal 0.4.0 documented.')
