from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
needle='''            dock->close();QTest::qWait(50);
            // Repeated open/close'''
assert needle in s;s=s.replace(needle,'''            dock->close();QTest::qWait(50);
            QTRY_VERIFY(main->findChildren<QDockWidget*>("pluginDetailDock").isEmpty());
            // Repeated open/close''',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
