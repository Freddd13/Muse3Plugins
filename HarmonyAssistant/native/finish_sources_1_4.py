# -*- coding: utf-8 -*-
"""One-time release preparation. Existing files and installs are preserved."""
from pathlib import Path
import subprocess,shutil
base=Path(__file__).resolve().parents[1]
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as out:out.write(text)
# Preserve the header's original CRLF convention, reducing merge noise.
p=repo/'mscore/notepreview.h';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
p=repo/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('// One shared row per system/part. No horizontal nudging: x remains the harmonic change\'s tick.',
    '// Prefer one row per system/part; lift colliding markers while keeping their tick x.')
write(p,s)
p=repo/'mtest/mscore/scoreobserver/smoke.qml';s=p.read_text(encoding='utf-8').replace('version: "1.3.0"','version: "1.4.0"')
assert 'persistedCorrection' not in s
s=s.replace('            panel.observer.setActiveScorePreview(600)', '''            while(panel.regionBuilder)panel.buildRegionChunk()
            if(panel.analysisDirty)result.failures.push("harmonic regions incomplete")
            result.persistedCorrection=panel.manualOverrides.length?panel.manualOverrides[0].chord:""
            if(result.persistedLabel==="third" && result.persistedCorrection!=="Am/C")result.failures.push("manual correction not restored on restart")
            panel.displayTick(480,true)
            panel.editRange("assign",0,720,13,1,0)
            if(panel.ownedRegion.chord!=="Am/C")result.failures.push("manual region assignment")
            panel.openAnnotation(0,0)
            if(panel.annotationTick!==0)result.failures.push("selected annotation tick")
            panel.observer.setActiveScorePreview(600)''')
# A is index 13 in the enharmonic root spelling array.
roots=(base/'Harmony.js').read_text(encoding='utf-8')
assert 'var rootPcs = [0,1,1,2,3,3,4,5,6,6,7,8,8,9,10,10,11]' in roots
write(p,s)
p=base/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('# 和声助手 1.3.0','# 和声助手 1.4.0',1).replace('完整版搭配个人主程序版本 `0.5.0`','完整版搭配个人主程序版本 `0.8.0`',1)
s=s.replace('msvc.install_harmony_1_3_x64','msvc.install_harmony_1_4_x64',1).replace('.pre-1.3.0.bak','.pre-1.4.0.bak',1)
s=s.replace('`ColorOption.qml`、`AppearanceEditor.qml`。标准','`ColorOption.qml`、`AppearanceEditor.qml`、`Timeline.js`、`RangeEditor.qml`。标准',1)
s=s.replace('## 1.3 记号优先级与双面板','''## 1.4 区间识别、人工修正与原生字体

- 设置 →「踏板内识别」选择「一个和弦」或「允许多个」。默认综合整个踏板区间的持续时长与音高证据，只生成一个识别结果；跨小节、延音链不单独产生变化点。多和弦模式仍允许同一踏板内换和声，但降低踏板残留与旧延长音的影响，优先考虑新伴奏与当前实际低音。级数按和弦根音计算，转位低音写在斜线后，不将低音当成新的级数根音。
- 全谱结果是按乐器保存的半开区间 `[start,end)`。相邻相同根音、类型、低音和调性合并；默认关闭小节重复记号，可单独开启。「顶部摘要结果」与「详细面板结果」各自选择实时或所属和弦，功能音和离调色也分别遵循所选结果。实时瞬间与区间综合结果允许不同。
- 谱面固定记号保持变化 tick 的 x；拥挤时将冲突记号放到更高的行，其他记号保持共同基线。最多六行，页外或原谱文字占满时显示省略数量提示；避免无限上移。单击或双击可聚焦面板，停止时记号也保持当前高亮。
- 设置 →「和声范围编辑」提供可拖动的左右范围手柄、起止 tick 精确输入、指定根音/类型/低音、拆分、合并、排除范围、恢复自动以及独立撤销/重做。手柄吸附到 60 tick（四分音符的八分之一）。选中记号再修正；在没有自动结果的位置也能指定新范围。范围操作只修改分析，不修改音符或占用谱面的撤销记录。
- 人工修正按谱面内容指纹原子保存，下次加载自动读取。编辑谱面导致指纹变化后，旧修正暂停应用并提供复核按钮，不静默套用错位范围。JSON 分析升级为 schema 2，包含区间和人工修正；仍接受 schema 1。CSV 导出区间起止、乐器、根音、低音和来源。
- 和弦使用原生 `Harmony` 的字形排版，在独立样式副本中生成缓存图片，默认遵循当前谱的和弦字体/后缀规则与字号。Edwin/Arial 覆盖仍可选，级数字体另设；缺字或字体回退会提示。样式变化使缓存失效，原谱的和弦列表、布局与保存内容不被预览改动。
- 临时着色现在通过原生 `Element::curColor` 保留选中、播放、拖放和隐藏状态的优先级；取消预览恢复原色。P 键盘与选区框宽度保持原实现，加入对照回归。

`Timeline.js` 负责分批区间构建与人工覆盖，`RangeEditor.qml` 负责范围交互。音乐规则仍在插件；软件本体仅补充延音攻击起点、当前踏板元数据、字形预览与鼠标命中。原生实现不会进入音频回调。复杂复调或一个踏板内实际多个和弦应选择多和弦模式或人工修正；识别不等于唯一的功能和声解释。

## 历史 1.3 记号优先级与双面板''',1)
s=s.replace('## 1.2 显示与交互','## 历史 1.2 显示与交互',1).replace('## 1.1 新功能','## 历史 1.1 新功能',1)
s=s.replace('上述十一个运行文件','上述十三个运行文件')
s=s.replace('- `Harmony.js`：ES5 音乐逻辑，不依赖 Qt/MuseScore 对象。','- `Harmony.js`：ES5 音乐逻辑，不依赖 Qt/MuseScore 对象；`Timeline.js`：加权区间构建、合并及人工覆盖；`RangeEditor.qml`：范围编辑交互。')
s=s.replace('node HarmonyAssistant/tests/test-exchange.cjs','node HarmonyAssistant/tests/test-exchange.cjs\nnode HarmonyAssistant/tests/test-timeline.cjs',1)
s=s.replace('python HarmonyAssistant/tests/test_dual_panel.py','python HarmonyAssistant/tests/test_dual_panel.py\npython HarmonyAssistant/tests/test_regions_panel.py\npython HarmonyAssistant/tests/test_range_drag.py',1)
s+='''
1.4 验证：原生观察器 16 项、实际 Widgets/QML 宿主 10 项通过。新增持续踏板跨小节、低音转位、新伴奏优先、人工覆盖/抑制/恢复、范围拖动吸附与绑定恢复、摘要/详情独立结果、专用字形及选中/播放/拖放/P 键盘/选区框对照。1000 小节/6000 音符实测：索引 26.47 ms、1000 缓存快照 1.95 ms、上下文 6.46 ms、数值帧 24.04 ms、基础色层定位 21.66 ms；1000 次标记高亮索引变化 0.703 ms，不含绘制。离线 JS 10000 切片约 1.9 秒，生产版本用 32 步/约 6 ms 预算分批构建，首次全谱分析仍有成本。历史数字与说明保留用于追溯；以当前版本说明为准。
'''
write(p,s)
# Publish only runtime files, not development fixtures/backups.
for p in base.iterdir():
    if p.suffix in ('.qml','.js') or p.name=='README.md':shutil.copy2(str(p),str(repo/'share/plugins/HarmonyAssistant'/p.name))
