# -*- coding: utf-8 -*-
"""One-time native GUI additions, run after extend_display_0_5.py."""
from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp'
s=p.read_text(encoding='utf-8')
needle='''            QVERIFY(panel->property("ribbon").toBool());
            auto ribbonImage=panelView->grabWindow();'''
replacement='''            QVERIFY(panel->property("ribbon").toBool());
            QTRY_VERIFY(panel->detailPanelVisible());
            auto details=main->findChild<QDockWidget*>("pluginDetailDock");QVERIFY(details);
            QCOMPARE(main->dockWidgetArea(details),Qt::RightDockWidgetArea);
            QVERIFY(panel->detailPanelHost());
            QCOMPARE(panel->findChildren<PluginAPI::ScoreObserver*>().size(),1);
            QCOMPARE(panel->findChildren<QObject*>("harmonyConfiguration").size(),1);
            auto summary=panel->findChild<QQuickItem*>("harmonySummary");QVERIFY(summary);
            QCOMPARE(summary->window(),panel->detailPanelHost()->window());
            auto detailImage=panel->detailPanelHost()->window()->grabWindow();
            QVERIFY(!detailImage.isNull());
            detailImage.save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("dual-details.png"));
            details->close();QTest::qWait(30);QVERIFY(!panel->detailPanelVisible());
            QVERIFY(QMetaObject::invokeMethod(panel,"toggleDetailPanel"));
            QTRY_VERIFY(panel->detailPanelVisible());
            auto ribbonImage=panelView->grabWindow();'''
assert needle in s;s=s.replace(needle,replacement,1)
needle='''            QVERIFY(panel->property("expanded").toBool());'''
assert needle in s;s=s.replace(needle,needle+'''
            QTRY_VERIFY(!panel->detailPanelVisible());
            QCOMPARE(summary->window(),panelView);''',1)
needle='''            const auto fixedPixels=view->grab(fixedArea).toImage();'''
assert needle in s;s=s.replace(needle,'''            const auto masked=view->grab(fixedArea).toImage();
            auto transparent=simultaneous;transparent["chordMask"]=false;
            observer.setScorePreview({transparent});
            QVERIFY(view->grab(fixedArea).toImage()!=masked);
            observer.setScorePreview({simultaneous});
'''+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Shared native dock ownership and mask GUI regressions added.')
