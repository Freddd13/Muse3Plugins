from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent;D=R/'staged056/plugins/ReferencePlayer';D.mkdir(parents=True,exist_ok=True)
s=(P/'ReferencePlayer/ReferencePlayer_MS3.qml').read_text(encoding='utf8')
s=s.replace(' property var observer:null',''' property bool documentReady:false
 property bool restoringDocument:false
 property bool writingDocument:false
 property string documentJSON:""
 property bool linkEditor:false
 property bool handTool:false
 property real lastLinkedTick:-1
 function scheduleDocument(){if(documentReady&&!restoringDocument&&!writingDocument&&owner&&observer)documentTimer.restart()}
 function saveScoreProject(){
  if(!documentReady||restoringDocument||writingDocument||!owner||!observer||typeof observer.setWorkflowData!=="function")return
  if(observer.playing)return
  var list=Project.copy(tracks);list.forEach(function(t){delete t.missing;var p=observer.referenceFileLocation(t.path);t.originalPath=p.path;t.relativePath=p.relative})
  var data={schema:2,structure:observer.referenceStructureKey(),tracks:list,selectedTrack:selectedTrack,playbackMode:playbackMode,volume:jointVolume,linked:linkEditor}
  writingDocument=true;var result=observer.setWorkflowData("reference",data);writingDocument=false
  if(result.error){status=result.error;return}documentJSON=JSON.stringify(observer.workflowData("reference"))
 }
 function restoreScoreProject(){
  if(!observer||typeof observer.workflowData!=="function")return
  var data=observer.workflowData("reference");documentJSON=JSON.stringify(data);restoringDocument=true
  if(data.schema===2&&data.tracks&&data.tracks.length){
   var value=Project.copy(data);value.tracks.forEach(function(t){var p=observer.referenceFileLocation(t.originalPath||t.path,t.relativePath||"");t.path=p.path;t.missing=!p.exists;if(data.structure&&data.structure!==root.observer.referenceStructureKey())(t.associations||[]).forEach(function(a){a.stale=true})})
   restoreTracks(value,"");jointVolume=data.volume===undefined?.5:data.volume;linkEditor=!!data.linked
   status=value.tracks.some(function(t){return t.missing})?"音轨与关联已恢复；找不到的音频可点“重新定位”。":"正在读取这份乐谱的参考音轨。"
  }else{
   if(audioProject&&audioProject.playing)stopJoint();var retired=sessions.slice();switchingTrack=true;tracks=[];sessions=[];selectedTrack=-1;associations=[];bookmarks=[];selectedAssociation=-1;sourceIdentity=null;a=0;b=0;viewStart=0;viewEnd=0;media=root.newReferenceMedia();switchingTrack=false
   if(audioProject&&audioProject.available)audioProject.setTracks([]);retired.forEach(function(m){root.releaseReferenceMedia(m)});status="打开原曲，为这份乐谱建立片段关联。"
  }
  restoringDocument=false
 }
 function linkFromScore(){
  if(!linkEditor||!observer||!usable||selectedAssociation<0||media.playing||(audioProject&&audioProject.playing))return
  var selected=observer.expressionSelection(),tick=selected.notes&&selected.notes.length?selected.notes[0].tick:observer.tick,item=associations[selectedAssociation]
  if(tick===lastLinkedTick||tick<item.start||tick>item.end)return;lastLinkedTick=tick;media.seek(Project.mapped(item,tick))
 }
 function linkToScore(ms){
  if(!linkEditor||!observer||selectedAssociation<0||observer.playing)return
  var item=associations[selectedAssociation],points=[{tick:item.start,ms:item.from}].concat(item.anchors||[]).concat([{tick:item.end,ms:item.until}]);if(ms<item.from||ms>item.until)return
  var i=1;while(i<points.length-1&&ms>points[i].ms)i++;var a=points[i-1],b=points[i],tick=Math.round(a.tick+(ms-a.ms)*(b.tick-a.tick)/(b.ms-a.ms));lastLinkedTick=tick;observer.navigateWorkflow({start:tick,end:tick+1,firstTrack:item.firstTrack,endTrack:item.endTrack},false)
 }
 Timer {id:documentTimer;interval:0;onTriggered:root.saveScoreProject()}
 onTracksChanged:scheduleDocument()
 onLinkEditorChanged:scheduleDocument()
 property var observer:null''',1)
s=s.replace('workspace=String(url);playbackMode=data.playbackMode||0;','if(!restoringDocument)workspace=String(url);playbackMode=data.playbackMode||0;',1)
a='''  if(changed&&associations.length){associations=associations.map(function(item){var next=Project.copy(item);next.stale=true;return next;});status="已切换乐谱，打开关联的“修改”可选用当前谱段。";}
  owner=curScore;observer.score=curScore;
  if(changed)structureKey=typeof observer.referenceStructureKey==="function"?observer.referenceStructureKey():"";
  if(changed)storeTrack();'''
b='''  if(changed)saveScoreProject();owner=curScore;observer.score=curScore;
  if(changed){structureKey=typeof observer.referenceStructureKey==="function"?observer.referenceStructureKey():"";lastLinkedTick=-1;restoreScoreProject();}'''
