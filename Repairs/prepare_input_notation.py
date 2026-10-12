# coding: utf-8
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def mirror(path,old,new):
 dst=ROOT/'native'/path
 text=dst.read_text(encoding='utf8') if dst.exists() else (HOST/path).read_text(encoding='utf8')
 if new in text:return
 assert text.count(old)==1,(path,old,text.count(old))
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(text.replace(old,new).encode('utf8'))
mirror('mscore/inputrhythmpreference.h','constexpr char PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM[] = "ui/score/noteEntry/autoRhythm";','constexpr char PREF_SCORE_NOTE_INPUT_AUTO_RHYTHM[] = "ui/score/noteEntry/autoRhythm";\nconstexpr char PREF_SCORE_TIED_BEAMS[] = "ui/score/notation/tiedBeams";\nconstexpr char PREF_SCORE_COHERENT_TIE_STEMS[] = "ui/score/notation/coherentTieStems";')
mirror('libmscore/inputrhythm.cpp','      if (!cr->isChord()) return false;','      if (!cr->isChord() || cr->beamMode() != Beam::Mode::AUTO) return false;')
test=ROOT/'native/mtest/libmscore/inputrhythm/tst_inputrhythm.cpp'
if not test.exists():
 test.parent.mkdir(parents=True,exist_ok=True);test.write_bytes((HOST/'mtest/libmscore/inputrhythm/tst_inputrhythm.cpp').read_text(encoding='utf8').encode('utf8'))
mirror('mtest/libmscore/inputrhythm/tst_inputrhythm.cpp','#include "libmscore/inputrhythm.h"','#include "libmscore/inputrhythm.h"\n#include "libmscore/inputnotation.h"\n#include "libmscore/beam.h"')
mirror('mtest/libmscore/inputrhythm/tst_inputrhythm.cpp','      void init() { InputRhythm::setEnabled(true); }','      void init() { InputRhythm::setEnabled(true); InputNotation::setTiedBeams(false); InputNotation::setCoherentStems(false); }')
mirror('mtest/libmscore/inputrhythm/tst_inputrhythm.cpp','      void cleanup() { InputRhythm::setEnabled(false); }','      void cleanup() { InputRhythm::setEnabled(false); InputNotation::setTiedBeams(false); InputNotation::setCoherentStems(false); }')
mirror('mtest/libmscore/inputrhythm/tst_inputrhythm.cpp','      void grouping_data()','''#ifdef Q_MOC_RUN
      void quarterChangedAfterDottedQuarter();
      void threeThreeTwoStemsAndManualSettings();
      void manualNoBeamSurvivesDurationChanges();
#else
#include "input_notation_tests.inc"
#endif
      void grouping_data()''')
