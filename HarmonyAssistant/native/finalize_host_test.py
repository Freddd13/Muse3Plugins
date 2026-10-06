"""One-time development migration; not an installer."""
from pathlib import Path

root = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
p = root / 'mtest/mscore/pluginhost/tst_pluginhost.cpp'
s = p.read_text(encoding='utf-8')
a = s.index('            for(auto candidate:main->findChildren<QDockWidget*>())')
b = s.index('            QVERIFY(dock);', a)
s = s[:a] + '''            // createWindowContainer reparents the QWindow to a native window, not the dock QObject.
            for(auto window:QGuiApplication::allWindows()) {
                  auto view=qobject_cast<QQuickView*>(window);
                  auto root=view ? qobject_cast<QmlPlugin*>(view->rootObject()) : nullptr;
                  if(root && root->version()=="1.1.0") {panel=root;break;}
                  }
            for(auto candidate:main->findChildren<QDockWidget*>())
                  if(candidate->windowTitle()=="Harmony Assistant") {dock=candidate;break;}
''' + s[b:]
with p.open('w', encoding='utf-8', newline='\n') as f:
    f.write(s)
