# coding: utf-8
"""Apply owned additions; never run earlier release installers over newer code."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent
PLUGINS=ROOT.parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def patch(path,old,new):
 p=HOST/path;s=p.read_text(encoding='utf8')
 if new in s:return
 if s.count(old)!=1:raise RuntimeError('Cannot identify edit in '+path+': '+old[:55])
 p.write_bytes(s.replace(old,new).encode('utf8'))
def apply():
 state_path=ROOT/'out/applied-native.json';state_path.parent.mkdir(parents=True,exist_ok=True)
 previous=json.loads(state_path.read_text(encoding='utf8')) if state_path.exists() else {}
 pending=[(src,HOST/src.relative_to(ROOT/'native')) for src in (ROOT/'native').rglob('*') if src.is_file()]
 excluded=set()
 for i,arg in enumerate(sys.argv[:-1]):
  if arg=='--exclude-plugin':excluded.add(sys.argv[i+1])
 plugin_names=[name for name in ['ReferencePlayer','PerformanceExpression','ArrangementVariants','ArrangementAssistant','HarmonyAssistant','WorkflowCommon'] if name not in excluded]
 for name in plugin_names:
  pending.extend((src,HOST/'share/plugins'/name/src.name) for src in (PLUGINS/name).glob('*') if src.is_file() and src.suffix in ('.qml','.js','.md'))
 # Check all destinations before writing anything. A second task's edits must
 # be merged deliberately rather than overwritten by a local source mirror.
 for src,dst in pending:
  key=dst.relative_to(HOST).as_posix()
  if not dst.exists() or dst.read_bytes()==src.read_bytes():continue
  current=hashlib.sha256(dst.read_bytes()).hexdigest()
  if key in previous:
   if current!=previous[key]:raise RuntimeError('另一个任务修改了 '+key+'；请先合并这份修改。')
  else:
   committed=subprocess.run(['git','show','HEAD:'+key],cwd=str(HOST),capture_output=True)
   if committed.returncode or committed.stdout!=dst.read_bytes():raise RuntimeError('目标文件有尚未核对的修改：'+key)
 for src in (ROOT/'native').rglob('*'):
  if src.is_file():
   dst=HOST/src.relative_to(ROOT/'native');dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists() or dst.read_bytes()!=src.read_bytes():dst.write_bytes(src.read_bytes())
 p=HOST/'mscore/plugin/api/scoreobserver.h';s=p.read_text(encoding='utf8')
 declarations=['      Q_INVOKABLE QVariantMap stopWorkflowPlayback();','      Q_INVOKABLE QVariantMap referencePlan(const QVariantMap&);','      Q_INVOKABLE QVariantMap startReferencePlayback(const QVariantMap&);','      Q_INVOKABLE QVariantMap stopReferencePlayback();','      Q_INVOKABLE QVariantMap setEditorComparison(const QVariantMap&);','      Q_INVOKABLE QVariantMap setReferenceTracks(const QVariantList&);']
 s='\n'.join(line for line in s.splitlines() if line not in declarations)+'\n'
 anchor='      Q_INVOKABLE QVariantMap workflowStatus();'
 if s.count(anchor)!=1:raise RuntimeError('Workflow declarations changed')
 s=s.replace(anchor,anchor+'\n'+'\n'.join(declarations))
 if p.read_bytes()!=s.encode('utf8'):p.write_bytes(s.encode('utf8'))
 patch('mscore/plugin/plugin.cmake','    ${CMAKE_CURRENT_LIST_DIR}/api/readonlyanalysisjob.cpp','    ${CMAKE_CURRENT_LIST_DIR}/api/readonlyanalysisjob.cpp\n    ${CMAKE_CURRENT_LIST_DIR}/api/pianohandanalysis.h\n    ${CMAKE_CURRENT_LIST_DIR}/api/pianohandanalysis.cpp')
 if 'handbracket.cpp handbracket.h tempotext.cpp' in (HOST/'libmscore/CMakeLists.txt').read_text(encoding='utf8'):
  patch('libmscore/CMakeLists.txt','handbracket.cpp handbracket.h tempotext.cpp','handbracket.cpp handbracket.h handbracketanalysis.cpp tempotext.cpp')
 patch('libmscore/CMakeLists.txt','system.cpp stringdata.cpp tempotext.cpp text.cpp','system.cpp stringdata.cpp handbracket.cpp handbracket.h handbracketanalysis.cpp tempotext.cpp text.cpp')
 patch('libmscore/symbol.h','      QPointF _handDragOriginal;','      QPointF _handDragOriginal;\n      QPointF _handBase;\n      bool _handBaseValid=false,_handLegacyAnchor=false;')
 patch('libmscore/symbol.h','      bool _handBaseValid=false,_handLegacyAnchor=false;','      bool _handBaseValid=false,_handLegacyAnchor=false;\n      bool _handGeometryEdited=false;')
 patch('mscore/CMakeLists.txt','      inputnotationmenu.h inputnotationmenu.cpp temposymbols.h temposymbols.cpp','      inputnotationmenu.h inputnotationmenu.cpp temposymbols.h temposymbols.cpp handbracketsettings.h handbracketsettings.cpp')
 patch('mscore/menus.cpp','#include "temposymbols.h"','#include "temposymbols.h"\n#include "handbracketsettings.h"')
 patch('mscore/menus.cpp','      for (auto id : {SymId::keyboardPlayWithLH,SymId::keyboardPlayWithRH}) {','      loadHandBracketDefaults();\n      for (auto id : {SymId::keyboardPlayWithLH,SymId::keyboardPlayWithRH}) {')
 patch('mscore/menus.cpp','            sp->append(symbol,id==SymId::keyboardPlayWithLH ? QT_TRANSLATE_NOOP("Palette", "左手弹（可伸缩）") : QT_TRANSLATE_NOOP("Palette", "右手弹（可伸缩）"));','            sp->append(symbol,id==SymId::keyboardPlayWithLH ? QT_TRANSLATE_NOOP("Palette", "左手弹（可伸缩）") : QT_TRANSLATE_NOOP("Palette", "右手弹（可伸缩）"),QString(),.65);')
 patch('mscore/menus.cpp','      return sp;\n      }\n\n//---------------------------------------------------------\n//   newTremoloPalettePanel','      completeHandBracketPalette(sp);\n      return sp;\n      }\n\n//---------------------------------------------------------\n//   newTremoloPalettePanel')
 patch('mscore/palette/palettetree.cpp','#include "../temposymbols.h"','#include "../temposymbols.h"\n#include "../handbracketsettings.h"')
 patch('mscore/palette/palettetree.cpp','      appendPlayableTempoSymbols(this);','      appendPlayableTempoSymbols(this);\n      completeHandBracketPalette(this);')
 patch('mscore/inspector/inspector.cpp','#include "freeslurinspector.h"','#include "freeslurinspector.h"\n#include "../handbracketsettings.h"')
 patch('mscore/inspector/inspector.cpp','      mapSignals({h,v,width,{Pid::HAND_BRACKET_MODE,0,_mode,nullptr},{Pid::HAND_BRACKET_TEXT,0,text,nullptr}},{});','      addHandBracketDefaultControls(host,grid,inspector);\n      mapSignals({h,v,width,{Pid::HAND_BRACKET_MODE,0,_mode,nullptr},{Pid::HAND_BRACKET_TEXT,0,text,nullptr}},{});')
 patch('libmscore/CMakeLists.txt','slur.cpp freeslur.cpp tie.cpp','slur.cpp freeslur.cpp freesluravoidance.cpp tie.cpp')
 patch('libmscore/CMakeLists.txt','undo.cpp cmd.cpp scorefile.cpp revisions.cpp','undo.cpp cmd.cpp scorefile.cpp regionalvariants.cpp regionalvariants.h revisions.cpp')
 p=HOST/'libmscore/CMakeLists.txt';s=p.read_text(encoding='utf8');s=s.replace('set_source_files_properties(regionalvariants.cpp scorefile.cpp PROPERTIES COMPILE_FLAGS "/utf-8")','set_source_files_properties(regionalvariants.cpp scorefile.cpp PROPERTIES COMPILE_FLAGS "/execution-charset:utf-8")');encoding='\nif(MSVC)\n  set_source_files_properties(regionalvariants.cpp scorefile.cpp PROPERTIES COMPILE_FLAGS "/execution-charset:utf-8")\nendif()\n'
 if encoding not in s:s+=encoding
 if p.read_bytes()!=s.encode('utf8'):p.write_bytes(s.encode('utf8'))
 patch('libmscore/property.h','      HAND_BRACKET_TEXT,','      HAND_BRACKET_TEXT,\n      FREE_SLUR_AUTO,')
 patch('libmscore/property.cpp','      { Pid::HAND_BRACKET_TEXT, P_TYPE::BOOL, true, "handBracketText", "hand bracket label" },','      { Pid::HAND_BRACKET_TEXT, P_TYPE::BOOL, true, "handBracketText", "hand bracket label" },\n      { Pid::FREE_SLUR_AUTO, P_TYPE::BOOL, true, "freeSlurAuto", "free slur automatic avoidance" },')
 patch('libmscore/slur.h','      bool _freeMode = false;','      bool _freeMode = false;\n      bool _freeAuto = false;')
 patch('libmscore/slur.h','      QVector<FreeGrips> _freeGrips;','      QVector<FreeGrips> _freeGrips;\n      QVector<FreeSlur::CurvePoint> _freeCurvePoints;')
 patch('libmscore/slur.h','      bool _freeDragging = false;','      bool _freeDragging = false;\n      int _freeCollisions = 0;\n      bool _freeLimited = false;')
 patch('libmscore/slur.h','      bool edit(EditData&) override;','      bool edit(EditData&) override;\n      bool displayedFreeNode(int index,FreeSlurNode*) const;\n      bool displayedFreeNode(double position,FreeSlurNode*) const;')
 patch('libmscore/slur.h','      bool isEdited() const;','      bool isEdited() const;\n      int freeCollisions() const { return _freeCollisions; }\n      bool freeLimited() const { return _freeLimited; }')
 patch('libmscore/slur.h','      bool freeMode() const { return _freeMode; }','      bool freeMode() const { return _freeMode; }\n      bool freeAuto() const { return _freeAuto; }')
 patch('libmscore/slur.cpp','      _freeGrips.clear();','      _freeGrips.clear();_freeCurvePoints.clear();')
 patch('libmscore/slur.cpp','!(slur()->freeMode() && !slur()->freeNodes().isEmpty())','!(slur()->freeMode() && (slur()->freeAuto() || !slur()->freeNodes().isEmpty()))')
 patch('libmscore/slur.cpp','      _freeMode=s._freeMode; _freeNodes=s._freeNodes; _freeData=s._freeData;','      _freeMode=s._freeMode; _freeAuto=s._freeAuto; _freeNodes=s._freeNodes; _freeData=s._freeData;')
 patch('libmscore/slur.cpp','      writeProperty(xml,Pid::FREE_SLUR_NODES);','      writeProperty(xml,Pid::FREE_SLUR_NODES);\n      writeProperty(xml,Pid::FREE_SLUR_AUTO);')
 patch('libmscore/slur.cpp','      if(e.name()==propertyName(Pid::FREE_SLUR_NODES)) {readProperty(e,Pid::FREE_SLUR_NODES);return true;}','      if(e.name()==propertyName(Pid::FREE_SLUR_NODES)) {readProperty(e,Pid::FREE_SLUR_NODES);return true;}\n      if(e.name()==propertyName(Pid::FREE_SLUR_AUTO)) {readProperty(e,Pid::FREE_SLUR_AUTO);return true;}')
 patch('mscore/dragdrop.cpp','#include "scoreview.h"','#include "scoreview.h"\n#include "temposymbols.h"')
 patch('mscore/dragdrop.cpp','      if (editData.dropElement) {\n            bool firstStaffOnly = false;','      if (editData.dropElement && isPlayableTempoSymbol(editData.dropElement)) {\n            const bool changed=applyPlayableTempoDrop(editData.dropElement,pos);\n            delete editData.dropElement;editData.dropElement=nullptr;setDropTarget(nullptr);\n            if(changed)event->acceptProposedAction();else event->ignore();\n            if(noteEntryMode())moveCursor();return;\n            }\n      if (editData.dropElement) {\n            bool firstStaffOnly = false;')
 patch('mscore/CMakeLists.txt','      inputnotationmenu.h inputnotationmenu.cpp','      inputnotationmenu.h inputnotationmenu.cpp temposymbols.h temposymbols.cpp')
 patch('mscore/menus.cpp','#include "menus.h"','#include "menus.h"\n#include "temposymbols.h"')
 patch('mscore/menus.cpp','      sp->setMoreElements(false);\n\n      return sp;\n      }\n\n//---------------------------------------------------------\n//   newTextPalettePanel','      appendPlayableTempoSymbols(sp);\n      sp->setMoreElements(false);\n\n      return sp;\n      }\n\n//---------------------------------------------------------\n//   newTextPalettePanel')
 patch('mscore/palette/palettetree.cpp','#include "palettetree.h"','#include "palettetree.h"\n#include "../temposymbols.h"')
 patch('mscore/palette/palettetree.cpp','      if (_type == Type::Unknown)\n            _type = guessType();','      if (_type == Type::Unknown)\n            _type = guessType();\n      appendPlayableTempoSymbols(this);')
 patch('mscore/palette.cpp','#include "palette.h"','#include "palette.h"\n#include "temposymbols.h"')
 patch('mscore/palette.cpp','      if (element->isSpanner())\n            TourHandler::startTour("spanner-drop-apply");','      if (isPlayableTempoSymbol(element))\n            return applyPlayableTempoSymbol(element);\n      if (element->isSpanner())\n            TourHandler::startTour("spanner-drop-apply");')
 patch('libmscore/CMakeLists.txt','noteentry.cpp inputrhythm.cpp inputrhythm.h','noteentry.cpp inputrhythm.cpp inputrhythm.h inputnotation.cpp inputnotation.h')
 patch('libmscore/layout.cpp','#include "beam.h"','#include "beam.h"\n#include "inputnotation.h"')
 patch('libmscore/layout.cpp','                  prev = cr;','                  if ((bm == Beam::Mode::BEGIN || bm == Beam::Mode::AUTO) && InputNotation::joinTiedChords(prev,cr)) bm = Beam::Mode::MID;\n                  prev = cr;')
 patch('libmscore/layout.cpp','            }\n      }\n\nstatic bool measureMayHaveBeamsJoinedIntoNext','            }\n      InputNotation::coordinateTieStems(measure);\n      }\n\nstatic bool measureMayHaveBeamsJoinedIntoNext')
 patch('mscore/CMakeLists.txt','      midicrop/midicroppanel.h midicrop/midicroppanel.cpp','      midicrop/midicroppanel.h midicrop/midicroppanel.cpp\n      inputnotationmenu.h inputnotationmenu.cpp')
 patch('mscore/preferences.cpp','{PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM,                    new BoolPreference(true, false)},','{PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM,                    new BoolPreference(true, false)},\n            {PREF_SCORE_TIED_BEAMS, new BoolPreference(false, false)},\n            {PREF_SCORE_COHERENT_TIE_STEMS, new BoolPreference(true, false)},')
 patch('mscore/musescore.cpp','#include "inputrhythmpreference.h"','#include "inputrhythmpreference.h"\n#include "inputnotationmenu.h"\n#include "libmscore/inputnotation.h"')
 patch('mscore/musescore.cpp','      InputRhythm::setEnabled(preferences.getBool(PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM));','      InputRhythm::setEnabled(preferences.getBool(PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM));\n      InputNotation::setTiedBeams(preferences.getBool(PREF_SCORE_TIED_BEAMS));\n      InputNotation::setCoherentStems(preferences.getBool(PREF_SCORE_COHERENT_TIE_STEMS));')
 patch('mscore/musescore.cpp','      menuTools->addAction(getAction("resequence-rehearsal-marks"));','      addInputNotationMenu(menuTools);\n      menuTools->addAction(getAction("resequence-rehearsal-marks"));')
 patch('mscore/CMakeLists.txt','      taptempo/taptempo.h taptempo/taptempo.cpp','      taptempo/taptempo.h taptempo/taptempo.cpp taptempo/tapmark.h taptempo/tapmark.cpp')
 patch('mscore/CMakeLists.txt','      scoreview.cpp editharmony.cpp editfiguredbass.cpp events.cpp','      scoreview.cpp workflow/chordoverlay.cpp editharmony.cpp editfiguredbass.cpp events.cpp')
 patch('mscore/scoreview.h','      QRectF previewEditBounds() const;','      QRectF previewEditBounds() const;\n      void paintTopChordPreview(QPainter&);')
 patch('mscore/scoreview.cpp','      PerformanceEditor::paintForView(this, vp);','      PerformanceEditor::paintForView(this, vp);\n      paintTopChordPreview(vp);')
 patch('mscore/scoreview.cpp','if (!box.intersects(fr) || box.intersects(protectedArea)) return;','if (entry.onTop || !box.intersects(fr) || box.intersects(protectedArea)) return;')
 patch('mscore/plugin/qmlplugin.cpp','#include <QTimer>','#include <QTimer>\n#include <QStyle>')
 patch('mscore/plugin/qmlplugin.cpp','qBound(80,preferred,400)','qBound(40,preferred,400)+(property("ribbonContentHeight").toBool()?_panelDock->style()->pixelMetric(QStyle::PM_TitleBarHeight):0)')
 patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.h','    ${PROJECT_SOURCE_DIR}/mscore/workflow/paneldock.h\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/paneldock.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.h')
 patch('mscore/plugin/mscorePlugins.cpp','#include "qmlplugin.h"','#include "qmlplugin.h"\n#include "mscore/workflow/paneldock.h"')
 patch('mscore/plugin/mscorePlugins.cpp','                  addDockWidget(area, dock);\n                  p->attachPanelDock(dock);','                  addDockWidget(area, dock);\n                  const bool restored=arrangeWorkflowDock(this,dock,QFileInfo(pp).completeBaseName(),p->property("preferredPanelGroup").toString(),area);\n                  p->attachPanelDock(dock);')
 patch('mscore/plugin/mscorePlugins.cpp','                  resizeDocks({ dock }, { size }, orientation);','                  if(!restored)resizeDocks({ dock }, { size }, orientation);')
 patch('mscore/plugin/qmlplugin.cpp','#include "qmlplugin.h"','#include "qmlplugin.h"\n#include "mscore/workflow/paneldock.h"')
 patch('mscore/plugin/qmlplugin.cpp','_detailDock->setObjectName("pluginDetailDock");','_detailDock->setObjectName(_panelDock->objectName()+"/details");')
 patch('mscore/plugin/qmlplugin.cpp','_detailWindow->setObjectName("pluginDetailWindow");','_detailWindow->setObjectName(_panelDock->objectName()+"/detailWindow");')
 patch('mscore/plugin/qmlplugin.cpp','            main->resizeDocks({_detailDock.data()},{360},Qt::Horizontal);','            const bool restored=arrangeWorkflowDock(main,_detailDock,_panelDock->objectName()+"/details",property("preferredPanelGroup").toString(),Qt::RightDockWidgetArea);\n            if(!restored)main->resizeDocks({_detailDock.data()},{360},Qt::Horizontal);')
 patch('mscore/plugin/api/scoreobserver.h','      Q_INVOKABLE QVariantMap workflowStatus();','      Q_INVOKABLE QVariantMap workflowStatus();\n      Q_INVOKABLE QVariantMap stopWorkflowPlayback();')
 patch('mscore/workflow/scoreworkflow.cpp','QVariantMap ScoreObserver::workflowStatus() {','QVariantMap ScoreObserver::stopWorkflowPlayback() {\n if(seq&&seq->isPlaying())seq->stopWait();\n if(seq&&(!seq->backgroundRenderingIdle()||seq->isPlaying()))return {{"error","waiting for stop/render"}};\n return {{"ok",true}};\n}\nQVariantMap ScoreObserver::workflowStatus() {')
 patch('mscore/workflow/scoreworkflow.cpp',' if(element){_score->select(element,SelectType::SINGLE,track/VOICES);view->adjustCanvasPosition(element,false);}',' if(range.contains("index")){auto note=resolve(range);if(!note)return {{"error","stale note; read the score again"}};element=note;}\n if(element){_score->select(element,SelectType::SINGLE,track/VOICES);view->adjustCanvasPosition(element,false);}')
 if 'workflow/referencebus.cpp' not in (HOST/'mscore/CMakeLists.txt').read_text(encoding='utf8'):
  patch('mscore/CMakeLists.txt','      seq.cpp textpalette.cpp','      seq.cpp workflow/referencebus.cpp workflow/referencebus.h textpalette.cpp')
 patch('mscore/CMakeLists.txt','      seq.cpp workflow/referencebus.cpp workflow/referencebus.h textpalette.cpp','      seq.cpp workflow/referencebus.cpp workflow/referencebus.h workflow/workflowcontext.cpp workflow/workflowcontext.h textpalette.cpp')
 patch('mscore/CMakeLists.txt','    include(${CMAKE_CURRENT_LIST_DIR}/plugin/plugin.cmake)\nendif (SCRIPT_INTERFACE)','    include(${CMAKE_CURRENT_LIST_DIR}/plugin/plugin.cmake)\nelse (SCRIPT_INTERFACE)\n    set(PLUGIN_API_SRC ${CMAKE_CURRENT_LIST_DIR}/workflow/referencefactory.cpp ${CMAKE_CURRENT_LIST_DIR}/workflow/referencefactory.h)\nendif (SCRIPT_INTERFACE)')
 patch('mscore/performanceeditor/performanceeditor.cmake','      ${CMAKE_CURRENT_LIST_DIR}/envelopepreview.cpp','      ${CMAKE_CURRENT_LIST_DIR}/envelopepreview.cpp\n      ${CMAKE_CURRENT_LIST_DIR}/workflowlanes.h\n      ${CMAKE_CURRENT_LIST_DIR}/workflowlanes.cpp')
 patch('mscore/plugin/api/qmlpluginapi.h','      Q_INVOKABLE QObject* newReferenceProject();','      Q_INVOKABLE QObject* newReferenceProject();\n      Q_INVOKABLE QObject* newWorkflowContext();')
 patch('mscore/plugin/api/qmlpluginapi.cpp','#include "mscore/workflow/referencefactory.h"','#include "mscore/workflow/referencefactory.h"\n#include "mscore/workflow/workflowcontext.h"')
 patch('mscore/plugin/api/qmlpluginapi.cpp','QObject* PluginAPI::newReferenceProject() { return Ms::referenceProject(); }','QObject* PluginAPI::newReferenceProject() { return Ms::referenceProject(); }\nQObject* PluginAPI::newWorkflowContext() { return Ms::workflowContext(); }')
 patch('mscore/plugin/api/scoreobserver.h','      Q_INVOKABLE QVariantMap stopReferencePlayback();','      Q_INVOKABLE QVariantMap stopReferencePlayback();\n      Q_INVOKABLE QVariantMap setEditorComparison(const QVariantMap&);')
 patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.cpp','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/referenceworkflow.cpp')
 p=HOST/'mscore/shortcut.cpp';s=p.read_text(encoding='utf8')
 if '"reference-audio-play"' not in s:
  at=s.index('"tap-tempo",');end=s.index('},',at)+2
  additions=''
  for name,label,description in [('reference-audio-play','播放／停止选定原曲片段','在原曲参考中选择音轨和片段后，独立播放音频'),('reference-joint-play','联合播放／停止','按照原曲参考里选定的方式播放乐谱和参加播放的音轨')]:
   additions+='\n        {\n           MsWidget::MAIN_WINDOW,\n           STATE_NORMAL | STATE_NOTE_ENTRY | STATE_PLAY,\n           "'+name+'",\n           QT_TRANSLATE_NOOP("action","'+label+'"),\n           QT_TRANSLATE_NOOP("action","'+label+'"),\n           QT_TRANSLATE_NOOP("action","'+description+'"),\n           Icons::play_ICON\n           },'
  p.write_bytes((s[:end]+additions+s[end:]).encode('utf8'))
 patch('mscore/musescore.cpp','#include "inputnotationmenu.h"','#include "inputnotationmenu.h"\n#include "workflow/referencefactory.h"')
 patch('mscore/musescore.cpp','      menuTools->addAction(getAction("tap-tempo"));','      menuTools->addAction(getAction("tap-tempo"));\n      addReferenceActions(menuTools);')
 patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referenceworkflow.cpp','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referenceworkflow.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalpanel.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalpanel.h')
 patch('mscore/musescore.cpp','#include "workflow/referencefactory.h"','#include "workflow/referencefactory.h"\n#include "workflow/regionalpanel.h"')
 patch('mscore/musescore.cpp','      QString cmdn(a->data().toString());','      QString cmdn(a->data().toString());\n#ifdef SCRIPT_INTERFACE\n      if(cmdn=="regional-variants"){showRegionalVariantPanel();return;}\n#endif')
 patch('mscore/musescore.cpp','      addReferenceActions(menuTools);','      addReferenceActions(menuTools);\n#ifdef SCRIPT_INTERFACE\n      addRegionalVariantAction(menuTools);\n#endif')
 p=HOST/'mscore/shortcut.cpp';s=p.read_text(encoding='utf8')
 if '"regional-variants"' not in s:
  at=s.index('"reference-joint-play",');end=s.index('},',at)+2
  entry='\n        {\n           MsWidget::MAIN_WINDOW,\n           STATE_NORMAL | STATE_NOTE_ENTRY | STATE_PLAY,\n           "regional-variants",\n           QT_TRANSLATE_NOOP("action","分段试写方案"),\n           QT_TRANSLATE_NOOP("action","分段试写方案"),\n           QT_TRANSLATE_NOOP("action","在一个MSCZ中保留不同小节和声部的多种写法"),\n           Icons::play_ICON\n           },'
  p.write_bytes((s[:end]+entry+s[end:]).encode('utf8'))
 patch('mscore/plugin/api/qmlpluginapi.h','      Q_INVOKABLE QObject* newReferenceMedia();','      Q_INVOKABLE QObject* newReferenceMedia();\n      Q_INVOKABLE QObject* newReferenceProject();')
 if 'QObject* PluginAPI::newReferenceProject()' not in (HOST/'mscore/plugin/api/qmlpluginapi.cpp').read_text(encoding='utf8'):
  patch('mscore/plugin/api/qmlpluginapi.cpp','QObject* PluginAPI::newReferenceMedia() { return Ms::createReferenceMedia(this); }','QObject* PluginAPI::newReferenceMedia() { return Ms::createReferenceMedia(this); }\nQObject* PluginAPI::newReferenceProject() { return Ms::referenceProject(); }')
 patch('mscore/plugin/api/qmlpluginapi.h','      Q_INVOKABLE QObject* newWorkflowContext();','      Q_INVOKABLE QObject* newWorkflowContext();\n      Q_INVOKABLE void releaseReferenceMedia(QObject*);')
 patch('mscore/plugin/api/qmlpluginapi.cpp','QObject* PluginAPI::newReferenceMedia() { return Ms::createReferenceMedia(this); }','QObject* PluginAPI::newReferenceMedia() { auto media=Ms::createReferenceMedia(this);media->setProperty("kumoReferenceOwned",true);return media; }\nvoid PluginAPI::releaseReferenceMedia(QObject* media) { if(media&&media->parent()==this&&media->property("kumoReferenceOwned").toBool())media->deleteLater(); }')
 patch('mscore/seq.cpp','#include "seq.h"','#include "seq.h"\n#include "workflow/referencebus.h"')
 patch('mscore/seq.cpp','      float* p = buffer;','      ReferenceAudioPeriod referencePeriod(buffer,framesPerPeriod,playFrame,state==Transport::PLAY && !inCountIn);\n      float* p = buffer;')
 patch('mscore/seq.cpp','qreal playPosSeconds = PlaybackTiming::time(cs, playPosUTick);','qreal playPosSeconds = referenceOutputTime(PlaybackTiming::time(cs, playPosUTick));')
 patch('mscore/seq.cpp','playFrame < PlaybackTiming::time(cs, _preRollTarget) * MScore::sampleRate','playFrame < referenceOutputTime(PlaybackTiming::time(cs, _preRollTarget)) * MScore::sampleRate')
 patch('mscore/seq.cpp','playFrame = PlaybackTiming::time(cs, from) * MScore::sampleRate;','playFrame = referenceOutputTime(PlaybackTiming::time(cs, from)) * MScore::sampleRate;')
 patch('mscore/seq.cpp','            int scoreEndUTick = cs->repeatList().tick2utick(cs->lastMeasure()->endTick().ticks());','            const int referenceStopTick=inCountIn?-1:referenceEndTick();\n            const int referenceStopFrame=referenceStopTick<0?-1:int(referenceOutputTime(PlaybackTiming::time(cs,referenceStopTick))*MScore::sampleRate);\n            if(referenceStopFrame>=0)periodEndFrame=qMin(periodEndFrame,referenceStopFrame);\n            int scoreEndUTick = cs->repeatList().tick2utick(cs->lastMeasure()->endTick().ticks());')
 patch('mscore/seq.cpp','                        metronome(framesRemain, p, inCountIn);\n                        _synti->process(framesRemain, p);','                        const unsigned before=referenceStopFrame<0?framesRemain:unsigned(qBound(0,referenceStopFrame-*pPlayFrame,int(framesRemain)));\n                        if(before){metronome(before,p,inCountIn);_synti->process(before,p);}\n                        if(referenceStopFrame>=0&&*pPlayFrame+int(before)>=referenceStopFrame){stopNotes(-1,true);stopTransport();}\n                        if(before<framesRemain)_synti->process(framesRemain-before,p+before*2);')
 p=HOST/'mscore/seq.cpp';s=p.read_text(encoding='utf8');old='cs->utime2utick(qreal(playFrame) / qreal(MScore::sampleRate))';new='cs->utime2utick(referenceScoreTime(qreal(playFrame) / qreal(MScore::sampleRate)))'
 if old in s:
  if s.count(old)!=3:raise RuntimeError('Seq playback position sites changed')
  p.write_bytes(s.replace(old,new).encode('utf8'))
 s=p.read_text(encoding='utf8');period='      ReferenceAudioPeriod referencePeriod(buffer,framesPerPeriod,playFrame,state==Transport::PLAY && !inCountIn);\n'
 s=s.replace(period,'');anchor='      processMessages();\n'
 if s.count(anchor)!=1:raise RuntimeError('Seq period preparation changed')
 p.write_bytes(s.replace(anchor,anchor+period).encode('utf8'))
 for name in plugin_names:
  for src in (PLUGINS/name).glob('*'):
   if src.is_file() and src.suffix in ('.qml','.js','.md'):
    dst=HOST/'share/plugins'/name/src.name;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists() or dst.read_bytes()!=src.read_bytes():dst.write_bytes(src.read_bytes())
 recording_patch=ROOT/'midi-recording-host.patch'
 if recording_patch.exists():
  already=subprocess.run(['git','apply','--reverse','--check',str(recording_patch)],cwd=str(HOST),capture_output=True)
  if already.returncode:
   check=subprocess.run(['git','apply','--check',str(recording_patch)],cwd=str(HOST),capture_output=True)
   if check.returncode:raise RuntimeError('实时MIDI接线需要合并：'+check.stderr.decode('utf8',errors='replace'))
   subprocess.run(['git','apply',str(recording_patch)],cwd=str(HOST),check=True)
 updated={dst.relative_to(HOST).as_posix():hashlib.sha256(dst.read_bytes()).hexdigest() for src,dst in pending}
 state_path.write_bytes(json.dumps(updated,indent=2,ensure_ascii=False).encode('utf8'))
 print('本次修复模块和插件已更新到软件源码中。')
if __name__=='__main__':apply()
