from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;N=ROOT/'Repairs/native';HOST=ROOT.parent/'muse3_dev/MuseScore'
def mirror(name):
 p=N/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HOST/name).read_bytes())
 return p
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:60];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=mirror('mscore/plugin/plugin.cmake');edit(p,'    ${PROJECT_SOURCE_DIR}/mscore/workflow/playbackpreview.h','    ${PROJECT_SOURCE_DIR}/mscore/workflow/analysisidentity.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/positionhint.h\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/positionhint.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/playbackpreview.h')
p=mirror('mscore/workflow/scoreworkflow.cpp');edit(p,'#include "playbackpreview.h"','#include "playbackpreview.h"\n#include "positionhint.h"');edit(p,' if(auto editor=mscore->findChild<PerformanceEditor*>())editor->revealTick(tick);',' if(auto editor=mscore->findChild<PerformanceEditor*>())editor->revealTick(tick);\n if(!audition)showWorkflowPositionHint(view,range);')
p=mirror('mscore/plugin/qmlplugin.h');edit(p,'      Q_INVOKABLE void focusPanel();','      Q_INVOKABLE void focusPanel();\n      Q_INVOKABLE void hidePanel();')
p=mirror('mscore/plugin/qmlplugin.cpp');edit(p,'      _panelDock = dock;','''      _panelDock = dock;
      if(property("independentPanelSurfaces").toBool())dock->setAttribute(Qt::WA_DeleteOnClose,false);''');edit(p,'QQuickItem* QmlPlugin::detailPanelHost() const','void QmlPlugin::hidePanel() { if(_panelDock)_panelDock->hide(); }\nQQuickItem* QmlPlugin::detailPanelHost() const')
edit(p,'_summaryDock=new QDockWidget(tr("和弦摘要"),main);','''const auto title=property("summaryPanelTitle").toString();
            _summaryDock=new QDockWidget(title.isEmpty()?_panelDock->windowTitle()+tr(" · 摘要"):title,main);''')
p=mirror('mscore/plugin/mscorePlugins.cpp')
old='      QmlPluginEngine* engine = getPluginEngine();\n      QmlPlugin* p = pluginFromPath(engine, pp);'
new='''      // An independently hidden workflow panel keeps its result and other surfaces.
      for(auto window:QGuiApplication::allWindows())if(auto view=qobject_cast<QQuickView*>(window))
            if(auto existing=qobject_cast<QmlPlugin*>(view->rootObject()))
                  if(existing->property("independentPanelSurfaces").toBool() && existing->property("workflowPluginPath").toString()==pp){existing->focusPanel();return;}
      QmlPluginEngine* engine = getPluginEngine();
      QmlPlugin* p = pluginFromPath(engine, pp);'''
edit(p,old,new)
edit(p,'                  p->attachPanelDock(dock);','                  if(p->property("independentPanelSurfaces").toBool())p->setProperty("workflowPluginPath",pp);\n                  p->attachPanelDock(dock);')
