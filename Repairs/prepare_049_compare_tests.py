from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
name='mtest/mscore/performanceeditor/tst_performanceeditor.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
s='#include <QJsonArray>\n#include <QJsonDocument>\n'+s
s=s.replace('      void expressionPlaybackKeepsScoreAndBeat();','      void expressionPlaybackKeepsScoreAndBeat();\n      void expressionParameterDragAndApply();',1)
s=s.replace('#include "expression_playback_tests.inc"','#include "expression_playback_tests.inc"\n#include "expression_compare_tests.inc"',1)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mtest/mscore/performanceeditor/expression_compare_tests.inc';(host/name).write_bytes((root/'native'/name).read_bytes())
print('Parameter preview mouse editing, selection and one-step score application checks added')
