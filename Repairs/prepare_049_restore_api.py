from pathlib import Path
import shutil
HOST=Path(r'E:/programming/funcodes/muse3_dev/MuseScore')
ROOT=Path(__file__).resolve().parent
for name in ['libmscore/velocitybackup.cpp','libmscore/velocitybackup.h']:
 shutil.copy2(ROOT/'native'/name,HOST/name)
name='mscore/plugin/api/scoreobserver.h';p=HOST/name;s=p.read_text(encoding='utf-8');needle='      Q_INVOKABLE QVariantMap applyExpression(const QVariantMap& candidate);';assert s.count(needle)==1;s=s.replace(needle,needle+'''
      Q_INVOKABLE QVariantMap expressionVelocityHistory(const QVariantMap& range);
      Q_INVOKABLE QVariantMap restoreExpressionVelocity(const QVariantMap& range);
      Q_INVOKABLE QVariantMap saveCurrentExpressionVelocity(const QVariantMap& range);''');p.write_text(s,encoding='utf-8',newline='\n');(ROOT/'native'/name).write_bytes(p.read_bytes())
name='mscore/workflow/workflowexpression.cpp';p=HOST/name;s=p.read_text(encoding='utf-8');s=s.replace('#include "libmscore/undo.h"','#include "libmscore/undo.h"\n#include "libmscore/velocitybackup.h"\n#include "libmscore/select.h"');needle=' return {{"ok",true},{"changed",velocities.size()+bpm.size()},{"durationError",error},{"duration",newDuration}};';assert needle in s;s=s.replace(needle,'''
 QVariantList appliedValues;
 for(auto value:values){auto item=value.toMap();auto note=noteAt(_score,item);item["oldType"]=int(note->veloType());item["oldRaw"]=note->veloOffset();item["oldBase"]=NoteVelocity::referenceBase(note);appliedValues.append(item);}
 return {{"ok",true},{"changed",velocities.size()+bpm.size()},{"durationError",error},{"duration",newDuration},{"revision",analysisRevision()},{"appliedVelocity",appliedValues}};''')
at=s.rfind('\n}}');assert at>=0
code=r'''
namespace {
bool insideHistoryRange(Ms::Score* score, Ms::Note* note, const QVariantMap& range) {
 const int tick=note->chord()->tick().ticks();
 if(tick<range.value("start",0).toInt() || tick>=range.value("end",score->lastMeasure()->endTick().ticks()).toInt() || note->track()<range.value("firstTrack",0).toInt() || note->track()>=range.value("endTrack",score->ntracks()).toInt())return false;
 return !range.value("selectedOnly").toBool() || score->selection().noteList().contains(note);
}
}
QVariantMap ScoreObserver::expressionVelocityHistory(const QVariantMap& range) {
 if(!_score || !_score->lastMeasure())return {{"count",0}};
 int count=0;for(auto note:VelocityBackup::notes(_score))if(insideHistoryRange(_score,note,range))++count;
 return {{"count",count},{"revision",analysisRevision()}};
}
QVariantMap ScoreObserver::restoreExpressionVelocity(const QVariantMap& range) {
 if(!_score || !idle())return {{"error",tr("停止播放后即可恢复力度。")}};
 if(_score->readOnly())return {{"error",tr("请在可编辑的乐谱中恢复力度。")}};
 if(range.value("revision").toString()!=analysisRevision())return {{"error",tr("乐谱刚有修改，请刷新这一区域后恢复。")}};
 auto notes=VelocityBackup::notes(_score);QList<Ms::Note*> targets;
 for(auto note:notes)if(insideHistoryRange(_score,note,range)){auto old=VelocityBackup::original(note);if(int(note->veloType())!=old.first || note->veloOffset()!=old.second)targets.append(note);}
 if(targets.isEmpty())return {{"ok",true},{"changed",0},{"revision",analysisRevision()}};
 _score->startCmd();for(auto note:targets){auto old=VelocityBackup::original(note);note->undoChangeProperty(Pid::VELO_TYPE,old.first);note->undoChangeProperty(Pid::VELO_OFFSET,old.second);}_score->endCmd();
 return {{"ok",true},{"changed",targets.size()},{"revision",analysisRevision()}};
}
QVariantMap ScoreObserver::saveCurrentExpressionVelocity(const QVariantMap& range) {
 if(!_score || !idle())return {{"error",tr("停止播放后即可保存当前力度。")}};
 if(_score->readOnly())return {{"error",tr("请在可编辑的乐谱中保存力度起点。")}};
 if(range.value("revision").toString()!=analysisRevision())return {{"error",tr("乐谱刚有修改，请刷新这一区域后保存。")}};
 QList<Ms::Note*> targets;const int start=range.value("start",0).toInt(),end=range.value("end",_score->lastMeasure()->endTick().ticks()).toInt();
 auto measure=_score->tick2measure(Fraction::fromTicks(start));
 for(auto segment=measure?measure->first(SegmentType::ChordRest):nullptr;segment&&segment->tick().ticks()<end;segment=segment->next1(SegmentType::ChordRest))
  for(int track=range.value("firstTrack",0).toInt();track<range.value("endTrack",_score->ntracks()).toInt();++track){auto e=segment->element(track);if(!e||!e->isChord())continue;auto chords=toChord(e)->graceNotes();chords.append(toChord(e));for(auto chord:chords)for(auto note:chord->notes())if(insideHistoryRange(_score,note,range))targets.append(note);}
 _score->startCmd();for(auto note:targets)VelocityBackup::remember(_score,note,true);_score->endCmd();
 return {{"ok",true},{"changed",targets.size()},{"revision",analysisRevision()}};
}
'''
s=s[:at]+code+s[at:];p.write_text(s,encoding='utf-8',newline='\n');(ROOT/'native'/name).write_bytes(p.read_bytes());print('Velocity restore APIs prepared')
