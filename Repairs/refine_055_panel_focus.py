from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mscore/plugin/qmlplugin.cpp';s=p.read_text(encoding='utf8');s=s.replace('if (_panelDock->widget()) _panelDock->widget()->setFocus(Qt::OtherFocusReason);','if (_panelDock->widget()) _panelDock->widget()->setFocus(Qt::OtherFocusReason);\n      if(window()){window()->requestActivate();forceActiveFocus(Qt::OtherFocusReason);}',1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/p1native/tst_p1native.cpp';s=p.read_text(encoding='utf8').replace('reference->forceActiveFocus();double oldStart=','reference->focusPanel();reference->forceActiveFocus();QTest::qWait(80);double oldStart=');p.write_bytes(s.encode())
# Carry the updated fixture into the later native-player batch.
p=R/'staged056/native/mtest/mscore/p1native/tst_p1native.cpp';s=p.read_text(encoding='utf8').replace('reference->forceActiveFocus();double oldStart=','reference->focusPanel();reference->forceActiveFocus();QTest::qWait(80);double oldStart=');p.write_bytes(s.encode())
