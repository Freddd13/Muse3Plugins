from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore';D=R/'staged056/native'
k='mtest/mscore/p1native/tst_p1native.cpp';p=R/'native'/k;s=(p if p.exists() else H/k).read_text(encoding='utf8')
s=s.replace(' void referenceClockAndPlan();',' void nativeReferenceDocumentAndMenu();\n void referenceClockAndPlan();').replace('#include "reference_tests.inc"','#include "reference_tests.inc"\n#include "reference_056_tests.inc"')
p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=D/'mtest/mscore/p1native/reference_056_tests.inc';p.write_bytes('''void TestP1Native::nativeReferenceDocumentAndMenu(){
 auto score=mscore->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");QVERIFY(score);mscore->setCurrentScoreView(mscore->appendScore(score));mscore->resize(1250,900);mscore->show();
 const auto scorePath=settings.filePath("portable.mscz");score->setFilePath(scorePath);
 PluginAPI::Score wrap(score);PluginAPI::ScoreObserver observer;observer.setScore(&wrap);
 QFile audio(settings.filePath("portable.wav"));QVERIFY(audio.open(QIODevice::WriteOnly));audio.write("temporary location probe");audio.close();
 const auto location=observer.referenceFileLocation("X:/missing/portable.wav","portable.wav");QVERIFY(location["exists"].toBool());QCOMPARE(QFileInfo(location["path"].toString()).absoluteFilePath(),QFileInfo(audio).absoluteFilePath());
 const QVariantMap project{{"schema",2},{"structure",observer.referenceStructureKey()},{"tracks",QVariantList{QVariantMap{{"id","audio1"},{"name","定位文件示例"},{"path","X:/missing/sample.wav"},{"relativePath","sample.wav"},{"associations",QVariantList{QVariantMap{{"start",0},{"end",1920},{"from",0},{"until",2000},{"active",true}}}}}}},{"linked",false}};
 QVERIFY(observer.setWorkflowData("reference",project)["ok"].toBool());QFileInfo info(scorePath);QVERIFY(score->saveCompressedFile(info,false,false));
 std::unique_ptr<MasterScore> reopened(mscore->readScore(scorePath));QVERIFY(reopened);PluginAPI::Score loaded(reopened.get());PluginAPI::ScoreObserver read;read.setScore(&loaded);QCOMPARE(read.workflowData("reference"),project);
 auto action=getAction("reference-player");QVERIFY(action);action->setEnabled(true);action->trigger();QTest::qWait(100);
 QmlPlugin* root=nullptr;for(auto window:QGuiApplication::allWindows())if(auto view=qobject_cast<QQuickView*>(window))if(auto q=qobject_cast<QmlPlugin*>(view->rootObject()))if(q->menuPath()=="Plugins.Reference Player")root=q;QVERIFY(root);
 QTRY_VERIFY(root->property("documentReady").toBool());QTRY_COMPARE(root->property("tracks").value<QJSValue>().toVariant().toList().size(),1);
 auto dock=mscore->findChild<QDockWidget*>("kumoPanel/ReferencePlayer_MS3");QVERIFY(dock&&dock->isVisible());QVERIFY(root->findChild<QQuickItem*>("referenceTimeScroll"));QVERIFY(!root->property("linkEditor").toBool());
 action->trigger();QVERIFY(!dock->isVisible());action->trigger();QVERIFY(dock->isVisible());
 const auto entry=QString(TESTROOT)+"/share/plugins/ReferencePlayer/ReferencePlayer_MS3.qml";mscore->loadPlugin(entry);mscore->pluginTriggered(entry);QTest::qWait(80);QCOMPARE(mscore->findChildren<QDockWidget*>("kumoPanel/ReferencePlayer_MS3").size(),1);
 auto folder=qEnvironmentVariable("HARMONY_TEST_ARTIFACTS");if(!folder.isEmpty())mscore->grab().save(folder+"/reference-native-056.png");
 root->disposePanelForReload();QCoreApplication::sendPostedEvents(nullptr,QEvent::DeferredDelete);
}
'''.encode())
p=D/'mscore/workflow/referencepanel.cpp';s=p.read_text(encoding='utf8').replace('if(referenceDock){referenceDock->setVisible(visible);if(visible)referenceRoot->focusPanel();return;}','if(referenceDock&&referenceRoot){referenceDock->setVisible(visible);if(visible)referenceRoot->focusPanel();return;}')
s=s.replace('root->attachPanelDock(dock);root->setFilePath','QObject::connect(root,&QObject::destroyed,dock,&QObject::deleteLater);\n root->attachPanelDock(dock);root->setFilePath');p.write_bytes(s.encode())
