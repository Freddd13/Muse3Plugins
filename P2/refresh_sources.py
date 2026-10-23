"""Refresh only the P2 source index and documentation copies before applying."""
from pathlib import Path
import csv,io,shutil
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
index=R/'native/personal/docs/source-map.tsv'
rows=list(csv.DictReader(io.StringIO(index.read_text('utf8')),delimiter='\t'))
rows += [
 dict(topic="和弦独立面板样式",path="share/workflow/panels/HarmonyAssistant/HarmonyStyleEditor.qml",symbol="Column {",line="1",role="摘要与详情分别调整内容、音乐字体、排列及间距",tests="mtest/mscore/pluginhost/harmony_panel_077_tests.inc"),
 dict(topic="人工和弦随改音更新",path="share/workflow/panels/HarmonyAssistant/HarmonyAssistant.view.qml",symbol="function correctionStructure()",line="1",role="按小节与谱表结构判断人工范围，改音后保留解释",tests="mtest/mscore/pluginhost/harmony_panel_077_tests.inc"),
 dict(topic="人工和弦当前音符",path="share/workflow/panels/HarmonyAssistant/Timeline.js",symbol="function refreshNotes(",line="1",role="按范围与声部读取当前音符，保留用户指定的和弦",tests="mtest/mscore/pluginhost/harmony_panel_077_tests.inc"),
 dict(topic="完整谱试写保存",path="mscore/workflow/workflowexpression.cpp",symbol="QVariantMap ScoreObserver::saveWorkflowScore(",line="1",role="保存当前项目副本，更新文件校验及原生已保存状态",tests="mtest/mscore/pluginhost/variant_metadata_076_tests.inc"),
 dict(topic="插件控件识别",path="mscore/plugin/mscorePlugins.cpp",symbol="static bool personalSupportComponent(",line="1",role="元信息扫描跳过本项目公共界面控件，保留真实插件",tests="mtest/mscore/pluginhost/variant_metadata_076_tests.inc"),
 dict(topic="完整谱工作区迁移",path="share/plugins/ArrangementVariants/ArrangementVariants_MS3.qml",symbol="function saveAt(url)",line="1",role="另存索引时保持已有材料路径，保存切换与删除恢复",tests="mtest/mscore/pluginhost/variant_metadata_076_tests.inc"),
 dict(topic="谱行带位置与操作",path="mscore/performanceeditor/performanceoverlay.cpp",symbol="QRectF PerformanceEditor::scoreBandLane() const",line="1",role="选中谱行附近的可见位置、固定底部与窄行菜单",tests="mtest/mscore/pluginhost/score_editing_075_tests.inc;mtest/mscore/performanceeditor/performance_controls_tests.inc"),
 dict(topic="最近音滚轮",path="mscore/performanceeditor/performancewheel.cpp",symbol="bool PerformanceEditor::nearestWheelShortcut(",line="1",role="扩展开关、修饰键和最近可编辑音",tests="mtest/mscore/pluginhost/score_editing_075_tests.inc"),
 dict(topic="和弦范围手柄",path="mscore/workflow/chordeditor.cpp",symbol="QPointF pointFor(int tick) const",line="1",role="手柄固定到音乐范围，文字可独立拖动及避让",tests="mtest/mscore/pluginhost/harmony_display_075_tests.inc"),
 dict(topic="和弦显示延续",path="share/workflow/panels/HarmonyAssistant/Timeline.js",symbol="function displayAtTick(",line="1",role="保留上一和弦的显示，遵守人工排除范围",tests="../../muse3_plugins/HarmonyAssistant/tests/test-display-result.cjs"),
 dict(topic="分段写法删除",path="libmscore/regionalvariants.cpp",symbol="QVariantMap remove(",line="1",role="删除写法、整组与组合，保留当前谱面并一次撤销",tests="mtest/mscore/p1native/regional_070_tests.inc"),
 dict(topic="谱面按钮位置",path="libmscore/regionalvariants.cpp",symbol="QVariantMap setControlPlacement(",line="1",role="手动位置、单组显隐、随谱保存及撤销",tests="mtest/mscore/p1native/regional_070_tests.inc"),
 dict(topic="分段写法列表操作",path="mscore/workflow/regionalpanel.cpp",symbol="void removeSelected(",line="1",role="单击切换、明确当前写法、删除与恢复入口",tests="mtest/mscore/p1native/regional_070_tests.inc"),
 dict(topic="VST 音源与效果",path="mscore/workflow/vstpanel.cpp",symbol="void addVstPanelAction(",line="1",role="原生面板、扫描、预设、撤销和独立实例",tests="mtest/mscore/pluginhost/vst_tests.inc"),
 dict(topic="VST 音频图",path="audio/vst/rack.cpp",symbol="struct Rack::Impl",line="1",role="有界 MIDI 队列、串联效果、SF2 混合和延迟补偿",tests="../../muse3_plugins/P2/tests/vst/checks.cpp"),
 dict(topic="VST3 适配",path="audio/vst/vst3plugin.cpp",symbol="class Vst3Plugin",line="1",role="音频、MIDI、参数、状态和插件界面",tests="mtest/mscore/pluginhost/vst_tests.inc"),
 dict(topic="VST2 适配",path="audio/vst/vst2plugin.cpp",symbol="class Vst2Plugin",line="1",role="x64 ABI、CC、预设、CFX 和插件界面",tests="mtest/mscore/pluginhost/vst_tests.inc"),
 dict(topic="VST 独立进程",path="audio/vst/proxy.cpp",symbol="class Proxy",line="1",role="固定缓冲、独立扫描、进程退出和离线处理",tests="../../muse3_plugins/P2/tests/vst/checks.cpp"),
 dict(topic="SF2 单乐器效果",path="audio/vst/fluidsource.cpp",symbol="class FluidSource",line="1",role="按需创建发声实例，复用原生 SF2",tests="mtest/mscore/pluginhost/vst_tests.inc"),
 dict(topic="谱行锁定",path="mscore/workflow/systemlocks.cpp",symbol="QVariantMap changeSystemLocks(",line="1",role="分行范围、原生撤销、相邻行边界与解锁",tests="mtest/mscore/pluginhost/system_lock_tests.inc"),
 dict(topic="谱行锁定保存",path="libmscore/layoutbreak.cpp",symbol='xml.tag("kumoSystemLock"',line="1",role="常规分行符附带分组，插入小节后继续对应",tests="mtest/mscore/pluginhost/system_lock_tests.inc"),
 dict(topic="卷帘写音交互",path="mscore/performanceeditor/rollwritinginteraction.cpp",symbol="void RollWritingBar::begin(",line="1",role="画音、移动、复制、尾端和选择",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="卷帘写音转换",path="mscore/performanceeditor/rollnotation.cpp",symbol="QVariantMap buildRollEdit(",line="1",role="工作线程中的修改范围、声部、时值与连音组",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="卷帘草稿保存",path="mscore/performanceeditor/rollwritingmodel.cpp",symbol="void RollWritingBar::saveDraft(",line="1",role="草稿、试听、采用与撤销",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="频谱显示与颜色",path="mscore/performanceeditor/spectrumdisplay.cpp",symbol="QImage colorSpectrum(",line="1",role="颜色查表、显示增益、叠加透明度",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="频谱节拍操作",path="mscore/performanceeditor/spectrumbeat.cpp",symbol="SpectrumBeatControls::SpectrumBeatControls(",line="1",role="BPM、拍号、第一拍、候选和跟拍",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="频谱标注长度",path="mscore/performanceeditor/spectrumannotation.cpp",symbol="QVariantMap estimateSpectrumExtent(",line="1",role="估计亮线连续范围和常用记谱时值",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="频谱听辨均衡",path="mscore/referenceaudio/auditionfilter.cpp",symbol="AuditionFilter::AuditionFilter(",line="1",role="独立双声道均衡与选频听",tests="mtest/mscore/spectrum/tst_spectrum.cpp"),
 dict(topic="原曲速度估计",path="mscore/referenceaudio/tempoestimate.cpp",symbol="QVariantMap estimateTempo(",line="1",role="起音能量、周期与第一拍候选",tests="mtest/mscore/spectrum/tst_spectrum.cpp"),
 dict(topic="实时录制对应",path="mscore/workflow/realtimematcher.h",symbol="class RealtimeMatcher",line="1",role="音高集合与起音间隔的有限路径匹配",tests="mtest/mscore/p1native/tst_p1native.cpp"),
 dict(topic="表达精确选区",path="mscore/workflow/workflowexpression.cpp",symbol="QVariantMap ScoreObserver::expressionSelection",line="1",role="保留所选拍位与谱表范围",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="表达目标与输入",path="share/workflow/panels/PerformanceExpression/ExpressionScopeBar.qml",symbol="ColumnLayout {",line="1",role="目标谱段、设备开关与录制位置",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic='节拍音符字体兼容',path='libmscore/textbase.cpp',symbol='if (family == "Leland Text")',line='1',role='默认节拍字形采用3.6.2尺寸；其它符号和自选字体保留',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp;../../muse3_plugins/P2/compare_fonts.py'),
 dict(topic='工作视图',path='mscore/workflow/workspaceviews.cpp',symbol='class WorkspaceViews',line='1',role='四种布局、DAW谱面对照、共用动作工具栏及返回乐谱',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='独立编辑区域',path='mscore/workflow/editorareas.cpp',symbol='class EditorAreas',line='1',role='悬浮、右侧停靠、放回与各视图的区域保存',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='原曲滑块输入',path='share/workflow/panels/WorkflowCommon/SliderNumber.qml',symbol='RowLayout {',line='1',role='原生滑块与数值输入',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic="给定音高写节奏",path="mscore/performanceeditor/rhythmpane.cpp",symbol="RhythmPane::RhythmPane(",line="1",role="录制、导入、拖动草稿、试听和采用",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="节奏音序与时值",path="share/plugins/PerformanceExpression/Rhythm.js",symbol="function build(",line="1",role="给定音高、漏敲多敲、休止与连音组",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp;../../muse3_plugins/PerformanceExpression/tests/test-rhythm.cjs"),
 dict(topic="MIDI录音目录",path="mscore/workflow/midicapture.cpp",symbol='const QString folder=QSettings().value("workflow/recordingDirectory"',line="1",role="沿用录制，默认写入E盘",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="传统编配建议任务",path="mscore/workflow/localsuggestions.cpp",symbol="void LocalSuggestionTask::start(",line="1",role="分批读取、可取消音乐规则和原生候选",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="指法与配音规则",path="share/plugins/ArrangementAssistant/Suggestions.js",symbol="function generate(",line="1",role="连续按键、指法、换手和对位候选",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic='AI任务范围',path='mscore/workflow/arrangementreader.cpp',symbol='QVariantMap ScoreObserver::arrangementState(',line='1',role='内存谱、版本、准确选区和共同资料',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='AI分批读取',path='mscore/workflow/arrangementreader.cpp',symbol='QVariantMap ScoreObserver::arrangementRange(',line='1',role='声部、精确时值、连线和演奏数据',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='MCP关闭处理',path='mscore/workflow/arrangementreader.cpp',symbol='void ScoreObserver::prepareLocalBridge(',line='1',role='应用关闭时释放网络默认配置',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='局部编配候选',path='mscore/workflow/arrangementoptions.cpp',symbol='QVariantMap arrangementOperation(',line='1',role='副本检查、采用、保存写法与操作结果',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='编配建议面板',path='mscore/workflow/suggestionpanel.cpp',symbol='void showSuggestionPanel(',line='1',role='原生差异、定位、试听和采用',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='频谱分段计算',path='mscore/referenceaudio/spectrum.cpp',symbol='SpectrumTile spectrum(',line='1',role='Hann 窗、各声道能量、对数音高、分段读取',tests='mtest/mscore/spectrum/tst_spectrum.cpp'),
 dict(topic='频谱任务与缓存',path='mscore/referenceaudio/spectrumsession.cpp',symbol='void ReferenceSpectrumSession::request(',line='1',role='取消旧任务、有界缓存、独立工作线程',tests='mtest/mscore/spectrum/tst_spectrum.cpp'),
 dict(topic='扒谱交互',path='mscore/performanceeditor/spectrumpane.cpp',symbol='SpectrumPane::SpectrumPane(',line='1',role='原曲片段、取音、音符输入、上下与叠加',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='扒谱标注保存',path='mscore/performanceeditor/spectrumpane.cpp',symbol='void SpectrumPane::saveMarks(',line='1',role='频率与音名、原生撤销、MSCZ 元数据',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
]
rows += [
 dict(topic='频谱时间范围',path='mscore/performanceeditor/spectrumpane.cpp',symbol='void SpectrumPane::fitTimeRange(',line='1',role='完整音频与按谱片段、匹配显示、逐音轨选择保存',tests='mtest/mscore/pluginhost/spectrum_078_tests.inc'),
 dict(topic='圆滑线共同参考曲线',path='libmscore/freeslur.cpp',symbol='std::array<QPointF,4> SlurSegment::freeBaseControls(',line='1',role='中间节点点位、锁定与整理共用参考坐标',tests='mtest/mscore/performanceeditor/engraving_085_tests.inc'),
 dict(topic='圆滑线切线整理',path='libmscore/freeslur.cpp',symbol='bool FreeSlur::smoothNode(',line='1',role='保持可见节点，按邻点间距整理切线',tests='mtest/mscore/performanceeditor/engraving_085_tests.inc'),
 dict(topic='圆滑线连续绕行',path='libmscore/freeslurrouting.cpp',symbol='RoutingCandidate smoothRouting(',line='1',role='比较整段形状、避让边界与共同切线，固定人工节点',tests='mtest/mscore/performanceeditor/engraving_085_tests.inc'),
 dict(topic='圆滑线独立端点',path='libmscore/freeslurendpoints.cpp',symbol='std::array<QPointF,4> SlurSegment::freeDrawingControls(',line='1',role='复用原生符干和符杠端点，独立保存位置和切线',tests='mtest/mscore/performanceeditor/endpoints_085_tests.inc'),
 dict(topic='共同时间缩放',path='mscore/performanceeditor/performanceinteraction.cpp',symbol='void PerformanceEditor::zoomTimeline(',line='1',role='卷帘和频谱共用缩放中心与时间滚动范围',tests='mtest/mscore/pluginhost/spectrum_078_tests.inc'),
 dict(topic='原曲时间叠加缩放',path='mscore/performanceeditor/spectrumpane.cpp',symbol='void SpectrumPane::editorTimelineZoomed(',line='1',role='全曲、选区、参数区与卷帘共用叠加缩放，保留浏览时刻',tests='mtest/mscore/pluginhost/spectrum_078_tests.inc'),
]
rows += [
 dict(topic='独立工具与当前页',path='mscore/workflow/editorareas.cpp',symbol='void keepInlinePage(',line='1',role='唤回独立工具时保留当前编辑器页，恢复导航和时间滚动',tests='mtest/mscore/pluginhost/layout_079_tests.inc'),
 dict(topic='写节奏紧凑操作',path='mscore/performanceeditor/rhythmpane.cpp',symbol='RhythmPane::RhythmPane(',line='1',role='录制、细分、试听与采用按自然宽度排列及换行',tests='mtest/mscore/pluginhost/layout_079_tests.inc'),
 dict(topic='表达结果选音',path='mscore/workflow/workflowexpression.cpp',symbol='QVariantMap ScoreObserver::selectExpressionNote(',line='1',role='对应列表与原生选音同步，播放中保持拍位并更新采用数量',tests='mtest/mscore/performanceeditor/expression_080_tests.inc'),
 dict(topic='录完直接看结果',path='share/workflow/panels/PerformanceExpression/PerformanceExpression.view.qml',symbol=' function revealResults()',line='1',role='录制与导入后显示试听、采用和逐音结果；保留手动浏览',tests='mtest/mscore/performanceeditor/expression_080_tests.inc'),
 dict(topic='工具内容高度',path='mscore/workflow/editorareas.cpp',symbol='void ensureEditorDockContent(',line='1',role='根据当前内容补足最小空间，保留用户调整的较大编辑器',tests='mtest/mscore/pluginhost/layout_079_tests.inc'),
 dict(topic='工作视图初始显示',path='mscore/workflow/workspaceviews.cpp',symbol='void activate(',line='1',role='首次雕版与DAW收起输入工具，保存布局继续恢复',tests='mtest/mscore/pluginhost/layout_079_tests.inc'),
]
rows += [
 dict(topic='导出音长的撤销',path='mscore/midicrop/gatehistory.cpp',symbol='void MidiCropPanel::changeRelease(',line='1',role='每份谱独立记录松手和排除，一次手势一次撤销，保留乐谱撤销',tests='mtest/mscore/performanceeditor/midi_gate_086_tests.inc'),
 dict(topic='导出音长对比',path='mscore/midicrop/midicroppanel.cpp',symbol='void MidiCropPanel::compare()',line='1',role='紧凑分组、可调图表与列表、共同试听和返回导出',tests='mtest/mscore/performanceeditor/midi_gate_086_tests.inc;mtest/mscore/performanceeditor/midi_transport_086_tests.inc'),
 dict(topic='导出音长图表',path='mscore/midicrop/gateroll.inc',symbol='class GateRoll final',line='1',role='原新长度、折叠音高、通道踏板、缩放和当前时间定位',tests='mtest/mscore/performanceeditor/midi_gate_086_tests.inc'),
]
rows += [
 dict(topic='节奏草稿连续采用',path='mscore/performanceeditor/rhythmpane.cpp',symbol='void RhythmPane::operate(',line='1',role='采用后重新读取、等待计算后执行、试听状态与原生撤销',tests='mtest/mscore/performanceeditor/writing_087_tests.inc'),
 dict(topic='节奏草稿局部撤销',path='mscore/performanceeditor/rhythmpane.cpp',symbol='void RhythmPane::commitRows(',line='1',role='一次拖动或表格编辑一次撤销，恢复草稿及采用状态',tests='mtest/mscore/performanceeditor/writing_087_tests.inc'),
 dict(topic='节奏的逐音保持',path='share/plugins/PerformanceExpression/Rhythm.js',symbol='function voiceEvents(',line='1',role='保留休止、各音延音与力度，按交叠区间写延音和休止',tests='mtest/mscore/performanceeditor/writing_087_tests.inc;../../muse3_plugins/PerformanceExpression/tests/test-rhythm-preservation.cjs'),
 dict(topic='卷帘草稿删除',path='mscore/performanceeditor/rollwritingmodel.cpp',symbol='void RollWritingBar::discardDraft(',line='1',role='只删除当前范围的草稿，原生撤销及保存恢复',tests='mtest/mscore/performanceeditor/writing_087_tests.inc'),
]
seen=set();result=[]
for row in rows:
 key=(row['path'],row['symbol'])
 if key in seen:continue
 seen.add(key);file=R/'native'/row['path']
 if not file.exists():file=H/row['path']
 if file.exists() and row['symbol']!='-':
  lines=[i+1 for i,s in enumerate(file.read_text('utf8',errors='replace').splitlines()) if row['symbol'] in s]
  if lines:row['line']=str(min(lines,key=lambda n:abs(n-int(row['line']))))
 result.append(row)
out=io.StringIO();writer=csv.DictWriter(out,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(result);index.write_bytes(out.getvalue().encode('utf8'))
for name in ('transcription-separate-059.png','transcription-overlay-059.png','arrangement-options-060.png','traditional-suggestions-061.png','rhythm-writing-062.png'):
 source=R.parent/'P1/out/final-regression'/name
 if source.exists():
  for folder in (R/'docs/images',R/'native/personal/docs/images'):
   folder.mkdir(parents=True,exist_ok=True)
   if not (folder/name).exists():shutil.copyfile(source,folder/name)
print('Updated',len(result),'source entries and spectrum screenshots')
