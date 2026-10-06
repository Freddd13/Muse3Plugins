# -*- coding: utf-8 -*-
"""One-time verified 1.3 deployment/docs. Run only after native suites and smoke pass."""
from pathlib import Path
import csv,shutil,subprocess,zipfile
base=Path(__file__).resolve().parents[1]
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
install=repo/'msvc.install_harmony_1_3_x64'
user=Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')
git=r'E:\Git\cmd\git.exe'
parent='9a5ae07ec43b3c6aacd53692c199b8f94ced8e75'
names=['HarmonyAssistant_MS3.qml','Harmony.js','Preferences.js','Analysis.js','ConfigurationEditor.qml',
       'SettingsStore.qml','PanelCard.qml','UiLabel.qml','StableLabel.qml','ColorOption.qml','AppearanceEditor.qml','README.md']
def write(p,s):
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=base/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('1000 小节/6000 音符本轮实测','1.2 版本的 1000 小节/6000 音符实测',1)
write(p,s+'\n1.3 Release 验证：tst_scoreobserver 14、tst_note 11、实际 tst_pluginhost 5 项通过，无失败/跳过；固定布局、配置/交换与双面板 Qt 测试通过。新增用例验证同一持续音两个变化的实际 x 坐标、原谱和弦/Roman 优先级、遮罩开关、移动标签与原生文字光标避让、双面板共用一个观察器和配置控件、关闭重开/悬浮返回。实际安装连续启动两次，新增三个开关与既有样式均恢复。日志及硬件/长会话限制见个人 CHANGELOG 0.5.0。\n')
for name in names:
    target=user/name
    if not target.exists():continue
    previous=subprocess.check_output([git,'-C',str(repo),'show',parent+':share/plugins/HarmonyAssistant/'+name])
    assert target.read_bytes().replace(b'\r\n',b'\n')==previous.replace(b'\r\n',b'\n'),name
for name in names:
    target=user/name
    if target.exists():
        backup=user/(name+'.pre-1.3.0.bak')
        if backup.exists():assert backup.read_bytes()==target.read_bytes(),backup
        else:shutil.copy2(str(target),str(backup))
for directory in [repo/'share/plugins/HarmonyAssistant',install/'plugins/HarmonyAssistant',user]:
    for name in names:
        shutil.copy2(str(base/name),str(directory/name))
        assert (directory/name).read_bytes()==(base/name).read_bytes(),name
