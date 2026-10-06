# -*- coding: utf-8 -*-
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
needle='''            details->close();QTest::qWait(30);QVERIFY(!panel->detailPanelVisible());'''
replacement='''            details->setFloating(true);details->resize(800,680);QTest::qWait(50);
            QVERIFY(details->isFloating());QTRY_VERIFY(panel->property("expanded").toBool());
            details->setFloating(false);main->addDockWidget(Qt::RightDockWidgetArea,details);
            main->resizeDocks({details},{360},Qt::Horizontal);QTest::qWait(30);
            details->close();QTest::qWait(30);QVERIFY(!panel->detailPanelVisible());'''
assert needle in s;s=s.replace(needle,replacement,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
