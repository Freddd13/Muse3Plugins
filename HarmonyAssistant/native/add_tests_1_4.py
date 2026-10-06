from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
base=Path(__file__).resolve().parents[1]
names=['HarmonyAssistant_MS3.qml','Harmony.js','Preferences.js','Analysis.js','ConfigurationEditor.qml',
       'SettingsStore.qml','PanelCard.qml','UiLabel.qml','StableLabel.qml','ColorOption.qml','AppearanceEditor.qml',
       'Timeline.js','RangeEditor.qml']
for name in names:
    target=repo/'share/plugins/HarmonyAssistant'/name
    if target.exists():
        old=base/'backups/1.3.0'/(name+'.bak')
        assert old.exists() and target.read_text(encoding='utf-8').replace('\r\n','\n')==old.read_text(encoding='utf-8').replace('\r\n','\n'),name
for name in names:(repo/'share/plugins/HarmonyAssistant'/name).write_bytes((base/name).read_bytes())
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8')
assert 'root->version()=="1.3.0"' in s
s=s.replace('root->version()=="1.3.0"','root->version()=="1.4.0"')
extra=r'''
      void nativeStateColorsAndRangeFrame()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();QTest::qWait(30);
            auto view=main->currentScoreView();PluginAPI::Score wrapped(score);
            PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            auto descriptors=observer.snapshot(480,0,4).value("notes").toList();
            auto segment=score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest);
            auto note=toChord(segment->element(0))->notes().front();
            auto d=descriptors.front().toMap();d["color"]="#9f1853";
            for(int state=0;state<3;++state) {
                  note->setSelected(state==0);note->setMark(state==1);note->setDropTarget(state==2);
                  observer.clearAllPreviews();view->update();QTest::qWait(10);
                  const auto baseline=view->grab().toImage();
                  observer.setNotePreviewColors({d});view->update();QTest::qWait(10);
                  QCOMPARE(view->grab().toImage(),baseline);
                  }
            note->setSelected(false);note->setMark(false);note->setDropTarget(false);
            observer.clearAllPreviews();view->update();QTest::qWait(10);
            const auto original=view->grab().toImage();observer.setNotePreviewColors({d});
            QVERIFY(view->grab().toImage()!=original);
            observer.clearAllPreviews();QCOMPARE(view->grab().toImage(),original);
            score->selectRange(segment,score->lastSegment(),0,1);
            observer.clearAllPreviews();view->update();QTest::qWait(10);
            const auto selected=view->grab().toImage();observer.setNotePreviewColors({d});
            QCOMPARE(view->grab().toImage(),selected);
            view->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("native-range-color.png"));
            main->hide();
            }
      void denseMarkersKeepTickAndNativeFont()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/piano.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();QTest::qWait(30);
            auto view=main->currentScoreView();PluginAPI::Score wrapped(score);
            PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            auto first=observer.snapshot(0,4,8).value("notes").toList().front().toMap();
            first["chord"]="Cmaj7(#11)/E";first["chordTick"]=0;first["chordUntil"]=60;
            auto second=first;second["chord"]="G7(b9)/B";second["chordTick"]=60;second["chordUntil"]=480;
            observer.setScorePreview({first,second});
            QCOMPARE(observer.previewStatus().value("hidden").toInt(),0);
            QSignalSpy activated(&observer,&PluginAPI::ScoreObserver::previewActivated);
            const auto segment=score->firstSegment(SegmentType::ChordRest);
            const auto next=score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest);
            const auto note=toChord(segment->element(4))->notes().front();
            const qreal x0=segment->pagePos().x()+segment->measure()->system()->page()->pos().x();
            const qreal x1=x0+(next->pagePos().x()-segment->pagePos().x())/8;
            QMap<int,qreal> hitYs;
            for(int dy=-qRound(note->spatium()*30);dy<0;dy+=1) {
                  for(const auto anchor:QVector<QPair<int,qreal>>{{0,x0},{60,x1}}) {
                        QPointF point(anchor.second+note->spatium()*.3,note->canvasPos().y()+dy);
                        if(view->activateNotePreview(point) && activated.last().front().toInt()==anchor.first)hitYs.insert(anchor.first,point.y());
                        }
                  }
            QCOMPARE(hitYs.size(),2);QVERIFY(qAbs(hitYs[0]-hitYs[60])>note->spatium());
            observer.setActiveScorePreview(60);
            view->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("dense-native-font.png"));
            const auto normal=view->grab().toImage();first["chordFont"]="Arial";second["chordFont"]="Arial";
            observer.setScorePreview({first,second});QVERIFY(view->grab().toImage()!=normal);
            main->hide();
            }
'''
pos=s.rindex('      };\nQTEST_MAIN');s=s[:pos]+extra+s[pos:]
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=repo/'mtest/mscore/scoreobserver/tst_scoreobserver.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('#include "libmscore/pedal.h"','#include "libmscore/pedal.h"\n#include "libmscore/tie.h"\n#include "libmscore/harmony.h"\n#include "libmscore/chordlist.h"')
extra=r'''
      void boundedPedalMetadataAndNativeRenderingIsolation()
            {
            std::unique_ptr<MasterScore> score(readScore("mscore/scoreobserver/piano.mscx"));
            QVERIFY(score);score->doLayout();
            auto pedal=new Pedal(score.get());pedal->setTrack(4);pedal->setTick(Fraction());
            pedal->setTick2(Fraction::fromTicks(960));score->addElement(pedal);
            PluginAPI::Score wrapped(score.get());PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            const auto context=observer.contextSnapshot(480,0,8,true,0);
            QCOMPARE(context.value("parts").toList().size(),1);
            QCOMPARE(context.value("pedalWindows").toList().size(),1);
            QCOMPARE(context.value("pedalWindows").toList().front().toMap().value("end").toInt(),960);
            QCOMPARE(observer.contextSnapshot(960,0,8,true,0).value("pedalWindows").toList().size(),0);
            for (const auto note:context.value("analysisNotes").toList())
                  QVERIFY(note.toMap().contains("attackTick"));
            const auto state=score->state();
            const auto descriptions=score->style().chordList()->size();
            auto anchor=context.value("analysisNotes").toList().front().toMap();
            anchor["chord"]="C7(b9,#11)/E";anchor["chordTick"]=0;anchor["chordUntil"]=960;
            observer.setScorePreview({anchor});
            QCOMPARE(score->style().chordList()->size(),descriptions);QVERIFY(score->state()==state);
            observer.clearAllPreviews();
            }
'''
pos=s.rindex('      };\nQTEST_MAIN');s=s[:pos]+extra+s[pos:]
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Runtime synced; original native suites retained and regressions appended.')