assert (repo/'personal/VERSION').read_text().strip()=='0.7.1'
write(repo/'personal/VERSION','0.8.0\n')
p=repo/'personal/docs/10-score-observer.md'
s=p.read_text(encoding='utf-8')+'''

## 0.8.0：区间输入、原生字形与状态颜色

contextSnapshot 新增每乐器当前踏板窗口、parts、scoreEnd；note descriptor 的 attackTick 沿反向 tie 链找到逻辑攻击起点，带循环保护。踏板窗口按乐器/起点排序并合并严格重叠范围，二分查找只传当前窗口，避免每帧携带全谱踏板。相邻抬/踩踏板边界仍分开。旧字段与接口保留；音乐推理仍在插件 Timeline.js，不在 libmscore 或音频侧。

固定标记使用独立 MasterScore 的样式副本和 Harmony::setHarmony/calculateBoundingRect/draw 记录 QPicture。先 checkChordList 支持尚无原生和弦的谱面；未知后缀不会加入用户谱的 ChordList。批次按文本/字体/缩放/颜色复用；渲染内容 SHA256 纳入 Entry 等价判断，防止同尺寸样式变更不重绘。degreeFont 单独配置，previewStatus 返回 hidden/fontFallback。冲突按实际高度逐个上移，最多六行，x 不改变；绝对页边界和原谱对象继续优先。

events.cpp 在 NORMAL、左键且无修饰键命中可见固定记号时激活，双击路径保留；编辑/foto 交还原生操作。ScoreView 音符预览调用原生 curColor(visible,override)，保持选中/播放/拖放/隐藏颜色，不改变 HPiano 或选区框实现。

插件 Timeline.js 的加权模板、区间/人工覆盖、Preferences.js 新显示模式以及 RangeEditor.qml 与宿主解耦。人工修正由既有配置接口保存，原生不理解其 JSON。schema 2 分析由插件处理，schema 1 兼容。实际回归和部署见 CHANGELOG 0.8.0；接口仍是 GUI 屏幕辅助，首次扫描/避让有成本。
''';write(p,s)
p=repo/'personal/docs/README.md';s=p.read_text(encoding='utf-8').replace('个人版本 0.5.0 提供通用播放观察','个人版本 0.8.0 提供区间输入元数据、原生和弦字形与状态颜色保护，以及通用播放观察');write(p,s)
p=repo/'personal/docs/04-feature-map.md';s=p.read_text(encoding='utf-8')+'''

0.8.0 和声区间：share/plugins/HarmonyAssistant/Timeline.js 是纯数值加权识别/人工范围，RangeEditor.qml 为手柄/精确 tick/独立历史，Preferences.js 配置单/多踏板与摘要/详情结果。attackTick 与踏板二分索引、私有 Harmony/QPicture 位于 scoreobserver.cpp；NotePreviewEntry 的字形等价与尺寸位于 notepreview.h；状态颜色优先级入口为 ScoreView::paint，单击接线 events.cpp。新回归在 tst_scoreobserver / tst_pluginhost，不修改音频、原生 P 键盘或选区框。
''';write(p,s)
print('Prepared 1.4 runtime/docs, native version 0.8.0')
