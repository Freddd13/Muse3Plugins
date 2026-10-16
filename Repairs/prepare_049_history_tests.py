from pathlib import Path
root=Path(__file__).resolve().parent
host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
name='mtest/mscore/p1native/tst_p1native.cpp'
path=host/name
text=path.read_text(encoding='utf8')
text=text.replace('#include "libmscore/undo.h"','#include "libmscore/undo.h"\n#include "libmscore/velocitybackup.h"')
at=' void guardedExpressionUndoAndStale(){'
assert text.count(at)==1
text=text.replace(at,'#ifdef Q_MOC_RUN\n void expressionVelocitySavedHistory();\n#else\n#include "velocity_history_tests.inc"\n#endif\n'+at)
(root/'native'/name).write_text(text,encoding='utf8',newline='\n');path.write_bytes((root/'native'/name).read_bytes())
name='mtest/mscore/p1native/velocity_history_tests.inc'
(host/name).write_bytes((root/'native'/name).read_bytes())
name='mscore/workflow/workflowexpression.cpp'
path=root/'native'/name;text=path.read_text(encoding='utf8')
for method in ['restoreExpressionVelocity','saveCurrentExpressionVelocity']:
 at='QVariantMap ScoreObserver::'+method+'(const QVariantMap& range) {\n'
 assert text.count(at)==1
 text=text.replace(at,at+' if(mscore&&mscore->currentScore()&&mscore->currentScore()!=_score)return {{"error",tr("切换到要修改的乐谱后继续。")}};\n')
path.write_text(text,encoding='utf8',newline='\n');(host/name).write_bytes(path.read_bytes())
print('Velocity history tests and current-score routing written')
