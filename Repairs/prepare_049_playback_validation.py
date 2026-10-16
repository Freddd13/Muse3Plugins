from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
N=ROOT/'Repairs/native'
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:60];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=N/'mscore/workflow/referenceworkflow.cpp'
edit(p,'#include <QAction>','#include <QAction>\n#include <QSignalBlocker>')
edit(p,'*started=true;seq->setScoreView(mscore->currentScoreView());seq->startAtUTick(from);','*started=true;seq->setScoreView(mscore->currentScoreView());if(auto play=getAction("play")){QSignalBlocker block(play);play->setChecked(true);}seq->startAtUTick(from);')
if '#include "mscore/shortcut.h"' not in p.read_text(encoding='utf8'):edit(p,'#include "mscore/seq.h"','#include "mscore/seq.h"\n#include "mscore/shortcut.h"')
p=N/'mtest/mscore/performanceeditor/expression_playback_tests.inc'
old='            stopPlaybackPreview(true);QApplication::processEvents();QVERIFY(!sequence->isPlaying());QVERIFY(!activePlaybackPreviewEvents(score));QCOMPARE(referenceEndTick(),-1);QVERIFY(!workflowContext()->audition()["playing"].toBool());'
new=old+'''
            // The actual plugin API prepares, swaps and frees its temporary material on the source tab.
            PluginAPI::Score wrapped(score);PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);observer.workflowInfo();
            auto revision=observer.analysisRevision();auto scope=observer.analysisScope(true);scope["occurrence"]=1;
            auto page=observer.performanceRange(0,scope["end"].toInt(),0,score->ntracks(),0,100,revision);QVariantList targets;
            for(auto value:page["notes"].toList()){auto n=value.toMap();n["oldType"]=n["velocityType"];n["oldRaw"]=n["velocityRaw"];n["oldBase"]=n["velocityBase"];n["target"]=105;n["unlock"]=true;targets.append(n);}
            QVERIFY(!targets.isEmpty());QVariantMap candidate{{"revision",revision},{"scope",scope},{"velocity",targets},{"tempos",QVariantList{}}};
            auto prepared=observer.auditionExpression(QString(),candidate,scope,true);QVERIFY2(prepared["ok"].toBool(),qPrintable(prepared["error"].toString()));QApplication::processEvents();QVERIFY(sequence->isPlaying());
            for(int i=0;i<5;++i)driver->pulse();before=sequence->getCurTick();
            auto continued=observer.auditionExpression(QString(),candidate,scope,true);QVERIFY(continued["continuing"].toBool());QCOMPARE(sequence->getCurTick(),before);
            auto source=observer.auditionExpression(QString(),candidate,scope,false);QVERIFY(source["ok"].toBool());QCOMPARE(source["fromUtick"].toInt(),before);QApplication::processEvents();QVERIFY(sequence->isPlaying());
            QCOMPARE(main->scores().size(),tabs);QCOMPARE(main->currentScore(),static_cast<Score*>(score));QCOMPARE(score->undoStack()->getCurIdx(),undo);QVERIFY(score->state()==state);
            QVERIFY(observer.finishExpressionAudition()["ok"].toBool());QApplication::processEvents();QVERIFY(!sequence->isPlaying());
'''
edit(p,old,new)
p=N/'mtest/mscore/p1native/tst_p1native.cpp'
old='  auto parameterCompare=editorDock->findChild<QToolButton*>("performanceExpressionCompare");QVERIFY(parameterCompare&&parameterCompare->isChecked());'
new=old+'''
  auto parameterSelector=editorDock->findChild<QComboBox*>("performanceParameter");QVERIFY(parameterSelector&&parameterSelector->isVisible());
  QVERIFY(!QRect(parameterSelector->mapTo(editorDock,QPoint()),parameterSelector->size()).intersects(QRect(parameterCompare->mapTo(editorDock,QPoint()),parameterCompare->size())));
'''
edit(p,old,new)
