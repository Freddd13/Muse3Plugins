"""Repair plugin window lifetime and reference playback invalidation."""
from pathlib import Path
R=Path(__file__).resolve().parent; H=R.parent.parent/'muse3_dev/MuseScore'
def edit(path,changes):
    p=H/path;s=p.read_text(encoding='utf8')
    for old,new in changes:
        if new in s:continue
        assert s.count(old)==1,(path,old[:100],s.count(old))
        s=s.replace(old,new)
    t=R/'native'/path;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(s.encode())
edit('mscore/plugin/mscorePlugins.cpp',[
 ('      QQmlComponent component(getPluginEngine(), QUrl::fromLocalFile(_pluginPath));','      QmlPluginEngine metadataEngine;\n      QQmlComponent component(&metadataEngine, QUrl::fromLocalFile(_pluginPath));'),
 ('      QString menuPath = item->menuPath();','      if (!item) { delete obj; return; }\n      QString menuPath = item->menuPath();'),
 ('                  tr("No score open.\\n"','                  tr("No score open.\\n"'),
 ('            QQuickView* view = new QQuickView(engine, 0);','            engine = new QmlPluginEngine(qApp);\n            QQuickView* view = new QQuickView(engine, 0);\n            engine->setParent(view);'),
 ('                  if(p->property("independentPanelSurfaces").toBool())p->setProperty("workflowPluginPath",pp);','                  p->setProperty("workflowPluginPath",pp);'),
 ('      connect(engine, &QmlPluginEngine::endCmd, p, &QmlPlugin::endCmd);','      connect(getPluginEngine(), &QmlPluginEngine::endCmd, p, &QmlPlugin::endCmd);'),
 ('      QQmlComponent component(mscore->getPluginEngine(), QUrl::fromLocalFile(d->path));','      QmlPluginEngine metadataEngine;\n      QQmlComponent component(&metadataEngine, QUrl::fromLocalFile(d->path));')])
edit('mscore/plugin/qmlplugin.h',[
 ('      void attachPanelDock(QDockWidget* dock);','      void attachPanelDock(QDockWidget* dock);\n      void disposePanelForReload();')])
edit('mscore/plugin/qmlplugin.cpp',[
 ('void QmlPlugin::attachPanelDock(QDockWidget* dock)','void QmlPlugin::disposePanelForReload()\n      {\n      auto dock=_panelDock.data();\n      if(dock){dock->close();_panelDock.clear();delete dock;}\n      }\n\nvoid QmlPlugin::attachPanelDock(QDockWidget* dock)')])
edit('mscore/plugin/pluginManager.h',[
 ('      bool shortcutsChanged;','      bool shortcutsChanged;\n      bool _reloadWaiting=false;')])
