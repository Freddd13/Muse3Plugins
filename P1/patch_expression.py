"""B2 edits to existing parameter editing: preserve old APIs, share preflight/transaction."""
from pathlib import Path
HOST=Path(r"E:\programming\funcodes\muse3_dev\MuseScore")
def patch():
 p=HOST/'mscore/performanceeditor/parameteredit.cpp';s=p.read_text(encoding='utf8')
 if 'bool expression(' not in s:
  s=s.replace('bool velocities(Score* score, const QMap<Note*, VelocityEdit>& edits)','static bool velocitiesImpl(Score* score, const QMap<Note*, VelocityEdit>& edits,bool ownCommand,bool dryRun)')
  s=s.replace('      if (!changed) return false;\n      score->startCmd();','      if(dryRun)return true;\n      if (!changed) return false;\n      if(ownCommand)score->startCmd();',1)
  s=s.replace('      score->endCmd();\n      return true;\n      }\n\nbool tempos(', '      if(ownCommand)score->endCmd();\n      return true;\n      }\n\nstatic bool temposImpl(',1)
  s=s.replace('const QMap<int, double>& bpm, int unlockedTick, QString* error)\n', 'const QMap<int, double>& bpm, int unlockedTick, QString* error,bool ownCommand,bool dryRun,bool visibleNew = false)\n',1)
  s=s.replace('      if (points.isEmpty()) return false;\n      score->startCmd();','      if(dryRun)return true;\n      if (points.isEmpty()) return false;\n      if(ownCommand)score->startCmd();',1)
  s=s.replace('text->setVisible(false);','text->setVisible(visibleNew);',1)
  at=s.index('bool tempoCurve(')
  prefix=s[:at]
  # Only temposImpl's final endCmd is conditional, not other existing APIs.
  pos=prefix.rfind('      score->endCmd();');prefix=prefix[:pos]+prefix[pos:].replace('      score->endCmd();','      if(ownCommand)score->endCmd();',1)
  wrappers=r"""bool velocities(Score* score,const QMap<Note*,VelocityEdit>& edits) {return velocitiesImpl(score,edits,true,false);}
bool tempos(Score* score,const QMap<int,double>& bpm,int unlockedTick,QString* error) {return temposImpl(score,bpm,unlockedTick,error,true,false);}
bool expression(Score* score,const QMap<Note*,VelocityEdit>& velocities,const QMap<int,double>& bpm,QString* error) {
 if(!velocitiesImpl(score,velocities,false,true)||!temposImpl(score,bpm,-1,error,false,true))return false;
 score->startCmd();velocitiesImpl(score,velocities,false,false);temposImpl(score,bpm,-1,error,false,false);score->endCmd();return true;
}
bool writeTapTempo(Score* score,int tick,double bpm,bool selectedExisting,QString* error) {
 if(!editable(score))return false;
 auto segment=score->masterScore()->tick2segment(Fraction::fromTicks(tick),false,SegmentType::ChordRest);
 if(!segment){if(error)*error=QObject::tr("请选取实际音符／休止位置。");return false;}
 for(auto e:segment->annotations())if(e->isTempoText()&&!selectedExisting){if(error)*error=QObject::tr("此处已有速度记号，请直接选中目标后再写入。");return false;}
 return temposImpl(score,{{tick,bpm}},selectedExisting?tick:-1,error,true,false,true);
}

"""
  p.write_bytes((prefix+wrappers+s[at:]).encode('utf8'))
 p=HOST/'mscore/performanceeditor/parameteredit.h';s=p.read_text(encoding='utf8')
 if 'bool expression(' not in s:
  s=s.replace('namespace ParameterEdit {','namespace ParameterEdit {\nbool expression(Score*,const QMap<Note*,VelocityEdit>&,const QMap<int,double>&,QString* error = nullptr);\nbool writeTapTempo(Score*,int tick,double bpm,bool selectedExisting,QString* error = nullptr);')
  p.write_bytes(s.encode('utf8'))
 p=HOST/'mscore/taptempo/taptempo.cpp';text=p.read_text(encoding='utf8')
 if 'showTapWriteDialog' not in text:
  text=text.replace('#include "taptempo.h"','#include "taptempo.h"\n#include "mscore/workflow/tapwrite.h"\n#include "libmscore/score.h"')
  text=text.replace('      auto item = new QWidgetAction(menu);','      auto write = new QPushButton(tr("写入指定谱面位置…"),body);grid->addWidget(write,6,0,1,3);\n      connect(write,&QPushButton::clicked,this,[this]{const double bpm=_estimate.bpm(_quarterBeats)*_multiplier;if(_estimate.ready()&&bpm>=5&&bpm<=999)showTapWriteDialog(mscore->currentScore(),bpm);});\n      connect(menu,&QMenu::aboutToShow,write,[this,write]{const double bpm=_estimate.bpm(_quarterBeats)*_multiplier;write->setEnabled(_estimate.ready()&&bpm>=5&&bpm<=999&&mscore->currentScore()&&(!seq||(!seq->isPlaying()&&seq->backgroundRenderingIdle())));});\n      auto item = new QWidgetAction(menu);',1)
  p.write_bytes(text.encode('utf8'))
 # A one-call explicit transport start; normal start semantics unchanged.
 p=HOST/'mscore/seq.h';text=p.read_text(encoding='utf8')
 if 'startAtUTick' not in text:
  text=text.replace('      void start();','      void start();\n      void startAtUTick(int utick);',1)
  text=text.replace('      int getPlayStartUtick();','      int getPlayStartUtick();\n      int _workflowStartUTick = -1;',1);p.write_bytes(text.encode('utf8'))
 p=HOST/'mscore/seq.cpp';text=p.read_text(encoding='utf8')
 if 'void Seq::startAtUTick' not in text:
  at=text.index('void Seq::start()')
  text=text[:at]+'void Seq::startAtUTick(int utick) {\n      if(!cs || isPlaying() || utick<0 || utick>cs->repeatList().ticks())return;\n      _workflowStartUTick=utick;start();_workflowStartUTick=-1;\n      }\n\n'+text[at:]
  text=text.replace('int Seq::getPlayStartUtick()\n      {','int Seq::getPlayStartUtick()\n      {\n      if(_workflowStartUTick>=0)return _workflowStartUTick;',1);p.write_bytes(text.encode('utf8'))
 print('B2 shared preflight and one-command editing prepared.')
if __name__=='__main__':patch()
