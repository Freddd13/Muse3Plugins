# coding: utf-8
"""Apply owned additions; never run earlier release installers over newer code."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent
PLUGINS=ROOT.parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def patch(path,old,new):
 p=HOST/path;s=p.read_text(encoding='utf8')
 if new in s:return
 if s.count(old)!=1:raise RuntimeError('Cannot identify edit in '+path+': '+old[:55])
 p.write_bytes(s.replace(old,new).encode('utf8'))
def apply():
 for src in (ROOT/'native').rglob('*'):
  if src.is_file():
   dst=HOST/src.relative_to(ROOT/'native');dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists() or dst.read_bytes()!=src.read_bytes():dst.write_bytes(src.read_bytes())
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
 print('Current repair modules and plugins installed in source tree.')
if __name__=='__main__':apply()
