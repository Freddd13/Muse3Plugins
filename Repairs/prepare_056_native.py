from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore';D=R/'staged056/native'
def read(k):
 p=R/'native'/k
 return (p if p.exists() else H/k).read_text(encoding='utf8')
def stage(k,s):
 p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
stage('mscore/workflow/referencepanel.h','''// GPL-2.0-or-later
#pragma once
class QMenu;
namespace Ms {void showReferencePanel(bool visible=true);void addReferencePanelAction(QMenu*);}
''')
stage('mscore/workflow/referencepanel.cpp','''// GPL-2.0-or-later. Native dock lifecycle; the media module is loaded on demand.
#include "referencepanel.h"
#include "paneldock.h"
#include "mscore/musescore.h"
#include "mscore/shortcut.h"
#include "mscore/plugin/qmlpluginengine.h"
#include "mscore/plugin/qmlplugin.h"
#include <QAction>
#include <QDockWidget>
#include <QQuickView>
#include <QPointer>
#include <QMenu>
#include <QApplication>
#include <QFileInfo>
namespace Ms {namespace {QPointer<QDockWidget> referenceDock;QPointer<QmlPlugin> referenceRoot;}
void showReferencePanel(bool visible){
 if(!mscore)return;
 if(referenceDock){referenceDock->setVisible(visible);if(visible)referenceRoot->focusPanel();return;}
 if(!visible)return;
 auto engine=new QmlPluginEngine;auto view=new QQuickView(engine,nullptr);engine->setParent(view);
 const auto file=mscoreGlobalShare+"plugins/ReferencePlayer/ReferencePlayer.view.qml";
 view->setResizeMode(QQuickView::SizeRootObjectToView);view->setSource(QUrl::fromLocalFile(file));
 auto root=qobject_cast<QmlPlugin*>(view->rootObject());if(!root){mscore->showMessage(QObject::tr("原曲参考界面读取失败，请检查安装目录中的 ReferencePlayer。"),8000);delete view;return;}
 auto dock=new QDockWidget(QObject::tr("原曲参考"),mscore);referenceDock=dock;referenceRoot=root;
 dock->setWidget(QWidget::createWindowContainer(view));dock->setMinimumSize(270,96);
 const bool restored=arrangeWorkflowDock(mscore,dock,"ReferencePlayer_MS3","bottomTools",Qt::BottomDockWidgetArea);
 root->attachPanelDock(dock);root->setFilePath(QFileInfo(file).absolutePath());
 QObject::connect(mscore->getPluginEngine(),&QmlPluginEngine::endCmd,root,&QmlPlugin::endCmd);
 QObject::connect(qApp,&QCoreApplication::aboutToQuit,root,[root]{root->disposePanelForReload();});
 auto action=getAction("reference-player");
 QObject::connect(dock,&QDockWidget::visibilityChanged,action,[action](bool shown){QSignalBlocker block(action);action->setChecked(shown);});
 QObject::connect(dock,&QObject::destroyed,action,[action]{QSignalBlocker block(action);action->setChecked(false);});
 view->setColor(QApplication::palette().color(QPalette::Window));dock->show();dock->raise();
 if(!restored)mscore->resizeDocks({dock},{350},Qt::Vertical);
 root->runPlugin();
}
void addReferencePanelAction(QMenu* menu){
 auto action=getAction("reference-player");action->setCheckable(true);menu->addAction(action);
 if(!action->property("referencePanelBound").toBool()){action->setProperty("referencePanelBound",true);QObject::connect(action,&QAction::triggered,qApp,[](bool checked){showReferencePanel(checked);});}
}
}
'''.replace('#include <QFileInfo>','#include <QFileInfo>\n#include <QSignalBlocker>'))
s=read('mscore/plugin/api/qmlpluginapi.h').replace('      Q_INVOKABLE QObject* newReferenceMedia();','      Q_INVOKABLE void openReferencePanel();\n      Q_INVOKABLE QObject* newReferenceMedia();',1);stage('mscore/plugin/api/qmlpluginapi.h',s)
s=read('mscore/plugin/api/qmlpluginapi.cpp').replace('#include "mscore/workflow/referencefactory.h"','#include "mscore/workflow/referencefactory.h"\n#include "mscore/workflow/referencepanel.h"',1).replace('QObject* PluginAPI::newReferenceMedia()','void PluginAPI::openReferencePanel(){Ms::showReferencePanel(true);}\nQObject* PluginAPI::newReferenceMedia()',1);stage('mscore/plugin/api/qmlpluginapi.cpp',s)
s=read('mscore/plugin/plugin.cmake').replace('set (PLUGIN_SRC','list(APPEND PLUGIN_API_SRC ${PROJECT_SOURCE_DIR}/mscore/workflow/referencepanel.cpp ${PROJECT_SOURCE_DIR}/mscore/workflow/referencepanel.h)\n\nset (PLUGIN_SRC',1);stage('mscore/plugin/plugin.cmake',s)
s=read('mscore/musescore.cpp').replace('#include "workflow/referencefactory.h"','#include "workflow/referencefactory.h"\n#include "workflow/referencepanel.h"',1).replace('      populateAlternativeOperations();','      populateAlternativeOperations();\n#ifdef SCRIPT_INTERFACE\n      addReferencePanelAction(menuView);\n#endif',1);stage('mscore/musescore.cpp',s)
s=read('mscore/shortcut.cpp');at=s.index('"tap-tempo",');at=s.index('},',at)+2
s=s[:at]+'''
      {MsWidget::MAIN_WINDOW,STATE_DISABLED | STATE_NORMAL | STATE_NOTE_ENTRY | STATE_PLAY | STATE_EDIT,
       "reference-player",QT_TRANSLATE_NOOP("action","原曲参考"),QT_TRANSLATE_NOOP("action","原曲参考"),QT_TRANSLATE_NOOP("action","打开或隐藏原曲参考播放器"),Icons::play_ICON},'''+s[at:];stage('mscore/shortcut.cpp',s)
