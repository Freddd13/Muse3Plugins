# coding: utf-8
"""Apply owned additions; never run earlier release installers over newer code."""
from pathlib import Path
import hashlib,json,subprocess
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
 for name in ['ReferencePlayer','PerformanceExpression','ArrangementVariants','ArrangementAssistant','HarmonyAssistant','WorkflowCommon']:
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
 patch('libmscore/CMakeLists.txt','slur.cpp freeslur.cpp tie.cpp','slur.cpp freeslur.cpp freesluravoidance.cpp tie.cpp')
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
 for name in ['ReferencePlayer','PerformanceExpression','ArrangementVariants','ArrangementAssistant','HarmonyAssistant','WorkflowCommon']:
  for src in (PLUGINS/name).glob('*'):
   if src.is_file() and src.suffix in ('.qml','.js','.md'):
    dst=HOST/'share/plugins'/name/src.name;dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists() or dst.read_bytes()!=src.read_bytes():dst.write_bytes(src.read_bytes())
 updated={dst.relative_to(HOST).as_posix():hashlib.sha256(dst.read_bytes()).hexdigest() for src,dst in pending}
 state_path.write_bytes(json.dumps(updated,indent=2,ensure_ascii=False).encode('utf8'))
 print('本次修复模块和插件已更新到软件源码中。')
if __name__=='__main__':apply()
