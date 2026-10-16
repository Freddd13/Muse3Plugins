from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def patch(name,old,new):
 p=root/'native'/name;s=p.read_text(encoding='utf8');assert s.count(old)==1,(name,old[:80],s.count(old));p.write_text(s.replace(old,new),encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
patch('mscore/plugin/api/scoreobserver.h','      Q_INVOKABLE QVariantMap showEditorComparison();','      Q_INVOKABLE QVariantMap showEditorComparison();\n      Q_INVOKABLE QVariantMap showEditorCorrespondence();')
name='mscore/workflow/workflowexpression.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
s=s.replace('#include <QToolButton>','#include <QToolButton>\n#include <QComboBox>',1)
start=s.index('QVariantMap ScoreObserver::showEditorComparison()');end=s.index('QVariantMap ScoreObserver::expressionSelection()',start)
s=s[:start]+'''QVariantMap ScoreObserver::showEditorComparison() {
 if(!mscore||!_score)return {{"error",tr("打开乐谱后可以查看力度对比。")}};
 auto oldDock=mscore->findChild<QDockWidget*>("performanceEditorDock");const bool wasVisible=oldDock&&oldDock->isVisible();
 if(auto action=mscore->findChild<QAction*>("performance-editor"))action->setChecked(true);mscore->showPerformanceEditor(true);
 if(auto button=mscore->findChild<QToolButton*>("performanceExpressionCompare"))button->setChecked(true);
 if(auto parameter=mscore->findChild<QComboBox*>("performanceParameter"))if(parameter->currentIndex()==2)parameter->setCurrentIndex(0);
 if(auto dock=mscore->findChild<QDockWidget*>("performanceEditorDock")){
  dock->show();dock->raise();const auto area=mscore->dockWidgetArea(dock);
  if(!wasVisible&&(area==Qt::BottomDockWidgetArea||area==Qt::TopDockWidgetArea))mscore->resizeDocks({dock},{qMin(mscore->height()-180,qMax(dock->widget()->minimumSizeHint().height()+24,mscore->height()/2))},Qt::Vertical);
 }
 return {{"ok",true}};
}
QVariantMap ScoreObserver::showEditorCorrespondence(){
 auto shown=showEditorComparison();if(shown.contains("error"))return shown;
 if(auto toggle=mscore->findChild<QToolButton*>("performanceWorkflowToggle"))toggle->setChecked(true);
 if(auto dock=mscore->findChild<QDockWidget*>("performanceEditorDock")){auto area=mscore->dockWidgetArea(dock);if(area==Qt::BottomDockWidgetArea||area==Qt::TopDockWidgetArea)mscore->resizeDocks({dock},{qMin(mscore->height()-180,qMax(dock->height(),dock->widget()->minimumSizeHint().height()+100))},Qt::Vertical);}
 return shown;
}
''' +s[end:]
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mscore/performanceeditor/expressioncompare.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
old='                  if(note.selected||i==_comparisonAnchor)painter.drawText(QPointF(x+7,target-5),QString("%1 → %2").arg(NoteVelocity::effective(note.base,note.type,note.raw)).arg(qRound(_comparisonDraft.value(_comparisonValues.value(i).value("id").toString(),_comparisonValues.value(i).value("target").toDouble()))));'
new='''                  if(i==_comparisonAnchor||(!_selectedIndices.isEmpty()&&i==_selectedIndices.front())){const QString text=QString("%1 → %2").arg(NoteVelocity::effective(note.base,note.type,note.raw)).arg(qRound(_comparisonDraft.value(_comparisonValues.value(i).value("id").toString(),_comparisonValues.value(i).value("target").toDouble())));const double w=painter.fontMetrics().horizontalAdvance(text)+10;QRectF badge(qBound(lane.left(),x+8,qMax(lane.left(),lane.right()-w)),lane.bottom()-19,w,18);painter.fillRect(badge,_appearance.colors[PerformanceAppearance::Background]);painter.setPen(QPen(color,1));painter.drawRect(badge);painter.setPen(original);painter.drawText(badge,Qt::AlignCenter,text);}'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
# Use the explicit correspondence command for correction tools and retain the ordinary parameter view.
p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace('else root.status="编辑器已显示原力度和演奏力度，可在下方试听和使用。"','else root.status="力度区已显示前后对比。实心条可拖动，使用力度后写入乐谱。"',1)
s=s.replace(' Menu {id:applicationMenu',' Menu {id:applicationMenu\n  MenuItem {text:"在编辑器调整对应";enabled:root.result.matches.length>0;onTriggered:{root.publishComparison();root.observer.showEditorCorrespondence()}}',1)
p.write_text(s,encoding='utf8',newline='\n')
# Check the main parameter view first, then expand the optional correspondence track.
name='mtest/mscore/p1native/tst_p1native.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
old='  auto compareLane = editorDock->findChild<QWidget *>("performanceWorkflowLanes");\n  QTRY_VERIFY(compareLane && compareLane->isVisible());'
new='''  auto compareLane = editorDock->findChild<QWidget *>("performanceWorkflowLanes");QVERIFY(compareLane);
  auto parameterCompare=editorDock->findChild<QToolButton*>("performanceExpressionCompare");QVERIFY(parameterCompare&&parameterCompare->isChecked());
  const auto previewOutput=qEnvironmentVariable("HARMONY_TEST_ARTIFACTS");if(!previewOutput.isEmpty())editorDock->grab().save(previewOutput+"/editor-expression-main-049.png");
  QVERIFY(observer->showEditorCorrespondence()["ok"].toBool());QTRY_VERIFY(compareLane->isVisible());'''
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
print('Parameter comparison opens first; the correspondence track expands separately')
