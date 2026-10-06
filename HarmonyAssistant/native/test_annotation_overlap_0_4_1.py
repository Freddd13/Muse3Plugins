# -*- coding: utf-8 -*-
"""One-time native GUI regression additions for priority and editor overlap."""
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
s=s.replace('#include "libmscore/chord.h"','#include "libmscore/chord.h"\n#include "libmscore/harmony.h"',1)
needle='''      };
QTEST_MAIN(TestPluginHost)'''
addition='''      void annotationPrioritiesWhileMoving()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();QTest::qWait(50);
            auto view=main->currentScoreView();
            PluginAPI::Score wrapped(score);PluginAPI::ScoreObserver observer;
            observer.setScore(&wrapped);
            auto segment=score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest);
            auto harmony=new Harmony(score);harmony->setTrack(0);segment->add(harmony);
            harmony->setHarmony("F7");score->doLayout();QTest::qWait(20);
            QVariantMap anchor;
            for (const auto& descriptor:observer.snapshot(480,0,8).value("notes").toList()) {
                  const auto value=descriptor.toMap();
                  if(value.value("tick").toInt()==480 && value.value("track").toInt()==0){anchor=value;break;}
                  }
            QVERIFY(!anchor.isEmpty());anchor["chord"]="Cmaj13";anchor["degree"]="Imaj13";
            anchor["chordTick"]=480;anchor["chordUntil"]=960;anchor["preferExistingHarmony"]=true;
            const auto baseline=view->grab().toImage();
            auto onlyChord=anchor;onlyChord["degree"]="";
            observer.setScorePreview({onlyChord});
            QCOMPARE(view->grab().toImage(),baseline); // native F7 remains, duplicate analysis stays in panel
            observer.setScorePreview({anchor});const auto preferred=view->grab().toImage();
            auto degreeOnly=anchor;degreeOnly["chord"]="";
            observer.setScorePreview({degreeOnly});QCOMPARE(view->grab().toImage(),preferred);
            QVERIFY(preferred!=baseline);
            auto simultaneous=anchor;simultaneous["preferExistingHarmony"]=false;
            observer.setScorePreview({simultaneous});QVERIFY(view->grab().toImage()!=preferred);
            // Roman notation retains its own degree while optionally supplementing chord analysis.
            observer.clearAllPreviews();harmony->setHarmonyType(HarmonyType::ROMAN);
            harmony->setHarmony("V7");score->doLayout();
            observer.setScorePreview({anchor});const auto romanPreferred=view->grab().toImage();
            onlyChord["preferExistingHarmony"]=false;observer.setScorePreview({onlyChord});
            QCOMPARE(view->grab().toImage(),romanPreferred);
            observer.clearAllPreviews();harmony->setHarmonyType(HarmonyType::STANDARD);
            harmony->setHarmony("F7");score->doLayout();
            observer.setScorePreview({simultaneous});
            const auto note=toChord(segment->element(0))->notes().front();
            QPointF hit;bool found=false;
            for(int dy=-qRound(note->spatium()*24);dy<0 && !found;dy+=2)
                  for(int dx=2;dx<note->spatium()*12;dx+=2) {
                        const auto point=note->canvasPos()+QPointF(dx,dy);
                        if(view->activateNotePreview(point)){hit=point+QPointF(8,8);found=true;break;}
                        }
            QVERIFY(found);
            // Moving selection / changing current function text must not repaint fixed chord text.
            const auto fixedArea=view->toPhysical(QRectF(hit-QPointF(8,8),QSizeF(note->spatium()*9,note->spatium()*2)));
            const auto fixedPixels=view->grab(fixedArea).toImage();
            for(int tick:{0,480,0,480}) {
                  auto current=observer.snapshot(tick,0,8).value("notes").toList();
                  for(auto& descriptor:current){auto d=descriptor.toMap();d["label"]=tick==0 ? "5" : "thirteen";descriptor=d;}
                  observer.setNotePreviewColors(current);
                  QCOMPARE(view->grab(fixedArea).toImage(),fixedPixels);
                  }
            observer.clearNotePreviewColors();
            // Move a native editor over an already cached preview: editor and its caret take priority.
            harmony->setOffset(harmony->offset()+hit-harmony->canvasBoundingRect().center());
            view->startEditMode(harmony);QVERIFY(view->textEditMode());
            QTest::keyClick(view,Qt::Key_Right);
            const auto editedWithPreview=view->grab().toImage();
            QVERIFY(!view->activateNotePreview(hit));
            observer.clearAllPreviews();
            QCOMPARE(view->grab().toImage(),editedWithPreview);
            view->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("native-editor-priority.png"));
            view->changeState(ViewState::NORMAL);main->hide();
            }
      };
QTEST_MAIN(TestPluginHost)'''
assert needle in s;s=s.replace(needle,addition,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Real GUI priority, selection movement, native notation and caret regressions added.')
