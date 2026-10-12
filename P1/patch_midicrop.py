# coding: utf-8
"""D: minimal export source metadata and preference registration; default MIDI unchanged."""
from pathlib import Path
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def patch():
 p=HOST/'audio/exports/exportmidi.cpp';s=p.read_text(encoding='utf8')
 if 'tag.sourceTick' not in s:
  s=s.replace('#include "libmscore/measure.h"','#include "libmscore/measure.h"\n#include "libmscore/segment.h"')
  s=s.replace('tag.channel = channel; tag.staff = staffIdx; tag.voice = note->chord()->track();', '''tag.channel = channel; tag.staff = staffIdx; tag.voice = staffIdx*VOICES+note->voice();
                                                tag.sourceTick = note->chord()->tick().ticks();
                                                tag.sourceMeasure = note->chord()->measure()->no()+1;
                                                int highest = note->ppitch();
                                                auto onset = note->chord()->segment();
                                                for(int t=part->startTrack();t<part->endTrack();++t) {
                                                      auto element=onset->element(t);if(!element||!element->isChord())continue;
                                                      for(auto candidate:toChord(element)->notes())if(!candidate->tieBack())highest=qMax(highest,candidate->ppitch());
                                                      }
                                                tag.melody = note->ppitch()>=highest;''')
  p.write_bytes(s.encode('utf8'))
 p=HOST/'mscore/preferences.cpp';s=p.read_text(encoding='utf8')
 if '"export/midi/cropFromMeasure"' not in s:
  s=s.replace('{"export/midi/cropSeed", new IntPreference(13013)},','''{"export/midi/cropSeed", new IntPreference(13013)},
            {"export/midi/cropFromMeasure", new IntPreference(0)},
            {"export/midi/cropUntilMeasure", new IntPreference(0)},
            {"export/midi/cropVoices", new StringPreference("")},
            {"export/midi/cropProtectedVoices", new StringPreference("")},
            {"export/midi/cropProtectMelody", new BoolPreference(false)},''')
  p.write_bytes(s.encode('utf8'))
 print('D export value metadata and isolated preferences registered.')
if __name__=='__main__':patch()