# Keep the native view out of plugin metadata discovery.
s=read('mscore/plugin/mscorePlugins.cpp');at=s.index('bool collectPluginMetaInformation(');where=s.index('      qDebug(',at);s=s[:where]+'      if(d->path.endsWith(".view.qml"))return false;\n'+s[where:];stage('mscore/plugin/mscorePlugins.cpp',s)
s=read('mscore/plugin/api/scoreobserver.h').replace('      Q_INVOKABLE QVariantMap workflowData(', '      Q_INVOKABLE QVariantMap referenceFileLocation(const QString& original,const QString& relative=QString()) const;\n      Q_INVOKABLE QVariantMap workflowData(',1);stage('mscore/plugin/api/scoreobserver.h',s)
s=read('mscore/workflow/workflowdocument.cpp').replace('#include <QJsonDocument>','#include <QJsonDocument>\n#include <QDir>\n#include <QFileInfo>\n#include <QUrl>',1)
at=s.rfind('\n}}');s=s[:at]+'''
QVariantMap ScoreObserver::referenceFileLocation(const QString& original,const QString& relative) const{
 const auto path=QUrl(original).isLocalFile()?QUrl(original).toLocalFile():original;
 const auto base=_score?QFileInfo(_score->masterScore()->fileInfo()->absoluteFilePath()).absoluteDir():QDir();
 QString resolved=path;if(!relative.isEmpty()&&QFileInfo::exists(base.filePath(relative)))resolved=QDir::cleanPath(base.filePath(relative));
 QFileInfo info(resolved);return {{"path",info.absoluteFilePath()},{"relative",base.relativeFilePath(info.absoluteFilePath())},{"original",path},{"exists",info.exists()&&info.isFile()}};
}
'''+s[at:];stage('mscore/workflow/workflowdocument.cpp',s)
print('0.56 native panel staged separately')
