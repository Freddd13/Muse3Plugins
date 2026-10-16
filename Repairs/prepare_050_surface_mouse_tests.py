from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:70];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml'
edit(p,'Desk.DeskButton {text:"×";ToolTip.visible:hovered;ToolTip.text:"隐藏摘要，详情继续保留"','Desk.DeskButton {objectName:"arrangementSummaryClose";text:"×";ToolTip.visible:hovered;ToolTip.text:"隐藏摘要，详情继续保留"')
edit(p,'id:moreButton;text:"更多"','id:moreButton;objectName:"arrangementMore";text:"更多"')
edit(p,'MenuItem {text:"指定局部和弦…"','MenuItem {objectName:"arrangementChordExplanation";text:"指定局部和弦…"')
old='MouseArea {anchors.fill:parent;onClicked:{list.currentIndex=index;if(!root.observer || !root.observer.playing){root.locate();if(root.config.scoreHints)root.openProblemHint(modelData.tick)}}}'
new='MouseArea {anchors.fill:parent;hoverEnabled:true;ToolTip.visible:containsMouse;ToolTip.text:"单击定位，双击在谱旁查看";onClicked:{list.currentIndex=index;if(!root.observer || !root.observer.playing){root.locate();if(root.config.scoreHints)root.openProblemHint(modelData.tick)}};onDoubleClicked:root.openProblemHint(modelData.tick)}'
edit(p,old,new)
p=ROOT/'Repairs/native/mtest/mscore/p1native/assistant_surface_tests.inc'
old='  QVERIFY(QMetaObject::invokeMethod(root,"openProblemHint",Q_ARG(QVariant,note["tick"])));QTest::qWait(60);QVERIFY(root->findChild<QQuickWindow*>("arrangementProblemHint"));QVERIFY(root->findChild<QQuickWindow*>("arrangementProblemHint")->isVisible());'
new='''  auto boxes=view->notePreviewMarkerBoxes();QVERIFY(!boxes.isEmpty());auto hit=view->matrix().map(boxes.front().center()).toPoint();QVERIFY(view->rect().contains(hit));QTest::mouseDClick(view,Qt::LeftButton,Qt::NoModifier,hit);QTest::qWait(80);
  auto popup=root->findChild<QQuickWindow*>("arrangementProblemHint");QVERIFY(popup&&popup->isVisible());
  const auto output=qEnvironmentVariable("HARMONY_TEST_ARTIFACTS");if(!output.isEmpty())popup->grabWindow().save(output+"/arrangement-nearby-050.png");'''
edit(p,old,new)
old='  root->focusPanel();QTest::qWait(80);QVERIFY(primary->isVisible());summary->close();QTest::qWait(80);QVERIFY(primary->isVisible());QVERIFY(!root->summaryPanelVisible());'
new='''  auto click=[root](const char* name){auto item=root->findChild<QQuickItem*>(name);if(!item||!item->isEnabled()||!item->isVisible()||!item->window())return false;auto point=item->mapToScene(QPointF(item->width()/2,item->height()/2));QTest::mouseClick(item->window(),Qt::LeftButton,Qt::NoModifier,point.toPoint());return true;};
  root->focusPanel();QTest::qWait(80);QVERIFY(primary->isVisible());QVERIFY(click("arrangementSummaryClose"));QTest::qWait(80);QVERIFY(primary->isVisible());QVERIFY(!root->summaryPanelVisible());
  if(!output.isEmpty())root->window()->grabWindow().save(output+"/arrangement-range-050.png");
  primary->setFloating(false);mscore->addDockWidget(Qt::TopDockWidgetArea,primary);QTest::qWait(100);QVERIFY(QMetaObject::invokeMethod(root,"openDetails"));QTest::qWait(100);QVERIFY(root->detailPanelVisible());
  QVERIFY(click("arrangementSummaryClose"));QTest::qWait(80);QVERIFY(guarded);QVERIFY(!primary->isVisible());QVERIFY(root->detailPanelVisible());root->focusPanel();QTest::qWait(60);'''
edit(p,old,new)
old='  const auto folder=qEnvironmentVariable("HARMONY_TEST_ARTIFACTS");if(!folder.isEmpty())root->window()->grabWindow().save(folder+"/arrangement-range-050.png");root->setVisible(false);root->deleteLater();QTest::qWait(50);'
new='  if(!output.isEmpty())root->window()->grabWindow().save(output+"/arrangement-summary-050.png");root->setVisible(false);primary->setAttribute(Qt::WA_DeleteOnClose,true);primary->close();QTest::qWait(50);'
edit(p,old,new)
