from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;N=ROOT/'Repairs/native';HOST=ROOT.parent/'muse3_dev/MuseScore'
def mirror(name):
 p=N/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HOST/name).read_bytes())
 return p
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:60];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=mirror('mscore/workflow/workflowcontext.h');edit(p,'      QPointer<Score> _score;','      QPointer<Score> _score, _activeScore;');edit(p,'      QVariantMap expression()const','      void setActiveScore(Score* score){if(_activeScore==score)return;_activeScore=score;emit activeScoreChanged();}\n      QVariantMap expression()const');edit(p,'      void changed();','      void changed();\n      void activeScoreChanged();');edit(p,'WorkflowContext* workflowContext();','WorkflowContext* workflowContext();\nvoid notifyWorkflowCurrentScore(Score*);')
p=mirror('mscore/workflow/workflowcontext.cpp');s=p.read_text(encoding='utf8');old='WorkflowContext* workflowContext(){static QPointer<WorkflowContext> context;if(!context)context=new WorkflowContext(qApp);return context;}'
new='''namespace { QPointer<WorkflowContext> context; }
WorkflowContext* workflowContext(){if(!context)context=new WorkflowContext(qApp);return context;}
void notifyWorkflowCurrentScore(Score* score){if(context)context->setActiveScore(score);}'''
edit(p,old,new)
p=mirror('mscore/plugin/api/scoreobserver.h');edit(p,'      void scoreChanged();','      void scoreChanged();\n      void activeScoreChanged();')
p=mirror('mscore/plugin/api/scoreobserver.cpp');edit(p,'#include "mscore/scoreview.h"','#include "mscore/scoreview.h"\n#include "mscore/workflow/workflowcontext.h"');edit(p,'      watchSurface();','''      auto context=workflowContext();context->setActiveScore(mscore?mscore->currentScore():nullptr);
      connect(context,&WorkflowContext::activeScoreChanged,this,&ScoreObserver::activeScoreChanged);
      watchSurface();''')
p=ROOT/'Repairs/apply_native.py';edit(p," patch('mscore/seq.cpp','#include \"seq.h\"'", " patch('mscore/musescore.cpp','#include \"musescore.h\"','#include \"musescore.h\"\\n#include \"workflow/workflowcontext.h\"')\n patch('mscore/musescore.cpp','      if (_performanceEditor) _performanceEditor->setView(cv);','      if (_performanceEditor) _performanceEditor->setView(cv);\\n      notifyWorkflowCurrentScore(cs);')\n patch('mscore/seq.cpp','#include \"seq.h\"'")
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';edit(p,'        onScoreChanged:root.newScore()','        onScoreChanged:root.newScore()\n        onActiveScoreChanged:root.newScore()')
p=ROOT/'HarmonyAssistant/HarmonyAssistant_MS3.qml';edit(p,'        onScoreChanged:requestRefresh(true)','        onScoreChanged:requestRefresh(true)\n        onActiveScoreChanged:requestRefresh(true)')
