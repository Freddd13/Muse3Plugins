from pathlib import Path
root=Path(__file__).resolve().parent
plugins=root.parent
p=plugins/'PerformanceExpression/PerformanceExpression_MS3.qml'
s=p.read_text(encoding='utf8')
def edit(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old))
 s=s.replace(old,new)
edit('import "Alignment.js" as Rules','import "Alignment.js" as Rules\nimport "ExpressionProgress.js" as Progress')
edit(' property var candidate:null',' property var candidate:null\n property var appliedProgress:({velocity:{},tempos:{}})\n property int applicationScope:1\n property bool applying:false\n property bool refreshingApplication:false\n property string applicationMessage:""\n property int savedVelocityCount:0')
edit(' function slice(){',''' function refreshHistory(){if(observer&&typeof observer.expressionVelocityHistory==="function")savedVelocityCount=observer.expressionVelocityHistory({}).count||0}
 function currentApplication(){return Progress.portion(candidate,applicationScope,observer.expressionSelection())}
 function readApplied(message){
  applicationMessage=message;refreshingApplication=true;revision=observer.analysisRevision();collecting=[];nextTick=scope.start;busy=true;stale=false;candidate=null;paging.start();
 }
 function restoreVelocity(replace){
  if(observer.playing){status="停止播放后可以恢复或保存力度。";return;}
  var range=applicationScope===2?({}):Project.copy(observer.expressionSelection().scope);
  range.selectedOnly=applicationScope===0;range.revision=observer.analysisRevision();
  applying=true;var r=replace?observer.saveCurrentExpressionVelocity(range):observer.restoreExpressionVelocity(range);applying=false;
  if(r.error){fail(r.error);return;}
  appliedProgress=({velocity:{},tempos:{}});refreshHistory();
  var text=replace?"已把当前力度保存为比较起点":"已恢复应用前的力度";
  if(notes.length)readApplied(text+" · "+r.changed+" 个音。Ctrl+Z 撤销。");else status=text+" · "+r.changed+" 个音。";
 }
 function slice(){''')
edit('if(page.done){notes=collecting;collecting=[];paging.stop();if(readForCapture)beginRecording();else runAlignment()}', '''if(page.done){notes=collecting;collecting=[];paging.stop();
   if(refreshingApplication){result=Progress.refreshed(result,notes);refreshingApplication=false;busy=false;status=applicationMessage;refreshHistory();build();}
   else if(readForCapture)beginRecording();else runAlignment();
  }''')
edit('notes:notes,revision:revision,scope:scope});','notes:notes,revision:revision,scope:scope});') # retain worker interface
begin=s.index(' function applyPart(part){');end=s.index(' function audition(useCandidate)',begin)
s=s[:begin]+''' function applyPart(part){
  pendingAudition=null;auditionRetry.stop();if(!candidate||stale)return;
  if(previewing&&!returnOriginal())return;
  var values=currentApplication();if(part==="velocity")values.tempos=[];else values.velocity=[];
  if(!values.velocity.length&&!values.tempos.length){status=applicationScope===0?"选中要使用的音后再点使用。":"这一范围的结果已经使用，可以继续处理其它音。";return;}
  applying=true;var response=observer.applyExpression(values);applying=false;
  if(response.error){fail(response.error);return;}
  appliedProgress=Progress.record(appliedProgress,values);
  readApplied("已使用"+(part==="velocity"?"演奏力度":"演奏速度")+"，更新 "+response.changed+" 项。Ctrl+Z 撤销。");
 }
 function apply(){
  if(!candidate||stale)return;if(previewing&&!returnOriginal())return;
  var values=currentApplication();applying=true;var response=observer.applyExpression(values);applying=false;
  if(response.error){fail(response.error);return;}appliedProgress=Progress.record(appliedProgress,values);readApplied("已使用力度和速度，共 "+response.changed+" 项。Ctrl+Z 撤销。");
 }
''' +s[end:]
edit('  if(previewing)return;','  if(previewing||applying||refreshingApplication)return;')
edit('root.candidate=result;root.status="准备使用：力度 "+result.velocity.length+" 个音 · 速度 "+result.tempos.length+" 处 · 保留 "+result.kept.length+" 项"','root.candidate=Progress.pending(result,root.appliedProgress);root.status=(root.applicationMessage?root.applicationMessage+" ":"")+"还有 "+root.candidate.velocity.length+" 个音的力度、"+root.candidate.tempos.length+" 处速度可用";root.applicationMessage=""')
edit('  observer=newScoreObserver();observer.score=curScore;','  observer=newScoreObserver();observer.score=curScore;refreshHistory();')
edit('root.loadedSourceHash="";root.passageChoice=0;root.manualAnchors=[];', 'root.appliedProgress=({velocity:{},tempos:{}});root.loadedSourceHash="";root.passageChoice=0;root.manualAnchors=[];')
edit('root.recordingImport=true;root.loadedSourceHash="";', 'root.appliedProgress=({velocity:{},tempos:{}});root.recordingImport=true;root.loadedSourceHash="";')
edit('text:"设锚点"','text:"固定这一处对应"')
edit('title:"人工对应与锚点"','title:"调整演奏对应"')
edit('text:"移除所有人工锚点"','text:"清除固定的对应位置"')
edit('   Desk.DeskButton {text:"取消";enabled:root.busy;onClicked:root.cancel()}','''   Desk.DeskButton {text:"取消";enabled:root.busy;onClicked:root.cancel()}
  }
  RowLayout {visible:!root.compact;Layout.fillWidth:true
   Desk.DeskButton {text:"已匹配 "+root.result.matches.length;enabled:root.result.matches.length>0;onClicked:issueMenu.open()}
   Desk.DeskButton {text:"漏弹 "+root.result.missing.length;enabled:root.result.missing.length>0;onClicked:{root.issueKind="missing";issues.open()}}
   Desk.DeskButton {text:"多弹 "+root.result.extra.length;enabled:root.result.extra.length>0;onClicked:{root.issueKind="extra";issues.open()}}
   Desk.DeskButton {text:"需核对 "+root.result.pending;enabled:root.result.pending>0;onClicked:{root.issueKind="pending";issues.open()}}''')
