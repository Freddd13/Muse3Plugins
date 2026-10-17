from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf8')
at=s.index('      void menuMetadataRelayoutAndDocking()')
s=s[:at]+'''      void nativeWorkflowDocumentAndTypography(){
            auto main=Ms::mscore;auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            PluginAPI::Score wrapped(score);PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            const QVariantMap data{{"schema",2},{"overrides",QVariantList{QVariantMap{{"start",0},{"end",1920},{"root",0},{"part",0}}}},{"positions",QVariantList{QVariantMap{{"start",0},{"part",0},{"x",1.},{"y",-1.}}}}};
            const int before=score->undoStack()->getCurIdx();auto saved=observer.setWorkflowData("harmony",data);QVERIFY2(saved.value("ok").toBool(),qPrintable(saved.value("error").toString()));QCOMPARE(score->undoStack()->getCurIdx(),before+1);QCOMPARE(observer.workflowData("harmony"),data);
            saved=observer.setWorkflowData("harmony",data);QVERIFY(saved.value("ok").toBool());QVERIFY(!saved.value("changed").toBool());QCOMPARE(score->undoStack()->getCurIdx(),before+1);
            EditData edit;score->undoRedo(true,&edit);QVERIFY(observer.workflowData("harmony").isEmpty());score->undoRedo(false,&edit);QCOMPARE(observer.workflowData("harmony"),data);
            const auto path=_settings.filePath("workflow-data.mscz");QFileInfo info(path);QVERIFY(score->saveCompressedFile(info,false,false));std::unique_ptr<MasterScore> restored(main->readScore(path));QVERIFY(restored);PluginAPI::Score read(restored.get());PluginAPI::ScoreObserver readObserver;readObserver.setScore(&read);QCOMPARE(readObserver.workflowData("harmony"),data);
            QVERIFY(observer.setWorkflowData("unlisted",data).contains("error"));
            for(const auto chord:{"C/E","D/F#","C7/E","F#m7b5/C"}){auto label=observer.harmonyLabel(chord,QString::fromUtf8("I⁶"),{{"pixels",24}});QVERIFY(label.value("baseline").toDouble()>0);QVERIFY(label.value("height").toInt()>10);const auto source=label.value("source").toString();QImage image;QVERIFY(image.loadFromData(QByteArray::fromBase64(source.mid(source.indexOf(',')+1).toLatin1())));image.save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath(QString(chord).replace('/','_').replace('#','s')+"-baseline.png"));}
            }
'''+s[at:]
p.write_bytes(s.encode())
