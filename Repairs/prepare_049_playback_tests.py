from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
name='mtest/mscore/performanceeditor/tst_performanceeditor.cpp';p=root/'native'/name
s=p.read_text(encoding='utf8')
s='#include "mscore/workflow/playbackpreview.h"\n#include "mscore/workflow/workflowcontext.h"\n#include "mscore/workflow/referencebus.h"\n'+s
at='      void arpeggioRealSequencerPreRoll()'
assert s.count(at)==1
s=s.replace(at,'#ifdef Q_MOC_RUN\n      void expressionPlaybackKeepsScoreAndBeat();\n#else\n#include "expression_playback_tests.inc"\n#endif\n'+at)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mtest/mscore/performanceeditor/expression_playback_tests.inc';(host/name).write_bytes((root/'native'/name).read_bytes())
name='mscore/workflow/workflowexpression.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
s=s.replace('for(auto note:_score->selection().noteList())notes.append(describe(note,note->ppitch()));','for(auto note:_score->selection().noteList()){auto value=describe(note,note->ppitch());if(note->chord()->isGrace()&&note->chord()->parent()&&note->chord()->parent()->isChord())value["graceIndex"]=toChord(note->chord()->parent())->graceNotes().indexOf(note->chord());notes.append(value);}')
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
print('Real sequencer comparison test added')