edit('  GridLayout {\n   columns:root.width<600?2:4;visible:!root.compact;Layout.fillWidth:true','''  RowLayout {visible:!root.compact;Layout.fillWidth:true
   Label {text:"使用范围";color:theme.text}
   Desk.DeskComboBox {objectName:"expressionApplicationScope";Layout.fillWidth:true;model:["选中音","当前选段","全部已对应范围"];currentIndex:root.applicationScope;onActivated:root.applicationScope=currentIndex}
  }
  GridLayout {
   columns:2;visible:!root.compact;Layout.fillWidth:true''')
edit('text:"试听原来"','text:"谱中效果"')
edit('text:"试听新力度"','text:"拟采用效果"')
edit('   Desk.DeskButton {text:"查看变化";enabled:root.candidate!==null;onClicked:changes.open()}','''   Desk.DeskButton {text:"查看变化";enabled:root.candidate!==null;onClicked:changes.open()}
   Desk.DeskButton {objectName:"expressionRestoreVelocity";text:"恢复应用前力度";enabled:root.savedVelocityCount>0&&!root.busy;onClicked:root.restoreVelocity(false)}
   Desk.DeskButton {text:"以当前力度为起点";enabled:!root.busy;onClicked:root.restoreVelocity(true)}''')
edit(' Menu {id:projectMenu',''' property string issueKind:"missing"
 Menu {id:issueMenu
  MenuItem {text:"重新比较已使用的结果";onTriggered:{root.appliedProgress=({velocity:{},tempos:{}});root.build()}}
  MenuItem {text:"读取并对应全曲";onTriggered:{root.whole=true;root.analyze()}}
 }
 Dialog {id:issues;title:root.issueKind==="missing"?"漏弹的音":root.issueKind==="extra"?"多弹的音":"需要核对的对应";modal:false;width:Math.min(400,root.width);height:300;standardButtons:Dialog.Close
  ListView {anchors.fill:parent;clip:true;model:root.issueKind==="pending"?root.result.matches.filter(function(m){return !m.confirmed&&m.confidence<.8}):root.result[root.issueKind];ScrollBar.vertical:ScrollBar{}
   delegate:ItemDelegate {width:parent.width;text:root.issueKind==="extra"?(modelData.seconds.toFixed(3)+"秒 · "+root.recordingPitch(modelData.pitch)):"第 "+(modelData.original||modelData).measure+" 小节 · "+root.recordingPitch(modelData.pitch);onClicked:{
    if(root.issueKind==="extra"){root.status="演奏 "+modelData.seconds.toFixed(3)+" 秒处多了这个音；在对应轨选择相邻谱面音后可连接。";root.publishComparison();root.editorRequest("select","",modelData.id);}
    else {var n=modelData.original||modelData;root.observer.navigateWorkflow({start:n.tick,firstTrack:n.track,index:n.index,writtenPitch:n.writtenPitch,writtenTpc:n.writtenTpc},false);var i=root.result.matches.findIndex(function(m){return m.scoreId===modelData.scoreId});if(i>=0)root.selected=i;root.status="已定位第 "+n.measure+" 小节；可在编辑器调整对应。";}
   }}
  }
 }
 Menu {id:projectMenu''')
p.write_text(s,encoding='utf8',newline='\n')
print('Expression partial-application flow updated')
