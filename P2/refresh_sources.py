"""Refresh only the P2 source index and documentation copies before applying."""
from pathlib import Path
import csv,io,shutil
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
index=R/'native/personal/docs/source-map.tsv'
rows=list(csv.DictReader(io.StringIO(index.read_text('utf8')),delimiter='\t'))
rows += [
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
