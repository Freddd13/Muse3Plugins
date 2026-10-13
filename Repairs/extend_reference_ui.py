# coding: utf-8
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'ReferencePlayer/ReferencePlayer_MS3.qml'
s=p.read_text(encoding='utf8')
def replace(old,new):
 global s
 if s.count(old)!=1:raise RuntimeError(old[:80])
 s=s.replace(old,new)
replace(' version:"1.0.0"',' version:"1.1.0"')
replace(' property var media:null',''' property var media:null
 property var audioProject:null
 property var tracks:[]
 property var sessions:[]
 property int selectedTrack:-1
 property bool addingAudio:false
 property bool switchingTrack:false
 property int playbackMode:0
 property var lastJointPlan:null
 property bool restartLoop:false
 function storeTrack(){
  if(switchingTrack||selectedTrack<0||selectedTrack>=tracks.length||!media)return;
  var list=Project.copy(tracks),t=list[selectedTrack];t.path=media.path;t.identity=sourceIdentity;t.a=a;t.b=b;t.loop=looping;t.fade=fade;t.bookmarks=Project.copy(bookmarks);t.associations=Project.copy(associations);t.volume=media.volume;t.speed=media.speed;tracks=list;
  if(audioProject&&audioProject.available&&!audioProject.playing)audioProject.setTracks(tracks);
 }
 function selectTrack(index){
  if(index<0||index>=tracks.length)return;storeTrack();if(usable)media.pause();switchingTrack=true;selectedTrack=index;media=sessions[index];var t=tracks[index];
  sourceIdentity=t.identity||null;a=t.a||0;b=t.b||media.duration;looping=!!t.loop;fade=t.fade!==false;bookmarks=t.bookmarks||[];associations=t.associations||[];selectedAssociation=associations.length?0:-1;viewStart=0;viewEnd=media.duration;
  viewportPeaks=[];media.volume=t.volume===undefined?.8:t.volume;media.speed=t.speed||1;switchingTrack=false;applyLoop();wave.requestPaint();status="已选音轨："+t.name;
 }
 function trackOption(name,value){if(selectedTrack<0)return;storeTrack();var list=Project.copy(tracks);list[selectedTrack][name]=value;tracks=list;if(audioProject&&!audioProject.playing)audioProject.setTracks(tracks);}
 function openAudio(url){
  if(audioProject&&audioProject.playing){status="请先停止联合播放。";return;}
  if(relocating){media.open(String(url));return;}
  storeTrack();if(usable)media.pause();
  if(addingAudio||selectedTrack<0){
   if(tracks.length>=16){status="最多添加 16 条音轨。";return;}
   var session=root.newReferenceMedia(),list=Project.copy(tracks),objects=sessions.slice();objects.push(session);list.push({id:"audio-"+Date.now()+"-"+list.length,name:String(url).split(/[\\\\/]/).pop(),path:String(url),associations:[],mute:false,solo:false,participate:true,volume:.8,speed:1});sessions=objects;tracks=list;selectedTrack=list.length-1;media=session;
  }
  addingAudio=false;restored=null;media.open(String(url));
 }
 function restoreTracks(data,url){
  if(audioProject&&audioProject.playing)observer.stopReferencePlayback();
  var list=Project.copy(data.tracks),objects=[];for(var i=0;i<list.length;++i){list[i].path=Project.resolve(url,list[i].path);var session=root.newReferenceMedia();objects.push(session);session.open(Project.fileUrl(list[i].path));}
  tracks=list;sessions=objects;selectedTrack=-1;selectTrack(Math.max(0,Math.min(list.length-1,data.selectedTrack||0)));restored=list[selectedTrack];workspace=String(url);playbackMode=data.playbackMode||0;status="正在恢复音轨与关联。";
 }
 function startJoint(){
  if(!audioProject||!audioProject.available||!observer||!curScore){status="需要支持多音频联动的软件版本。";return;}
  if(observer.playing){status="请先停止乐谱播放。";return;}
  if(selectedAssociation<0){status="先选择一条谱段关联。";return;}
  storeTrack();for(var i=0;i<sessions.length;++i)sessions[i].pause();
  var item=associations[selectedAssociation];observer.score=curScore;
  var request={revision:observer.analysisRevision(),start:item.start,end:item.end,occurrence:item.occurrence||1,mode:playbackMode,leader:item,speed:media.speed,tracks:tracks,volume:.8,fade:fade};
  var plan=observer.referencePlan(request);if(plan.error){error(plan.error);return;}
  lastJointPlan=plan;var r=observer.startReferencePlayback(plan);if(r.error)error(r.error);else status=playbackMode===0?"准备联合播放：开头对齐，此后各自保持速度。":"正在准备联合播放；临时速度不会保存到乐谱。";
 }
 function stopJoint(){restartLoop=false;loopRestart.stop();if(observer)observer.stopReferencePlayback();status="乐谱和参加播放的音轨已停止。";}
 Timer{id:loopRestart;interval:100;onTriggered:root.startJoint()}
 Connections{target:root.audioProject;ignoreUnknownSignals:true;onFinished:{if(root.looping&&root.lastJointPlan){root.restartLoop=true;loopRestart.start();}}}
 onAssociationsChanged:storeTrack()
 onBookmarksChanged:storeTrack()''')
