"""One-time GUI fixture migration; preserves the production program."""
from pathlib import Path
p = Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s = p.read_text(encoding='utf-8')
s = s.replace('QmlPlugin* panel=nullptr;', 'QmlPlugin* panel=nullptr;\n            QQuickView* panelView=nullptr;')
s = s.replace('{panel=root;break;}', '{panel=root;panelView=view;break;}')
s = s.replace('            QVERIFY(panel->property("ribbon").toBool());', '''            QVERIFY(panel->property("ribbon").toBool());
            auto ribbonImage=panelView->grabWindow();
            QVERIFY(!ribbonImage.isNull());
            ribbonImage.save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("ribbon.png"));''')
s = s.replace('            dock->grab().save', '''            auto floatingImage=panelView->grabWindow();
            QVERIFY(!floatingImage.isNull());
            floatingImage.save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("floating-panel.png"));
            dock->grab().save''')
s = s.replace('            main->close();', '''            // This fixture deliberately skips main()'s workspace/audio initialization.
            // Exercise plugin destruction; do not invoke unrelated workspace-save code.
            for(auto candidate:main->findChildren<QDockWidget*>())
                  if(candidate->windowTitle()=="Harmony Assistant") candidate->close();
            QTest::qWait(50);
            main->hide();''')
with p.open('w', encoding='utf-8', newline='\n') as f:
    f.write(s)
