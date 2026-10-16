from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
N=ROOT/'Repairs/native'
HOST=ROOT.parent/'muse3_dev/MuseScore'
def edit(p,old,new):
 s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:70];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
p=N/'mscore/performanceeditor/workflowlanes.h'
if not p.exists():p.write_bytes((HOST/'mscore/performanceeditor/workflowlanes.h').read_bytes())
edit(p,'      QVector<Hit> _hits;','      QVector<Hit> _hits;\n      QString _expressionVersion;\n      QVariantList _matches;\n      QVector<QPair<double,double>> _timing;\n      void refreshExpression();')
p=N/'mscore/performanceeditor/workflowlanes.cpp'
edit(p,'connect(workflowContext(),&WorkflowContext::changed,this,QOverload<>::of(&WorkflowLanes::update));','connect(workflowContext(),&WorkflowContext::changed,this,&WorkflowLanes::refreshExpression);refreshExpression();')
anchor='QObject* WorkflowLanes::wave(const QVariantMap& t){'
edit(p,anchor,'''void WorkflowLanes::refreshExpression(){
      const auto expression=workflowContext()->expression();
      const QString version=expression.value("revision").toString()+":"+expression.value("resultVersion").toString();
      if(version!=_expressionVersion||!expression.contains("resultVersion")){
            _expressionVersion=version;const auto result=expression.value("result").toMap();
            _matches=result.value("displayMatches").toList();if(!result.contains("displayMatches"))_matches=result.value("matches").toList();
            _timing.clear();for(auto value:result.value("timing").toList()){auto p=value.toMap();_timing.append({p.value("seconds").toDouble(),p.value("tick").toDouble()});}
            // Older panels provide only the endpoints. New panels supply the local clock.
            if(_timing.isEmpty()&&!_matches.isEmpty()){auto a=_matches.front().toMap(),b=_matches.back().toMap();_timing.append({a.value("seconds").toDouble(),a.value("tick").toDouble()});if(b.value("seconds").toDouble()>_timing.front().first)_timing.append({b.value("seconds").toDouble(),b.value("tick").toDouble()});}
            }
      update();
      }
'''+anchor)
s=p.read_text(encoding='utf8');start=s.index('                  auto matches=expression.value("result").toMap().value("displayMatches")');end=s.index('                  p.save();p.setClipRect',start)
s=s[:start]+'''                  const auto& matches=_matches;const QString selected=expression.value("selectedScoreId").toString();
                  const auto targets=expression.value("candidate").toMap().value("velocityById").toMap();
                  auto performanceTick=[&](double seconds){
                        if(_timing.isEmpty())return expression.value("scope").toMap().value("start").toDouble();
                        if(_timing.size()<2)return _timing.front().second;
                        auto next=std::upper_bound(_timing.cbegin(),_timing.cend(),seconds,[](double s,const QPair<double,double>& p){return s<p.first;});if(next==_timing.cbegin())++next;if(next==_timing.cend())--next;auto before=next-1;return before->second+(seconds-before->first)*(next->second-before->second)/(next->first-before->first);
                        };
'''+s[end:]
old='for(auto value:expression.value("result").toMap().value("extra").toList()){auto n=value.toMap();if(matches.isEmpty())continue;double px=x(performanceTick(n.value("seconds").toDouble()));p.drawText(QPointF(px-4,y+42),"+");_hits.append({QRectF(px-7,y+28,14,18),QString(),n.value("id").toString(),-1});}'
new='''for(auto value:result.value("extra").toList()){
                        auto n=value.toMap();if(_timing.isEmpty())continue;double px=x(performanceTick(n.value("seconds").toDouble()));
                        const bool selected=n.value("id").toString()==expression.value("selectedMidiId").toString();
                        p.setPen(QPen(selected?theme.highlight().color():theme.text().color(),selected?2:1));
                        if(selected){p.setBrush(Qt::NoBrush);p.drawRoundedRect(QRectF(px-8,y+26,16,21),3,3);}
                        p.drawText(QPointF(px-4,y+42),"+");_hits.append({QRectF(px-7,y+28,14,18),QString(),n.value("id").toString(),-1,tr("多弹 · MIDI %1 · %2 秒").arg(n.value("pitch").toInt()).arg(n.value("seconds").toDouble(),0,'f',3)});
                        }'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n')
p=ROOT/'PerformanceExpression/PerformanceExpression_MS3.qml'
edit(p,'previewVersion:previewVersion,previewCanUndo:','previewVersion:previewVersion,resultVersion:resultVersion,selectedMidiId:selectedMidiId,previewCanUndo:')
edit(p,' property int previewVersion:0',' property int previewVersion:0\n property int resultVersion:0\n property string selectedMidiId:""')
edit(p,' onDisplayedChanged:publishComparison()',' onDisplayedChanged:{resultVersion++;publishComparison()}')
edit(p,'  if(action==="select"){publishComparison();return;}','  if(action==="select"){selectedMidiId=midiId;publishComparison();return;}')
old='if(root.issueKind==="extra"){root.status="演奏 "+modelData.seconds.toFixed(3)+" 秒处多了这个音；在对应轨选择相邻谱面音后可连接。";root.publishComparison();root.editorRequest("select","",modelData.id);}'
new='''if(root.issueKind==="extra"){
     root.selectedMidiId=modelData.id;root.publishComparison();root.observer.showEditorCorrespondence();
     var tick=Progress.tickAt(root.displayed.result.timing,modelData.seconds),closest=null;
     if(tick!==null)root.notes.forEach(function(n){if(!closest||Math.abs(n.tick-tick)<Math.abs(closest.tick-tick))closest=n;});
     if(closest)root.observer.navigateWorkflow({start:closest.tick,firstTrack:closest.track,index:closest.index,writtenPitch:closest.writtenPitch,writtenTpc:closest.writtenTpc},false);
     root.status="已在演奏对应区标出 "+modelData.seconds.toFixed(3)+" 秒的多弹音。点一个谱面音，再点这个演奏音，可以重新连接。";
    }'''
edit(p,old,new)
edit(p,'    else {var n=modelData.original||modelData;root.observer.navigateWorkflow','    else {root.observer.showEditorCorrespondence();var n=modelData.original||modelData;root.observer.navigateWorkflow')
edit(p,'锚点','内部对齐点')
p=ROOT/'P1/tests/test_expression_progress.js'
with p.open('a',encoding='utf8') as f:f.write('''
const clockResult={matches:[{tick:0,seconds:10,confidence:1},{tick:0,seconds:10.02,confidence:1},{tick:480,seconds:11,confidence:1},{tick:960,seconds:12.5,confidence:1},{tick:1440,seconds:11.4,confidence:.2}]};
const points=ctx.timing(clockResult);assert.strictEqual(points.length,3);assert(Math.abs(ctx.tickAt(points,11.75)-720)<.01);assert(ctx.tickAt(points,9)<0);
const usedClock=ctx.display(clockResult,{velocity:{}},false).result.timing;assert.strictEqual(usedClock.length,3);
console.log('Local matching clock and extra-note navigation passed.');
''')