assert a in s;s=s.replace(a,b,1)
s=s.replace('  if(audioProject&&audioProject.available&&audioProject.tracks.length){','  if(!curScore&&audioProject&&audioProject.available&&audioProject.tracks.length){',1)
s=s.replace('  if(config.workspace && config.score && curScore && config.score.name===curScore.scoreName && config.score.measures===curScore.nmeasures)loadProject(config.workspace);','''  documentReady=true;
  if(curScore){structureKey=typeof observer.referenceStructureKey==="function"?observer.referenceStructureKey():"";restoreScoreProject();}''',1)
s=s.replace(' onScoreStateChanged: {\n  if(audioProject', ' onScoreStateChanged: {\n  if(writingDocument||restoringDocument)return;\n  if(audioProject',1)
s=s.replace('  structureKey=shape;\n }','''  structureKey=shape;
  if(documentReady&&observer&&typeof observer.workflowData==="function"&&documentJSON!==JSON.stringify(observer.workflowData("reference")))restoreScoreProject();
  linkFromScore();
 }''',1)
s=s.replace('Component.onDestruction:{storeTrack();','Component.onDestruction:{storeTrack();saveScoreProject();',1)
s=s.replace('onVisibleChanged:{if(!visible){','onVisibleChanged:{if(!visible){',1).replace('storeTrack();persist()}}','storeTrack();saveScoreProject();persist()}}',1)
s=s.replace('    property real downX:0;', '    property real downX:0;',1)
s=s.replace('acceptedButtons:Qt.LeftButton;hoverEnabled:true\n    property real downX', 'acceptedButtons:Qt.LeftButton|Qt.MiddleButton;hoverEnabled:true\n    property real downX',1)
s=s.replace('cursorShape:root.spaceDown?Qt.OpenHandCursor:Qt.CrossCursor','cursorShape:root.spaceDown||root.handTool?pressed?Qt.ClosedHandCursor:Qt.OpenHandCursor:Qt.CrossCursor',1)
s=s.replace('panning=root.spaceDown;', 'panning=root.spaceDown||root.handTool||mouse.button===Qt.MiddleButton;',1)
s=s.replace('root.media.seek(ms(mouse.x));}}','root.media.seek(ms(mouse.x));root.linkToScore(ms(mouse.x));}}',1)
at=s.index('    Flow {width:parent.width;spacing:5\n     Common.DragNumber')
s=s[:at]+'''    ScrollBar {objectName:"referenceTimeScroll";width:parent.width;orientation:Qt.Horizontal;policy:ScrollBar.AlwaysOn;active:true
        size:root.usable&&root.media.duration>0?Math.min(1,(root.viewEnd-root.viewStart)/root.media.duration):1
        position:root.usable&&root.media.duration>0?root.viewStart/root.media.duration:0
        onPositionChanged:if(pressed&&root.usable){var span=root.viewEnd-root.viewStart;root.viewStart=Math.max(0,Math.min(root.media.duration-span,position*root.media.duration));root.viewEnd=root.viewStart+span;wave.requestPaint()}
    }
    RowLayout {width:parent.width
        Desk.DeskButton {text:"选择";checkable:true;checked:!root.handTool;onClicked:root.handTool=false}
        Desk.DeskButton {text:"手形平移";checkable:true;checked:root.handTool;onClicked:root.handTool=true;ToolTip.visible:hovered;ToolTip.text:"拖动波形平移时间轴；鼠标中键也可以平移"}
        CheckBox {text:"联动编辑器定位";checked:root.linkEditor;onClicked:{root.linkEditor=checked;root.linkFromScore()}}
    }
'''+s[at:]
s=s.replace('        Desk.DeskButton {text:"删除";implicitWidth:48;', '        Desk.DeskButton {text:"删除";implicitWidth:48;',1)
# Add a direct missing-file action to every track row through the selected-track toolbar.
s=s.replace('MenuItem {text:"重新定位音频";', 'MenuItem {text:"重新定位音频";',1)
s=s.replace('     Desk.DeskButton {objectName:"referenceAssociate";', '     Desk.DeskButton {text:"重新定位音频";visible:root.selectedTrack>=0&&root.tracks[root.selectedTrack]&&root.tracks[root.selectedTrack].missing===true;onClicked:{root.relocating=true;audioDialog.open()}}\n     Desk.DeskButton {objectName:"referenceAssociate";',1)
s=s.replace('track.identity=info;track.path=session.path;', 'track.identity=info;track.path=session.path;track.missing=false;',1)
(D/'ReferencePlayer.view.qml').write_bytes(s.encode())
(D/'ReferencePlayer_MS3.qml').write_text('''import QtQuick 2.9
import MuseScore 3.0
MuseScore {
 menuPath:"Plugins.Reference Player"
 description:"打开内置原曲参考面板。音轨与关联随乐谱保存。"
 version:"1.4.0"
 requiresScore:false
 onRun:{if(typeof openReferencePanel==="function")openReferencePanel();Qt.quit()}
}
''',encoding='utf8')
print('0.56 native reference view and entry staged separately')
