# -*- coding: utf-8 -*-
"""One-time real host click/color-picker regression extension."""
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8').replace('#include <QQuickView>','#include <QQuickView>\n#include <QJSValue>')
needle='            // The panel jump keeps dock placement; top docks open their full detail tool window.'
extension='''            observer->setScorePreview({anchor});
            const auto note=toChord(score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest)->element(0))->notes().front();
            auto scoreView=main->currentScoreView();QPointF hitPoint;bool found=false;
            for(int dy=-120;dy<0 && !found;dy+=2) for(int dx=2;dx<80;dx+=2) {
                  const auto candidate=note->canvasPos()+QPointF(dx,dy);
                  if(scoreView->activateNotePreview(candidate)){hitPoint=candidate;found=true;break;}
                  }
            QVERIFY(found);
            observer->setScorePreview({anchor});QTest::qWait(20);
            const int priorClicks=activation.size();
            const auto physical=scoreView->toPhysical(hitPoint).toPoint();
            QVERIFY(scoreView->rect().contains(physical));
            QTest::mouseDClick(scoreView,Qt::LeftButton,Qt::NoModifier,physical);
            QTRY_VERIFY(activation.size()>priorClicks);
            scoreView->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("score-fixed-label.png"));
'''
assert needle in s;s=s.replace(needle,extension+needle,1)
needle='            QVERIFY(QMetaObject::invokeMethod(picker,"accept"));QTest::qWait(30);'
assert needle in s;s=s.replace(needle,needle+'''
            QCOMPARE(panel->property("configuration").value<QJSValue>().property("chordColor").toString(),QString("#224466"));''',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Real preview double-click and accepted color assertions added')
