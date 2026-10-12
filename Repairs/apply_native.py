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
