"""One-time guarded development step; do not reapply to released sources."""
from pathlib import Path
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as out: out.write(text)
path=repo/'mscore/plugin/api/scoreobserver.cpp'
s=path.read_text(encoding='utf-8')
needle='record(entry.chordColor,glyphs.chordPicture);record(entry.highlightColor,glyphs.activeChordPicture);'
assert needle in s and 'glyphs.chordPicture.data()' not in s
s=s.replace(needle,needle+'''
                        // Include rendered bytes: score style/font/chord-list edits must invalidate equal-sized glyphs.
                        glyphs.renderedChordKey += QCryptographicHash::hash(
                              QByteArray(glyphs.chordPicture.data(),glyphs.chordPicture.size()),QCryptographicHash::Sha256).toHex();''')
write(path,s)
path=repo/'mtest/mscore/scoreobserver/tst_scoreobserver.cpp'
s=path.read_text(encoding='utf-8')
s=s.replace('#include "libmscore/tie.h"','#include "libmscore/tie.h"\n#include "libmscore/measure.h"')
needle='      void boundedPedalMetadataAndNativeRenderingIsolation()'
assert needle in s and 'tiedAttackAcrossBar' not in s
s=s.replace(needle,'''      void tiedAttackAcrossBar()
            {
            std::unique_ptr<MasterScore> score(readScore("libmscore/inputrhythm/blank.mscx"));
            QVERIFY(score);score->startCmd();
            score->setNoteRest(score->firstMeasure()->first(SegmentType::ChordRest),0,NoteVal(60),Fraction(1,1));
            score->setNoteRest(score->tick2segment(Fraction(1,1),false,SegmentType::ChordRest),0,NoteVal(60),Fraction(1,4));
            auto before=toChord(score->findCR(Fraction(),0))->findNote(60);
            auto after=toChord(score->findCR(Fraction(1,1),0))->findNote(60);
            auto tie=new Tie(score.get());tie->setStartNote(before);tie->setEndNote(after);
            tie->setTick(Fraction());tie->setTick2(Fraction(1,1));tie->setTrack(0);score->undoAddElement(tie);score->endCmd();
            auto pedal=new Pedal(score.get());pedal->setTrack(0);pedal->setTick(Fraction());
            pedal->setTick2(Fraction::fromTicks(2400));score->addElement(pedal);
            PluginAPI::Score wrapped(score.get());PluginAPI::ScoreObserver observer;observer.setScore(&wrapped);
            const auto context=observer.contextSnapshot(1920,0,8,true,0);
            const auto notes=context.value("analysisNotes").toList();QVERIFY(!notes.isEmpty());
            QCOMPARE(notes.front().toMap().value("attackTick").toInt(),0);
            QCOMPARE(context.value("pedalWindows").toList().front().toMap().value("start").toInt(),0);
            }

'''+needle)
write(path,s)
