"""Add a real window reload case before changing the plugin lifetime code."""
from pathlib import Path
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
p=Path('mtest/mscore/pluginhost/tst_pluginhost.cpp')
s=(H/p).read_text(encoding='utf8')
s=s.replace('#include <QLabel>','#include <QLabel>\n#include <QMessageBox>\n#include <QTimer>')
case=r'''
      void reloadActiveWorkflowPanels()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();
            PluginManager manager(main);manager.init();
            const QString path=QString(TESTROOT)+"/share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml";
            main->pluginTriggered(path);QTest::qWait(100);
            auto live=[&](){int count=0;for(auto window:QGuiApplication::allWindows())if(auto view=qobject_cast<QQuickView*>(window))if(auto root=qobject_cast<QmlPlugin*>(view->rootObject()))if(root->menuPath()=="Plugins.Harmony Assistant")++count;return count;};
            QCOMPARE(live(),1);
            for(int i=0;i<3;++i){
                  QTimer dismiss;dismiss.setInterval(50);connect(&dismiss,&QTimer::timeout,this,[]{for(auto w:QApplication::topLevelWidgets())if(auto box=qobject_cast<QMessageBox*>(w))box->accept();});dismiss.start();
                  QVERIFY(QMetaObject::invokeMethod(&manager,"reloadPluginsClicked",Qt::DirectConnection));
                  QTest::qWait(100);QCOMPARE(live(),1);
                  }
            }
'''
if 'void reloadActiveWorkflowPanels()' not in s:s=s.replace('      void menuMetadataRelayoutAndDocking()',case+'      void menuMetadataRelayoutAndDocking()')
t=R/'native'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_text(s,encoding='utf8',newline='\n')
print(t)