smoke=(base/'tests/native-smoke.qml').read_text(encoding='utf-8')
write(repo/'mtest/mscore/scoreobserver/smoke.qml',smoke.replace('../HarmonyAssistant_MS3.qml','../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml'))
exchange=(base/'tests/test-exchange.cjs').read_text(encoding='utf-8')
exchange=exchange.replace("path.join(__dirname,'..',name)","path.join(process.argv[2] || path.join(__dirname,'../../../share/plugins/HarmonyAssistant'),name)")
write(repo/'mtest/mscore/scoreobserver/test-exchange.cjs',exchange)
write(repo/'personal/VERSION','0.5.0\n')
entry='''## 0.5.0 — 2026-10-06

- 类型：和声助手 1.3.0，补齐移动/编辑遮挡、变化节拍锚点、背景遮罩与顶部摘要/右侧详情。上游应用仍为 3.7.0，谱面格式不变。
- 插件：share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml 的全谱描述符在释放/踏板变化等无新音时也生成独立标记，chordTick 与用于定位乐器的数值 Note 描述符分离；Preferences.js / AppearanceEditor.qml 增加 chordMask、respectExistingHarmony、dualPanel，schema 1 向后兼容、自动读取/原子保存/配置交换。顶部操作三行，保持居中/自定位置，右侧完整内容仍能加宽双列、拖动悬浮；原功能保留。
- 原生标注：mscore/notepreview.h 分离颜色 QHash 和标记 QVector，一个持续 Note 可对应多次变化；每乐器二分时间索引和小型活动集合不变。QMultiHash 不透明来源索引用于析构时清掉该音所有标记，不调用已析构 Element 的虚函数；旧内联记号描述符仍支持。
- 原生几何：mscore/plugin/api/scoreobserver.h/.cpp 用变化所在 Measure/System 的节拍 x 锚点，无新音时在相邻 ChordRest 位置之间插值，不使用来源音的位置；同系统/乐器共同四行避让。当前功能标签避开固定记号缓存并复用全谱几何，原谱普通/Nashville 和弦及 Roman 级数可优先保留，另一个字段可补充。背景遮罩关闭后仍避让原谱并保留文字高亮。
- 编辑优先级：mscore/scoreview.h/.cpp 隐去与当前原生编辑/拖动对象相交的临时标签，编辑状态不消费插件双击；mscore/editelement.cpp 在开始/结束编辑时补齐标记区域刷新。普通选择/播放不移动固定记号；原生对象、光标和快捷键仍走原流程。
- 通用双面板：mscore/plugin/qmlplugin.h/.cpp 暴露 detailPanelHost/detailPanelVisible、showDetailPanel/focusDetailPanel 和关闭通知；一个辅助 QDockWidget/QQuickWindow 可接受已有 QML 控件的视觉重挂载。默认右侧，标题/背景由插件属性提供；关闭保存偏好，主插件销毁清理辅助面板。不另建 QML engine/ScoreObserver/全谱分析；和声/配置/UI 仍在插件，无 libmscore 模型、Seq、Driver 或音频回调改动。
- 验证：Release 主程序及三组测试编译/链接；tst_scoreobserver 14、tst_note 11、真实 tst_pluginhost 5 项通过，0 失败/跳过。新增持续音共享源的多个记号与析构清理、真实无新音 tick240 的横坐标、双面板单观察器/控件共享/关闭重开/悬浮返回、原谱和弦/Roman 优先级、遮罩显隐、当前标签移动不遮固定记号、原生和弦文字编辑与方向键光标。JS、固定位置及双面板 QML 测试通过；截图检查。
- 性能：1000 小节/6000 音符首次索引 23.187 ms；1000 次缓存 snapshot 1.779 ms、context 4.517 ms；数值帧 16.364 ms、全谱色层几何 16.368 ms。6000 音符/1000 标记的单测中，1000 次高亮切换共 0.909 ms（不含屏幕重绘）；实际安装 QML 跨接口 snapshot 10–11 ms、context 18–19 ms。遮罩单测首次对白纸比较白色背景无可见差异，改用有色高亮背景后验证通过，不改生产实现。
- 部署：独立 msvc.install_harmony_1_3_x64/bin/MuseScore3Evo.exe，保留全部旧安装；同 SDK Qt5QmlModels.dll / Qt5QmlWorkerScript.dll 补齐。启用副本逐文件与父提交比较，保存 .pre-1.3.0.bak 后同步十二个发布文件。配置 restart smoke 同一隔离目录连续启动两次验证新增三个开关与已有样式/功能名恢复，临时图层不改原色。
- 构建环境：PCH 缓存失效时只在构建进程设置 /Y- /MP1，不改上游默认；新增宿主字段后早期部分旧对象混用导致 GUI 创建崩溃，强制重新编译 mscoreapp 全部已有源（仅更新时间戳、不删文件）并重新链接后复验。该早期产物未部署到启用副本。审批服务曾因账户限额暂时无法完成自动审查，恢复后正常通过；没有绕过限制。
- 边界：密集/过大记号会省略；相邻节拍间位置是视觉插值；原谱和弦优先保留不改变原谱颜色。标注仅屏幕显示、不写 undo/MSCX/PDF；真实音频/MIDI 硬件与长会话未验收，不承诺零开销或 DAW 硬实时。
- 日志：msvc.build_harmony_release_x64/harmony-1-3-build.log、harmony-1-3-recompile.log、harmony-1-3-install.log、harmony-gui-1-3/gui.txt、harmony-observer-1-3/gui.txt、harmony-note-1-3/gui.txt；插件 tests/native-smoke-installed-1-3 与 native-gui-1-3。旧日志及首次调查基线保留。
- Git 父提交：9a5ae07ec43b3c6aacd53692c199b8f94ced8e75。
- Git 提交主题：feat(plugins): anchor harmonic changes and share detail docks。
- 提交定位：personal-v0.5.0 标签指向本次提交；git rev-parse personal-v0.5.0 查询 SHA。核对 origin/3.x 后普通 push 分支/标签，不强推。

'''
p=repo/'personal/CHANGELOG.md';s=p.read_text(encoding='utf-8');assert '## 0.5.0' not in s;write(p,s.replace('## 0.4.0',entry+'## 0.4.0',1))
additions={
'01-architecture.md':'0.5.0 将固定记号从音符颜色映射分离为时间标记向量，来源地址仅作析构清理。QmlPlugin 可提供一个共享 QML 控件的辅助停靠宿主；不重复创建分析或连接音频。',
'04-feature-map.md':'0.5.0 新入口：AppearanceEditor 配置原谱优先、背景遮罩、顶部/右侧共存；applyPreview / previewTickX 实现和声变化 x 锚点；QmlPlugin::showDetailPanel 接受一个已有控件树。编辑遮挡接线见 ScoreView::previewEditBounds / editelement.cpp，回归为 tst_pluginhost。',
'05-piano-development.md':'0.5.0 释放/踏板导致和弦变化但没有新音时，插件仍生成变化 tick 的标记；来源持续音可以在上一系统，几何取变化所在系统。该变化只影响分析展示，不修改 NoteEvent 或踏板解释。',
'06-build-and-test.md':'0.5.0 使用 msvc.install_harmony_1_3_x64。新增 QmlPlugin/NotePreviewLayers 字段后必须统一编译所有依赖该头文件的对象，再链接主程序及 GUI 测试；本机 PCH 无效时使用进程 _CL_=/Y- /MP1。只增量重编少数对象可能产生 ABI 混用，不能用一次链接成功代替真实宿主测试。',
'10-score-observer.md':'''0.5.0：独立标记、遮罩与共享详情

描述符 chordTick 可不同于来源 Note.tick；来源只数值定位乐器及析构身份。对应变化节拍有 ChordRest 用 segment.pagePos().x，无新音则按相邻节拍 x 插值，使用变化 Measure/System/Page。NotePreviewMarkers 独立存储，颜色表仍按 Note 查找；同一源多个变化不会互相覆盖。chordMask 默认 true；false 仅关背景，不关高亮/碰撞避让。preferExistingHarmony 默认由插件传 true，同 tick/Part 的 Harmony 可清除重复 chord 或 degree 字段，不更改原谱。当前层复用基础标签框并避开固定记号；原生编辑区域优先显示原对象和光标。

QmlPlugin 的 detailPanelHost 是弱窗口对应的 QQuickItem，detailPanelVisible 通知实际显示状态；showDetailPanel(bool) 创建/显隐单个辅助停靠窗口，focusDetailPanel 显式聚焦，panelDetailClosed 区分用户关闭。可选 detailPanelTitle/detailPanelBackground 由 QML 提供。插件通过 visual parent 重挂载同一控件，QObject ownership 保留在原根；没有第二个 QQmlEngine、ScoreObserver 或分析任务。辅助容器拥有 QWindow，插件销毁后 deleteLater 清理 dock；主面板关闭和设置持久化仍沿原生命周期。'''
}
for name,addition in additions.items():
    p=repo/'personal/docs'/name;s=p.read_text(encoding='utf-8')
    if name=='10-score-observer.md':s=s.replace('（个人版本 0.4.0）','（个人版本 0.5.0）',1)
    write(p,s+'\n'+addition+'\n')