edit('mscore/plugin/pluginManager.cpp',[
 ('#include "preferences.h"','#include "preferences.h"\n#include "qmlplugin.h"\n#include <QQuickView>\n#include <QGuiApplication>\n#include <QTimer>\n#include <QJSValue>\n#include <QSignalBlocker>'),
 ('            QmlPluginEngine* engine = mscore->getPluginEngine();\n            engine->clearComponentCache(); //TODO: Check this doesn\'t have unwanted side effects.','            // Every running panel has its own engine. Metadata scans use a short-lived engine.'),
 ('      QStringList saveLoaded; // If forcing a refresh, the load flags are lost. Keep a copy and reapply.','      const QSignalBlocker block(pluginListWidget);\n      const auto previous=_pluginList;\n      QString selectedPath;\n      if(auto item=pluginListWidget->currentItem()){int i=item->data(Qt::UserRole).toInt();if(i>=0&&i<_pluginList.size())selectedPath=_pluginList[i].path;}\n      QStringList saveLoaded; // Keep enabled plugins and shortcuts during a rescan.'),
 ('            Shortcut* s = &d.shortcut;\n            localShortcuts[s->key()] = new Shortcut(*s);','            if(forceRefresh)for(const auto& old:previous)if(old.path==d.path){d.shortcut=old.shortcut;break;}\n            Shortcut* s = &d.shortcut;\n            if(!localShortcuts.contains(s->key()))localShortcuts[s->key()] = new Shortcut(*s);'),
 ('            pluginListWidget->setCurrentRow(0);\n            pluginListWidgetItemChanged(pluginListWidget->item(0), 0);','            int selected=0;for(int i=0;i<n;++i)if(_pluginList[i].path==selectedPath)selected=i;\n            pluginListWidget->setCurrentRow(selected);\n            pluginListWidgetItemChanged(pluginListWidget->item(selected), 0);'),
 ('      int idx = item->data(Qt::UserRole).toInt();','      int idx = item->data(Qt::UserRole).toInt();'),
 ('''      loadList(true);
      QMessageBox::information(0,
            tr("MuseScore"),
            tr("Plugins reloaded."),
            QMessageBox::Ok, QMessageBox::NoButton);''','''      QList<QPointer<QmlPlugin>> panels;
      bool waiting=QApplication::mouseButtons()!=Qt::NoButton;
      for(auto window:QGuiApplication::allWindows())if(auto view=qobject_cast<QQuickView*>(window))
            if(auto panel=qobject_cast<QmlPlugin*>(view->rootObject())){
                  auto capture=panel->property("captureState").value<QJSValue>().toVariant().toMap();
                  waiting=waiting||capture.value("recording").toBool()||capture.value("stopping").toBool()||capture.value("saving").toBool();
                  if(!panel->property("workflowPluginPath").toString().isEmpty())panels.append(panel);
                  }
      if(waiting){
            reloadPlugins->setEnabled(false);reloadPlugins->setToolTip(tr("录制或拖动结束后将重载插件。"));
            if(!_reloadWaiting){_reloadWaiting=true;QTimer::singleShot(200,this,[this]{_reloadWaiting=false;reloadPluginsClicked();});}return;
            }
      reloadPlugins->setEnabled(false);
      QStringList reopen;
      for(auto panel:panels)if(panel){reopen.append(panel->property("workflowPluginPath").toString());panel->disposePanelForReload();}
      QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
      loadList(true);
      for(auto& plugin:_pluginList)if(plugin.load)mscore->registerPlugin(&plugin);
      for(const auto& path:reopen)mscore->pluginTriggered(path);
      reloadPlugins->setEnabled(true);reloadPlugins->setToolTip(tr("重新读取插件，并恢复打开的面板。"));
      QMessageBox::information(this,tr("MuseScore"),tr("插件已重载，打开的面板已恢复。"));''')])
edit('mscore/plugin/api/scoreobserver.h',[
 ('      Q_INVOKABLE QVariantMap referencePlan(const QVariantMap&);','      Q_INVOKABLE QString referenceStructureKey() const;\n      Q_INVOKABLE QVariantMap referencePlan(const QVariantMap&);')])
p=H/'mscore/workflow/referenceworkflow.cpp';s=p.read_text(encoding='utf8')
key='''QString ScoreObserver::referenceStructureKey() const {
 if(!_score)return {};
 QByteArray bytes;QDataStream out(&bytes,QIODevice::WriteOnly);
 for(auto measure=_score->firstMeasure();measure;measure=measure->nextMeasure())
  out<<measure->tick().ticks()<<measure->ticks().ticks()<<measure->timesig().numerator()<<measure->timesig().denominator();
 return QString::fromLatin1(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex());
}
'''
if 'ScoreObserver::referenceStructureKey()' not in s:
    s='#include <QCryptographicHash>\n#include <QDataStream>\n'+s
    anchor='QVariantMap ScoreObserver::referencePlan('
    assert anchor in s;s=s.replace(anchor,key+anchor,1)
(R/'native/mscore/workflow/referenceworkflow.cpp').write_bytes(s.encode())
p=R.parent/'ReferencePlayer/ReferencePlayer_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('property string workspace:""','property string workspace:""\n property string structureKey:""')
s=s.replace(' || height<170','')
s=s.replace('''  if(state && !state.selectionChanged && state.startLayoutTick>=0 && associations.length) {
   associations=associations.map(function(v){var n=Project.copy(v);if(state.startLayoutTick<n.end && state.endLayoutTick>n.start)n.stale=true;return n});
   status="谱面已编辑 · 相关关联请核查";
  }''','''  var shape=observer&&typeof observer.referenceStructureKey==="function"?observer.referenceStructureKey():"";
  if(structureKey&&shape&&structureKey!==shape&&associations.length){
   associations=associations.map(function(v){var n=Project.copy(v);n.stale=true;return n});
   status="小节或拍号已改变，请在关联行调整对应范围。";
  }
  structureKey=shape;''')
s=s.replace('owner=curScore;observer.score=curScore;','owner=curScore;observer.score=curScore;\n  if(changed)structureKey=typeof observer.referenceStructureKey==="function"?observer.referenceStructureKey():"";')
p.write_bytes(s.encode())
print('0.53 sources prepared')
