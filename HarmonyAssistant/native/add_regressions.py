"""Extend native regression coverage, including the actual Widgets/QML host path."""
from pathlib import Path
R=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=R/'mtest/mscore/scoreobserver/tst_scoreobserver.cpp'
s=p.read_text(encoding='utf-8').replace('#include "libmscore/undo.h"','#include "libmscore/undo.h"\n#include "libmscore/pedal.h"')
marker='      void previewDoesNotChangeScoreOrExport()'
tests='''      void pedalReleaseAndAnalysisFrames()
            {
            std::unique_ptr<MasterScore> score(readScore("mscore/scoreobserver/piano.mscx"));
            auto pedal = new Pedal(score.get());
            pedal->setTick(Fraction::fromTicks(0));
            pedal->setTicks(Fraction::fromTicks(1440));
            pedal->setTrack(4); pedal->setTrack2(4);
            score->addSpanner(pedal);
            PluginAPI::Score wrapped(score.get());
            PluginAPI::ScoreObserver observer; observer.setScore(&wrapped);
            QCOMPARE(observer.snapshot(1000,0,8).value("notes").toList().size(),0);
            QCOMPARE(observer.contextSnapshot(1000,0,8,true,0).value("analysisNotes").toList().size(),6);
            QCOMPARE(observer.contextSnapshot(1000,0,8,false,0).value("analysisNotes").toList().size(),0);
            QCOMPARE(observer.contextSnapshot(1440,0,8,true,0).value("analysisNotes").toList().size(),0);
            QCOMPARE(observer.contextSnapshot(1000,0,4,true,0).value("analysisNotes").toList().size(),3);
            const auto first=observer.analysisFrames(0,2,0,8,true,0);
            QCOMPARE(first.value("frames").toList().size(),2);
            QVERIFY(first.value("nextTick").toInt()>0);
            QCOMPARE(first.value("fingerprint").toString().size(),64);
            const auto rest=observer.analysisFrames(first.value("nextTick").toInt(),128,0,8,true,0);
            QCOMPARE(rest.value("nextTick").toInt(),-1);
            QCOMPARE(first.value("fingerprint"),rest.value("fingerprint"));
            }
      void arpeggioWindowAndRest()
            {
            std::unique_ptr<MasterScore> score(readScore("mscore/scoreobserver/arpeggio.mscx"));
            QVERIFY(score);
            PluginAPI::Score wrapped(score.get());
            PluginAPI::ScoreObserver observer; observer.setScore(&wrapped);
            QCOMPARE(observer.snapshot(960,0,8).value("notes").toList().size(),1);
            QCOMPARE(observer.contextSnapshot(960,0,8,false,960).value("analysisNotes").toList().size(),3);
            QCOMPARE(observer.contextSnapshot(960,0,8,false,0).value("analysisNotes").toList().size(),1);
            QCOMPARE(observer.contextSnapshot(1440,0,8,false,1920).value("analysisNotes").toList().size(),0);
            }
      void atomicConfigurationRoundTrip()
            {
            QStandardPaths::setTestModeEnabled(true);
            PluginAPI::ScoreObserver observer;
            QVariantMap value {{"schema",1},{"label",QString::fromUtf8("降七")}};
            QVERIFY(observer.saveConfiguration("HarmonyAssistantRegression",value));
            QCOMPARE(observer.loadConfiguration("HarmonyAssistantRegression"),value);
            QVERIFY(!observer.saveConfiguration("../invalid",value));
            QTemporaryDir directory;
            const auto path=directory.filePath("analysis.json");
            QVERIFY(observer.writeTextFile(QUrl::fromLocalFile(path).toString(),QString::fromUtf8("和弦")));
            QCOMPARE(observer.readTextFile(path),QString::fromUtf8("和弦"));
            }
'''
assert marker in s;s=s.replace(marker,tests+marker)
s=s.replace('#include <QTemporaryDir>','#include <QTemporaryDir>\n#include <QStandardPaths>\n#include <QUrl>')
write(p,s)
write(R/'mtest/mscore/scoreobserver/arpeggio.mscx',Path(__file__).with_name('arpeggio.mscx').read_text(encoding='utf-8'))

p=R/'mtest/CMakeLists.txt';s=p.read_text(encoding='utf-8');assert '        mscore/scoreobserver\n' in s
write(p,s.replace('        mscore/scoreobserver\n','        mscore/scoreobserver\n        mscore/pluginhost\n'))
write(R/'mtest/mscore/pluginhost/CMakeLists.txt','set(TARGET tst_pluginhost)\nset(MTEST_LINK_MSCOREAPP TRUE)\ninclude(${PROJECT_SOURCE_DIR}/mtest/CreateMtestTarget.cmake)\n')
write(R/'mtest/mscore/pluginhost/tst_pluginhost.cpp',Path(__file__).with_name('tst_pluginhost.cpp').read_text(encoding='utf-8'))
