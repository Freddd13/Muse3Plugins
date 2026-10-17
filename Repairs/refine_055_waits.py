from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mtest/mscore/p1native/assistant_surface_tests.inc';s=p.read_text(encoding='utf8')
s=s.replace('QTest::qWait(40);QVERIFY(root->property("manualPositions").value<QJSValue>().toVariant().toList().isEmpty());','QTRY_VERIFY(root->property("manualPositions").value<QJSValue>().toVariant().toList().isEmpty());QTRY_VERIFY(!root->property("analysisDirty").toBool());QTRY_VERIFY(editor->isVisible());QTest::qWait(100);')
s=s.replace('QTest::qWait(80);\n  const auto owned=', 'QTRY_VERIFY(!root->property("analysisDirty").toBool());QTest::qWait(100);\n  const auto owned=')
p.write_bytes(s.encode())
