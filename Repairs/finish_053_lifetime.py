from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
p=R/'native/mscore/plugin/mscorePlugins.cpp';s=p.read_text(encoding='utf8')
a='                  p->attachPanelDock(dock);'
s=s.replace(a,a+'\n                  connect(qApp,&QCoreApplication::aboutToQuit,p,[p]{p->disposePanelForReload();});',1)
p.write_bytes(s.encode())
p=H/'mtest/mscore/p1native/tst_p1native.cpp';s=p.read_text(encoding='utf8')
s=s.replace(' void initTestCase(){',''' void cleanupTestCase(){
  QList<QPointer<QmlPlugin>> roots;for(auto w:QGuiApplication::allWindows())if(auto v=qobject_cast<QQuickView*>(w))if(auto p=qobject_cast<QmlPlugin*>(v->rootObject()))roots.append(p);
  for(auto p:roots)if(p)p->disposePanelForReload();QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
 }
 void initTestCase(){''',1)
p=R/'native/mtest/mscore/p1native/tst_p1native.cpp';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
