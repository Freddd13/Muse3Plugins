from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
k='mtest/mscore/p1native/assistant_surface_tests.inc';p=R/'native'/k
s=(p if p.exists() else H/k).read_text(encoding='utf8')
s=s.replace('positions.front().toMap()["y"].toDouble()<0);QCOMPARE(score->undoStack()->getCurIdx(),undo);','positions.front().toMap()["y"].toDouble()<0);QCOMPARE(score->undoStack()->getCurIdx(),undo+1);')
s=s.replace('QVERIFY(owned["end"].toInt()>start);QCOMPARE(score->undoStack()->getCurIdx(),undo);','''QVERIFY(owned["end"].toInt()>start);QCOMPARE(score->undoStack()->getCurIdx(),undo+1);
  observer->workflowUndo();QTest::qWait(80);QCOMPARE(root->property("ownedRegion").value<QJSValue>().toVariant().toMap()["end"].toInt(),end);
  observer->workflowUndo(true);QTest::qWait(80);QCOMPARE(root->property("ownedRegion").value<QJSValue>().toVariant().toMap()["end"].toInt(),owned["end"].toInt());''')
p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=R.parent/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8').replace('root.currentIssueIndex=issues.length?0:-1;rangeChoice=2;','root.currentIssueIndex=filteredIssues.length?issues.findIndex(function(i){return i.id===root.filteredIssues[0].id}):-1;rangeChoice=2;');p.write_bytes(s.encode())
