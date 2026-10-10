# -*- coding: utf-8 -*-
"""Task-only host regressions and runtime synchronization; preserves unrelated files."""
from pathlib import Path
import xml.etree.ElementTree as ET
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
base=Path(__file__).resolve().parents[1]
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as stream:stream.write(text)
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8')
assert 'void highTrebleAndTempoKeepMarkers()' not in s
s=s.replace('#include <QSettings>','#include <QSettings>\n#include <QLabel>\n#include "mscore/mssplashscreen.h"\n#include "mscore/musescoredialogs.h"\n#include "personalbranding.h"',1)
needle='      void denseMarkersKeepTickAndNativeFont()'
s=s.replace(needle,'''      void currentPersonalBranding()
            {
            QFile version(QString(TESTROOT)+"/personal/VERSION");QVERIFY(version.open(QIODevice::ReadOnly));
            QCOMPARE(QString::fromUtf8(version.readAll()).trimmed(),QString(KUMO_PERSONAL_VERSION));
            AboutBoxDialog about;about.show();QTest::qWait(25);
            const auto label=about.findChild<QLabel*>("versionLabel");QVERIFY(label);
            QVERIFY(label->text().contains(personalBuildLabel()));
            const auto credits=about.findChild<QLabel*>("copyrightLabel");QVERIFY(credits);
            QVERIFY(credits->text().contains(personalReleaseUrl()));
            const QDir artifacts(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path()));
            about.grab().save(artifacts.filePath("kumo-about-022.png"));about.hide();
            MsSplashScreen splash;splash.show();QTest::qWait(30);
            splash.grab().save(artifacts.filePath("kumo-splash-022.png"));splash.hide();
            }
      void highTrebleAndTempoKeepMarkers()
            {
            auto main=Ms::mscore;
            auto score=main->readScore(QString(TESTROOT)+"/mtest/mscore/scoreobserver/high-treble.mscx");
            QVERIFY(score);main->setCurrentScoreView(main->appendScore(score));
            main->resize(1100,800);main->show();QTest::qWait(30);
            auto view=main->currentScoreView();PluginAPI::Score wrapped(score);
            PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            auto first=observer.snapshot(0,4,8).value("notes").toList().front().toMap();
            first["chord"]="G";first["degree"]="I";first["chordTick"]=0;first["chordUntil"]=480;
            auto second=first;second["chord"]="D/F#";second["degree"]="V";
            second["chordTick"]=480;second["chordUntil"]=960;
            observer.setScorePreview({first,second});
            QCOMPARE(observer.previewStatus().value("hidden").toInt(),0);
            const auto segment=score->tick2segment(Fraction::fromTicks(480),false,SegmentType::ChordRest);
            QVERIFY(segment);const auto page=segment->measure()->system()->page();
            const qreal x=segment->pagePos().x()+page->pos().x()+score->spatium()*.3;
            QSignalSpy activated(&observer,&PluginAPI::ScoreObserver::previewActivated);
            bool found=false;
            for(qreal y=page->pos().y();y<segment->pagePos().y()+page->pos().y();y+=1)
                  if(view->activateNotePreview(QPointF(x,y)) && activated.last().front().toInt()==480)found=true;
            QVERIFY(found);observer.setActiveScorePreview(480);
            view->grab().save(QDir(qEnvironmentVariable("HARMONY_TEST_ARTIFACTS",_settings.path())).filePath("high-treble-tempo.png"));
            main->hide();
            }
''' +needle,1)
write(p,s)
tree=ET.parse(str(repo/'mtest/mscore/scoreobserver/piano.mscx'))
voice=tree.find("./Score/Staff[@id='1']/Measure/voice")
tempo=ET.Element('Tempo');ET.SubElement(tempo,'tempo').text='1.333333';ET.SubElement(tempo,'text').text='♩ = 80  Con dolce nostalgia'
voice.insert(2,tempo)
rest=voice.find('Rest');at=list(voice).index(rest);voice.remove(rest)
chord=ET.Element('Chord');ET.SubElement(chord,'durationType').text='quarter'
for pitch,tpc in [(79,15),(86,16)]:
    note=ET.SubElement(chord,'Note');ET.SubElement(note,'pitch').text=str(pitch);ET.SubElement(note,'tpc').text=str(tpc)
voice.insert(at,chord)
for note,pitch,tpc in zip(voice.findall('Chord')[1].findall('Note'),[79,83,86],[15,19,16]):
    note.find('pitch').text=str(pitch);note.find('tpc').text=str(tpc)
tree.write(str(repo/'mtest/mscore/scoreobserver/high-treble.mscx'),encoding='utf-8',xml_declaration=True)
for p in base.iterdir():
    if p.suffix in ('.qml','.js') or p.name=='README.md':
        (repo/'share/plugins/HarmonyAssistant'/p.name).write_bytes(p.read_bytes())
print('Added real high-treble/tempo layout and version branding regressions; synchronized runtime')
