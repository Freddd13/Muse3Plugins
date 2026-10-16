from pathlib import Path
root=Path(__file__).resolve().parent
host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def load(name):
 p=root/'native'/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((host/name).read_bytes())
 return p.read_text(encoding='utf8')
def save(name,text):
 p=root/'native'/name;p.write_text(text,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
def patch(name,old,new):
 s=load(name);assert s.count(old)==1,(name,old[:70],s.count(old));save(name,s.replace(old,new))
patch('mscore/workflow/workflowcontext.h','      Q_PROPERTY(QString feedback MEMBER _feedback NOTIFY feedbackChanged)','      Q_PROPERTY(QString feedback MEMBER _feedback NOTIFY feedbackChanged)\n      Q_PROPERTY(QVariantMap audition READ audition NOTIFY auditionChanged)\n      QVariantMap _audition;')
patch('mscore/workflow/workflowcontext.h','      QVariantMap expression()const{return _expression;}','      QVariantMap expression()const{return _expression;}\n      QVariantMap audition()const{return _audition;}\n      void setAudition(const QVariantMap& value){_audition=value;emit auditionChanged();}')
patch('mscore/workflow/workflowcontext.h','      void feedbackChanged();','      void feedbackChanged();\n      void auditionChanged();')
patch('mscore/seq.h','      void collectEvents(int utick);','      void invalidatePlaybackEvents() { Q_ASSERT(!isPlaying()); playlistChanged=true; }\n      void collectEvents(int utick);')
s=load('mscore/seq.cpp');s='#include "workflow/playbackpreview.h"\n'+s
start=s.index('void Seq::collectEvents(int utick)');end=s.index('void Seq::ensureBufferAsync',start)
part=s[start:end]
part=part.replace('      if (playlistChanged) {','      const auto preview=activePlaybackPreviewEvents(cs);\n      if(preview){events=*preview;renderEvents.clear();renderEventsStatus.clear();}\n      else if (playlistChanged) {',1)
part=part.replace('      while (unrenderedUtick - utick < minUtickBufferSize) {','      while (!preview && unrenderedUtick - utick < minUtickBufferSize) {',1)
s=s[:start]+part+s[end:]
s=s.replace('void Seq::ensureBufferAsync(int utick)\n      {','void Seq::ensureBufferAsync(int utick)\n      {\n      if(activePlaybackPreviewEvents(cs))return;',1)
save('mscore/seq.cpp',s)
patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/workflowexpression.cpp','    ${PROJECT_SOURCE_DIR}/mscore/workflow/workflowexpression.cpp\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/playbackpreview.h\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/playbackpreview.cpp')
patch('mscore/plugin/api/scoreobserver.h','      Q_INVOKABLE QVariantMap expressionVelocityHistory(const QVariantMap& range);','      Q_INVOKABLE QVariantMap expressionVelocityHistory(const QVariantMap& range);\n      Q_INVOKABLE QVariantMap expressionSelection();\n      Q_INVOKABLE QVariantMap auditionExpression(const QString& workspace,const QVariantMap& candidate,const QVariantMap& scope,bool proposed);\n      Q_INVOKABLE QVariantMap finishExpressionAudition();')
s=load('mscore/workflow/workflowexpression.cpp');s=s.replace('#include "workflowcontext.h"','#include "workflowcontext.h"\n#include "playbackpreview.h"\n#include <QJsonDocument>\n#include <QJsonObject>\n#include <memory>')
index=s.index('QVariantMap ScoreObserver::previewExpression(')
code='''QVariantMap ScoreObserver::expressionSelection(){
 QVariantList notes;if(_score)for(auto note:_score->selection().noteList())notes.append(describe(note,note->ppitch()));
 return {{"scope",analysisScope(false)},{"notes",notes}};
}
QVariantMap ScoreObserver::finishExpressionAudition(){stopPlaybackPreview(true);return {{"ok",true}};}
QVariantMap ScoreObserver::auditionExpression(const QString& workspace,const QVariantMap& candidate,const QVariantMap& scope,bool proposed){
 if(!_score||candidate.value("revision").toString()!=analysisRevision())return {{"error",tr("乐谱已有修改，请更新演奏对应后试听。")}};
 const QString key=analysisRevision()+QString::fromLatin1(QCryptographicHash::hash(QJsonDocument::fromVariant(candidate).toJson(QJsonDocument::Compact),QCryptographicHash::Sha256).toHex());
 if(!playbackPreviewPrepared(_score,key)){
  stopPlaybackPreview();if(seq&&seq->isPlaying())seq->stopWait();if(!idle())return {{"error",tr("正在准备声音，稍后即可试听。")}};
  QString folder=QFileInfo(localFile(workspace)).absolutePath();if(!QDir().mkpath(folder))return {{"error",tr("请选择可以保存试听材料的位置。")}};
  const QString path=folder+"/expression-playback.mscz";
  auto copied=copyWorkflowScore(path,analysisRevision(),true);if(copied.contains("error"))return copied;
  std::unique_ptr<MasterScore> material(mscore->readScore(path));if(!material)return {{"error",tr("读取试听材料失败，请重新准备。")}};
  Ms::Score* target=material.get();
  if(_score!=_score->masterScore()){
   int index=-1;auto excerpts=_score->masterScore()->excerpts();for(int i=0;i<excerpts.size();++i)if(excerpts[i]->partScore()==_score)index=i;
   if(index<0||index>=material->excerpts().size())return {{"error",tr("找不到这份分谱，请从总谱准备试听。")}};target=material->excerpts()[index]->partScore();
  }
  auto original=renderPlaybackPreview(_score,target);
  PluginAPI::Score wrapped(target);ScoreObserver local;local.setScore(&wrapped);local._workflowApplyingPreview=true;local.workflowInfo();
  auto values=candidate;values["revision"]=local.analysisRevision();auto applied=local.applyExpression(values);if(applied.contains("error"))return applied;
  auto changed=renderPlaybackPreview(_score,target);
  preparePlaybackPreview(_score,key,std::move(original),std::move(changed));
 }
 return startPlaybackPreview(_score,proposed,scope);
}
'''
s=s[:index]+code+s[index:];save('mscore/workflow/workflowexpression.cpp',s)
for name in ['mscore/workflow/playbackpreview.h','mscore/workflow/playbackpreview.cpp']:(host/name).write_bytes((root/'native'/name).read_bytes())
print('Reusable expression audition and source-note mapping connected')
