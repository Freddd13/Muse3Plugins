# -*- coding: utf-8 -*-
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
s=s.replace('#include "libmscore/harmony.h"','#include "libmscore/harmony.h"\n#include "libmscore/measure.h"',1)
needle='      void annotationPrioritiesWhileMoving()'
addition='''      void changeTickWithoutNewOnset()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();QTest::qWait(30);
            PluginAPI::Score wrapped(score);PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            auto first=observer.snapshot(0,4,8).value("notes").toList().front().toMap();
            first["chord"]="C";first["chordTick"]=0;first["chordUntil"]=240;
            auto second=first;second["chord"]="Am";second["chordTick"]=240;second["chordUntil"]=480;
            observer.setScorePreview({first,second});
            const auto segment=score->firstSegment(SegmentType::ChordRest);
            const auto next=score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest);
            const auto bass=toChord(segment->element(4))->notes().front();
            const qreal start=segment->canvasPos().x(),half=(start+next->canvasPos().x())/2;
            auto view=main->currentScoreView();QSignalSpy activation(&observer,&PluginAPI::ScoreObserver::previewActivated);
            QMap<int,qreal> hits;
            for(int dy=-qRound(bass->spatium()*40);dy<0 && hits.size()<2;dy+=2)
                  for(qreal x=start-2;x<half+40 && hits.size()<2;x+=1) {
                        const auto point=QPointF(x,bass->canvasPos().y()+dy);
                        if(!view->activateNotePreview(point))continue;
                        const int tick=activation.last().at(0).toInt();if(!hits.contains(tick))hits.insert(tick,x);
                        }
            QVERIFY(hits.contains(0));QVERIFY(hits.contains(240));
            QVERIFY(qAbs(hits[0]-start)<=2);QVERIFY(qAbs(hits[240]-half)<=2);
            observer.setActiveScorePreview(300);view->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("no-onset-change.png"));
            observer.clearAllPreviews();main->hide();
            }
'''
assert needle in s;s=s.replace(needle,addition+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Actual no-onset tick position / independent marker regression added.')
