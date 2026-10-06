# -*- coding: utf-8 -*-
"""One-time real two-marker alignment and bass-anchor check."""
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
needle='            observer->setScorePreview({anchor});\n            const auto note='
replacement='''            auto firstMarker=observer->snapshot(0,4,8).value("notes").toList().front().toMap();
            firstMarker["chord"]="C";firstMarker["degree"]="I";firstMarker["chordTick"]=0;firstMarker["chordUntil"]=480;firstMarker["chordOrder"]=2;
            observer->setScorePreview({firstMarker,anchor});
            const auto note='''
assert needle in s;s=s.replace(needle,replacement,1)
s=s.replace('            observer->setScorePreview({anchor});QTest::qWait(20);','            observer->setScorePreview({firstMarker,anchor});QTest::qWait(20);',1)
needle='            scoreView->grab().save('
extension='''            const auto bass=toChord(score->firstSegment(SegmentType::ChordRest)->element(4))->notes().front();
            observer->setScorePreview({firstMarker,anchor});
            QPointF bassHit;bool bassFound=false;
            for(int dy=-200;dy<0 && !bassFound;dy+=2) for(int dx=2;dx<40;dx+=2) {
                  const auto candidate=bass->canvasPos()+QPointF(dx,dy);
                  if(scoreView->activateNotePreview(candidate)){bassHit=candidate;bassFound=true;break;}
                  }
            QVERIFY(bassFound);QVERIFY(qAbs(bassHit.y()-hitPoint.y())<=2.0);
            QCOMPARE(panel->property("currentTick").toInt(),0);
            observer->setScorePreview({firstMarker,anchor});observer->setActiveScorePreview(600);QTest::qWait(30);
'''
assert needle in s;s=s.replace(needle,extension+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Shared-row and bass-anchor checks added')
