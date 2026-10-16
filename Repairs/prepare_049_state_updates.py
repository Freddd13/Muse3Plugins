from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
N=ROOT/'Repairs/native'
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:60];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
edit(N/'mscore/plugin/api/scoreobserver.h','Q_INVOKABLE QVariantMap setEditorComparison(const QVariantMap&);','Q_INVOKABLE QVariantMap setEditorComparison(const QVariantMap&);\n      Q_INVOKABLE QVariantMap updateEditorComparisonState(const QVariantMap&);')
edit(N/'mscore/workflow/workflowcontext.h','      Q_INVOKABLE void expressionAction','      void updateExpression(const QVariantMap& state){for(auto it=state.cbegin();it!=state.cend();++it)_expression[it.key()]=it.value();emit changed();}\n      Q_INVOKABLE void expressionAction')
edit(N/'mscore/workflow/referenceworkflow.cpp','namespace {\ndouble audioAt','''QVariantMap ScoreObserver::updateEditorComparisonState(const QVariantMap& data){
 auto context=workflowContext();const auto previous=context->expression();
 if(!_score||!context->current(_score)||data.value("owner")!=previous.value("owner")||data.value("revision")!=previous.value("revision"))return {{"error",tr("重新打开演奏对比后可以继续选择音符。")}};
 QVariantMap state;for(const char* name:{"selectedScoreId","selectedMidiId","busy","previewCanUndo","previewCanRedo","applyCounts"})if(data.contains(name))state[name]=data.value(name);
 context->updateExpression(state);return {{"ok",true}};
}
namespace {
double audioAt''')
p=ROOT/'PerformanceExpression/PerformanceExpression_MS3.qml'
edit(p,' property bool auditionAudio:false',' property bool auditionAudio:false\n property string publishedComparisonKey:""')
start='  observer.setEditorComparison({owner:editorOwner,revision:revision,previewVersion:previewVersion,resultVersion:resultVersion,selectedMidiId:selectedMidiId,previewCanUndo:previewUndo.length>0,previewCanRedo:previewRedo.length>0,result:displayed.result,candidate:candidate||{},busy:busy||(candidate!==null&&previewUpdating),applyCounts:{velocity:scopedCandidate.velocity.length,tempos:scopedCandidate.tempos.length},selectedScoreId:selected>=0&&selected<result.matches.length?result.matches[selected].scoreId:"",scope:scope});'
new='''  var state={owner:editorOwner,revision:revision,selectedMidiId:selectedMidiId,previewCanUndo:previewUndo.length>0,previewCanRedo:previewRedo.length>0,busy:busy||(candidate!==null&&previewUpdating),applyCounts:{velocity:scopedCandidate.velocity.length,tempos:scopedCandidate.tempos.length},selectedScoreId:selected>=0&&selected<result.matches.length?result.matches[selected].scoreId:""};
  var key=revision+":"+previewVersion+":"+resultVersion;
  if(publishedComparisonKey===key&&typeof observer.updateEditorComparisonState==="function"){
   var updated=observer.updateEditorComparisonState(state);if(updated.ok)return;
  }
  state.previewVersion=previewVersion;state.resultVersion=resultVersion;state.result=displayed.result;state.candidate=candidate||{};state.scope=scope;
  var sent=observer.setEditorComparison(state);if(sent.ok)publishedComparisonKey=key;'''
edit(p,start,new)