p=repo/'personal/docs/README.md';write(p,p.read_text(encoding='utf-8').replace('个人版本 0.4.0 提供','个人版本 0.5.0 提供',1))
p=repo/'personal/docs/source-map.tsv';rows=list(csv.DictReader(p.open(encoding='utf-8',newline=''),delimiter='\t'))
for path,symbol,role in [('mscore/plugin/api/scoreobserver.cpp','static qreal previewTickX','变化节拍定位，无新音时插值'),('mscore/plugin/qmlplugin.cpp','QmlPlugin::showDetailPanel','共享控件的单辅助停靠窗口'),('mscore/scoreview.cpp','QRectF ScoreView::previewEditBounds','原生编辑/拖动优先区域')]:
    rows.append(dict(topic='plugin-display',path=path,symbol=symbol,line='',role=role,tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'))
for row in rows:
    lines=(repo/row['path']).read_text(encoding='utf-8-sig').splitlines()
    hits=[str(i+1) for i,line in enumerate(lines) if row['symbol'] in line];assert hits,row;row['line']=hits[0]
    if row['symbol']=='void ScoreObserver::applyPreview(':row['role']='独立和声变化标记、原谱优先与两层避让'
with p.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
with zipfile.ZipFile(str(base/'dist/HarmonyAssistant-1.3.0.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
    for name in names:archive.write(str(base/name),'HarmonyAssistant/'+name)
print('1.3 deployment backed up and verified; personal 0.5 documented.')