replace('  applyLoop();\n }\n function saveProject','  applyLoop();storeTrack();\n }\n function saveProject')
replace('   Project.writeModule(observer,url,"reference",{file:', '''   storeTrack();var savedTracks=Project.copy(tracks);savedTracks.forEach(function(t){t.path=Project.relative(url,t.path)});
   Project.writeModule(observer,url,"reference",{format:2,tracks:savedTracks,selectedTrack:selectedTrack,playbackMode:playbackMode,file:''')
replace('workspace=String(url);restored=data;media.open', 'workspace=String(url);if(data.tracks&&data.tracks.length){restoreTracks(data,url);persist();return;}restored=data;media.open')
replace('  if(typeof root.newReferenceMedia==="function")media=root.newReferenceMedia();','''  if(typeof root.newReferenceMedia==="function")media=root.newReferenceMedia();
  if(typeof root.newReferenceProject==="function")audioProject=root.newReferenceProject();
  if(audioProject&&audioProject.available&&audioProject.tracks.length){var existing=Project.copy(audioProject.tracks);var objects=[];existing.forEach(function(t){var m=root.newReferenceMedia();objects.push(m);m.open(Project.fileUrl(t.path));});tracks=existing;sessions=objects;selectedTrack=-1;selectTrack(0);restored=existing[0];}''')
replace('Component.onDestruction:{if(usable)media.pause();persist()}','Component.onDestruction:{storeTrack();if(audioProject&&audioProject.playing&&observer)observer.stopReferencePlayback();for(var i=0;i<sessions.length;++i)sessions[i].pause();if(usable)media.pause();persist()}')
replace('Desk.DeskButton {text:"打开";enabled:root.usable;onClicked:audioDialog.open()}', 'Desk.DeskButton {text:"打开";enabled:root.usable;onClicked:{root.addingAudio=false;audioDialog.open()}}\n   Desk.DeskButton {text:"添加音轨";visible:!root.compact;enabled:root.usable;onClicked:{root.addingAudio=true;audioDialog.open()}}')
replace('  GridLayout {\n   columns:root.compact?', '''  RowLayout {
   visible:!root.compact;Layout.fillWidth:true
   Desk.DeskComboBox {objectName:"referenceTracks";Layout.fillWidth:true;model:root.tracks.map(function(t){return t.name});currentIndex:root.selectedTrack;onActivated:root.selectTrack(currentIndex)}
   CheckBox {text:"参与";checked:root.selectedTrack>=0&&root.tracks[root.selectedTrack].participate!==false;onClicked:root.trackOption("participate",checked)}
   CheckBox {text:"静音";checked:root.selectedTrack>=0&&!!root.tracks[root.selectedTrack].mute;onClicked:root.trackOption("mute",checked)}
   CheckBox {text:"独听";checked:root.selectedTrack>=0&&!!root.tracks[root.selectedTrack].solo;onClicked:root.trackOption("solo",checked)}
  }
  RowLayout {
   Layout.fillWidth:true
   Desk.DeskComboBox {objectName:"referencePlaybackMode";Layout.fillWidth:true;model:["开头对齐，各自播放","音频跟随乐谱","乐谱跟随选中音频"];currentIndex:root.playbackMode;onActivated:root.playbackMode=currentIndex}
   Desk.DeskButton {objectName:"referenceJointPlay";text:root.audioProject&&root.audioProject.playing?"停止联动":"联合播放";enabled:root.audioProject&&root.audioProject.available;onClicked:{if(root.audioProject.playing)root.stopJoint();else root.startJoint()}}
  }
  GridLayout {
   columns:root.compact?''')
replace('root.media.volume=value;root.persist()', 'root.media.volume=value;root.storeTrack();root.persist()')
replace('root.media.speed=value/100;root.persist()', 'root.media.speed=value/100;root.storeTrack();root.persist()')
replace('text:root.status+(root.usable?', 'text:(root.audioProject&&root.audioProject.playing?root.audioProject.status:root.status)+(root.usable?')
replace('   Label {text:"反复出现次数（仅用于定位说明）"}', '''   CheckBox {text:"这条关联参加联合播放";checked:root.selectedAssociation>=0&&root.associations[root.selectedAssociation].active!==false;onClicked:{var list=Project.copy(root.associations);list[root.selectedAssociation].active=checked;root.associations=list}}
   Label {text:"播放第几遍（反复后的出现次数）"}''')
replace('onAccepted:root.media.open(String(fileUrl))', 'onAccepted:root.openAudio(String(fileUrl))')
p.write_bytes(s.encode('utf8'))
