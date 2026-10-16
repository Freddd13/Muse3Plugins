from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
name='mtest/mscore/p1native/tst_p1native.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
begin=s.index('  QVERIFY(click(expression,"expressionOriginalAudition"));')
end=s.index('\n  auto oldVelocity=',begin)
s=s[:begin]+'''  const int auditionTabs=mscore->scores().size();
  QVERIFY(click(expression,"expressionOriginalAudition"));QTRY_VERIFY2(expression->property("status").toString().contains("声音设备"),qPrintable(expression->property("status").toString()));
  QCOMPARE(mscore->scores().size(),auditionTabs);QCOMPARE(mscore->currentScore(),static_cast<Score*>(score));
  QVERIFY(click(expression,"expressionCandidateAudition"));QTRY_VERIFY(expression->property("status").toString().contains("声音设备"));QCOMPARE(mscore->scores().size(),auditionTabs);QVERIFY(!expression->property("previewing").toBool());
''' +s[end:]
s=s.replace('QTRY_VERIFY(expression->property("status").toString().contains("已使用演奏力度"));\n  QCOMPARE(score->undoStack()', 'QTRY_VERIFY(expression->property("status").toString().contains("已使用演奏力度"));\n  QTRY_VERIFY(!expression->property("busy").toBool());QVERIFY(!expression->property("stale").toBool());\n  QCOMPARE(score->undoStack()',1)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mtest/mscore/p1native/velocity_history_tests.inc';p=root/'native'/name;s=p.read_text(encoding='utf8')
s=s.replace('   original.append({int(note->veloType()),note->veloOffset()});','   if(notes.size()==1){note->setVeloType(Note::ValueType::USER_VAL);note->setVeloOffset(55);row["velocityType"]=int(note->veloType());row["velocityRaw"]=note->veloOffset();}\n   original.append({int(note->veloType()),note->veloOffset()});',1)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
print('Mouse checks now expect original-score audition and continuing partial application')
