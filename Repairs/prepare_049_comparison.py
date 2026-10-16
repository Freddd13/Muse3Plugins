from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def load(name):
 p=root/'native'/name
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((host/name).read_bytes())
 return p.read_text(encoding='utf8')
def save(name,text):
 p=root/'native'/name;p.write_text(text,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
def patch(name,old,new):
 s=load(name);assert s.count(old)==1,(name,old[:80],s.count(old));save(name,s.replace(old,new))
patch('mscore/performanceeditor/performanceeditor.h','      void paintVelocityHeaders(QPainter&, const QRectF&);','''      void paintVelocityHeaders(QPainter&, const QRectF&);
      QToolButton* _comparisonButton=nullptr;
      QHash<int,QVariantMap> _comparisonValues;
      QVariantList _comparisonTempos;
      QString _comparisonVersion;
      ScoreContentState _comparisonState;
      QMap<QString,double> _comparisonDraft;
      QMap<int,double> _comparisonStarts;
      bool _comparisonDragging=false;
      int _comparisonAnchor=-1,_comparisonTempoTick=-1;
      double _comparisonTempoStart=120;
      QPointF _comparisonPress;
      void setupExpressionComparison();
      void syncExpressionComparison();
      bool comparisonActive()const;
      double comparisonValue(int)const;
      void paintExpressionComparison(QPainter&,const QRectF&);
      bool comparisonEvent(QObject*,QEvent*);
      void cancelComparisonDrag();
      void commitComparisonDrag();''')
patch('mscore/performanceeditor/performanceeditor.cmake','      ${CMAKE_CURRENT_LIST_DIR}/performancepainting.cpp','      ${CMAKE_CURRENT_LIST_DIR}/performancepainting.cpp\n      ${CMAKE_CURRENT_LIST_DIR}/expressioncompare.cpp')
patch('mscore/performanceeditor/performanceeditor.cpp','      setupUsabilityControls(); applyAppearance(); status();','      setupUsabilityControls();setupExpressionComparison(); applyAppearance(); status();')
patch('mscore/performanceeditor/performanceeditor.cpp','bool PerformanceEditor::eventFilter(QObject* object, QEvent* event)\n      {','bool PerformanceEditor::eventFilter(QObject* object, QEvent* event)\n      {\n      if(comparisonEvent(object,event))return true;')
patch('mscore/performanceeditor/performancepainting.cpp','            if(_relativeActual)paintOriginalVelocity(painter,rect,onScore);','            if(_relativeActual)paintOriginalVelocity(painter,rect,onScore);\n            if(!onScore&&comparisonActive()){paintExpressionComparison(painter,rect);painter.restore();return;}')
patch('mscore/performanceeditor/performancepainting.cpp','      else if (parameter == 1) {','      else if (parameter == 1) {\n            if(!onScore&&comparisonActive()){paintExpressionComparison(painter,rect);painter.restore();return;}')
patch('mscore/performanceeditor/performanceinteraction.cpp','            if (!ruler && wheelVelocity(wheel, notes)) return true;','            if (!ruler && !(parameter&&comparisonActive()) && wheelVelocity(wheel, notes)) return true;')
patch('mscore/performanceeditor/performanceeditor.cpp','      updateSurfaces(); status();\n      if(_workflowPanel','      syncExpressionComparison();updateSurfaces(); status();\n      if(_workflowPanel')
patch('mscore/performanceeditor/performanceeditor.cpp','void PerformanceEditor::setSelectedValue(double value)\n      {','''void PerformanceEditor::setSelectedValue(double value)
      {
      if(comparisonActive()&&_parameter->currentIndex()==0){QVariantList edits;for(int index:selectedNotes())if(_comparisonValues.contains(index))edits.append(QVariantMap{{"id",_comparisonValues.value(index).value("id")},{"target",rangeKind()==1?NoteVelocity::effective(_notes[index].base,Note::ValueType::OFFSET_VAL,qRound(value)):qBound(1,qRound(value),127)}});if(!edits.isEmpty())workflowContext()->expressionAction("velocityTargets",QString(),QString::fromUtf8(QJsonDocument::fromVariant(edits).toJson(QJsonDocument::Compact)));return;}''')
patch('mscore/performanceeditor/performanceeditor.cpp','#include "performanceeditor.h"','#include "performanceeditor.h"\n#include <QJsonDocument>')
name='mscore/performanceeditor/workflowlanes.cpp';s=load(name)
old='auto performanceTick=[&](double seconds){return lastSeconds>firstSeconds?firstTick+(seconds-firstSeconds)*(lastTick-firstTick)/(lastSeconds-firstSeconds):firstTick;};'
new='''QMap<int,QVector<double>> byTick;for(auto value:matches){auto m=value.toMap();if(m.value("confirmed").toBool()||m.value("confidence").toDouble()>=.8)byTick[m.value("tick").toInt()].append(m.value("seconds").toDouble());}
                  QVector<QPair<double,double>> timing;for(auto it=byTick.cbegin();it!=byTick.cend();++it){auto times=it.value();std::sort(times.begin(),times.end());double seconds=times[times.size()/2];if(timing.isEmpty()||seconds>timing.back().first)timing.append({seconds,double(it.key())});}
                  auto performanceTick=[&](double seconds){if(timing.size()<2)return lastSeconds>firstSeconds?firstTick+(seconds-firstSeconds)*(lastTick-firstTick)/(lastSeconds-firstSeconds):firstTick;auto next=std::upper_bound(timing.cbegin(),timing.cend(),seconds,[](double s,const QPair<double,double>& p){return s<p.first;});if(next==timing.cbegin())++next;if(next==timing.cend())--next;auto before=next-1;return before->second+(seconds-before->first)*(next->second-before->second)/(next->first-before->first);};'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('上排是谱面起音，下排是演奏起音；演奏时间按首尾对应缩放到这段谱子的时间尺。','上排是谱面起音，下排是演奏起音；每一段使用附近的可靠对应来对齐时间。')
s=s.replace('QObject::tr("试听原来")','QObject::tr("谱中效果")').replace('QObject::tr("试听新效果")','QObject::tr("拟采用效果")')
old='      if(!hasExpression&&tracks.isEmpty())'
new='''      if(_editor->_playTick>=0){const double px=x(_editor->_playTick);if(px>=gutter&&px<=width()){p.setPen(QPen(colors[PerformanceAppearance::Playhead],1.5));p.drawLine(QPointF(px,0),QPointF(px,height()));}}
      if(!hasExpression&&tracks.isEmpty())'''
assert s.count(old)==1;s=s.replace(old,new);save(name,s)
patch('mscore/performanceeditor/performanceinteraction.cpp','      for (QWidget* canvas : {static_cast<QWidget*>(_noteCanvas), static_cast<QWidget*>(_ruler), _canvas}) {','      if(_workflowPanel&&_workflowPanel->isVisible())if(auto lane=_workflowPanel->findChild<QWidget*>("performanceWorkflowLanes"))lane->update();\n      for (QWidget* canvas : {static_cast<QWidget*>(_noteCanvas), static_cast<QWidget*>(_ruler), _canvas}) {')
name='mscore/performanceeditor/expressioncompare.cpp';(host/name).write_bytes((root/'native'/name).read_bytes())
# The panel receives one completed mouse operation, then updates the shared preview.
p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
s=s.replace(' property var appliedProgress:',' property int previewVersion:0\n property var previewUndo:[]\n property var appliedProgress:',1)
s=s.replace('owner:editorOwner,revision:revision,result:result','owner:editorOwner,revision:revision,previewVersion:previewVersion,result:result',1)
s=s.replace(' onCandidateChanged:publishComparison()',' onCandidateChanged:{previewVersion++;publishComparison()}',1)
at='  var index=result.matches.findIndex(function(m){return m.scoreId===scoreId});'
code='''  if(action==="undoPreview"){
   if(!previewUndo.length){status="预览已回到最初的对应结果。";return;}
   var history=previewUndo.slice(),previous=history.pop();previewUndo=history;config=previous.config;candidate=previous.candidate;dirtyProject=true;status="已撤销上一次预览调整。";return;
  }
  if(action==="velocityTargets"||action==="tempoTargets"){
   var values;try{values=JSON.parse(midiId)}catch(e){status="请重新拖动预览中的音。";return;}
   previewUndo=previewUndo.concat([{config:Project.copy(config),candidate:Project.copy(candidate)}]).slice(-40);
   var next=Project.copy(config),key=action==="velocityTargets"?"previewVelocity":"previewTempo",updates=next[key]||{};
   values.forEach(function(v){updates[action==="velocityTargets"?v.id:v.tick]=action==="velocityTargets"?v.target:v.bpm;});next[key]=updates;config=next;candidateConfig=JSON.stringify(config);candidate=Progress.targets(candidate,config);dirtyProject=true;status="已调整拟采用效果。试听后点击使用力度或使用速度。";return;
  }
'''
assert s.count(at)==1;s=s.replace(at,code+at)
s=s.replace('root.candidate=Progress.pending(result,root.appliedProgress)','root.candidate=Progress.pending(Progress.targets(result,root.config),root.appliedProgress)',1)
p.write_text(s,encoding='utf8',newline='\n')
print('Shared parameter comparison and preview editing prepared')
