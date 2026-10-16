from pathlib import Path
p=Path('ReferencePlayer/ReferencePlayer_MS3.qml');s=p.read_text(encoding='utf8')
s=s.replace('import "../WorkflowCommon/ActionMessages.js" as Messages','import "../WorkflowCommon/ActionMessages.js" as Messages\nimport "../WorkflowCommon" as Common')
s=s.replace('property int preferredRibbonHeight:410','property int preferredRibbonHeight:compact?68:410\n property bool independentPanelSurfaces:true')
a=s.index(' property string panelSpaceHandler:');b=s.index('\n ColumnLayout {',a)
s=s[:a]+''' property string panelSpaceHandler:"toggleReferencePlayback"
 property string panelSpacePressHandler:"beginReferenceSpace"
 property string panelSpaceReleaseHandler:"endReferenceSpace"
 property bool spaceDown:false
 property bool spacePanned:false
 property int transportTarget:0
 property var associationUndo:[]
 property var sliceBefore:null
 property bool changingSlice:false
 function beginReferenceSpace(){spaceDown=true;spacePanned=false}
 function endReferenceSpace(){var play=spaceDown&&!spacePanned;spaceDown=false;spacePanned=false;if(play)toggleReferencePlayback()}
 function toggleReferencePlayback() {
  if(transportTarget===1){
   if(observer&&observer.playing){observer.stopWorkflowPlayback();status="乐谱已停止。";return;}
   if(!observer||!curScore){status="打开乐谱后可以播放。";return;}
   observer.score=curScore;var range=selectedAssociation>=0?associations[selectedAssociation]:observer.analysisScope(false),r=observer.navigateWorkflow(range,true);if(r.error)error(r.error);else status="正在播放乐谱。";return;
  }
  if(!usable || !media.path){status="打开一段音频后即可播放。";return;}
  if(audioProject&&audioProject.playing){stopJoint();return;}
  if(transportTarget===2){startJoint();return;}
  if(media.playing){media.pause();status="原曲已暂停。";return;}
  if(tracks.length>1)playAudioTracks();else{lastSessionMode="single";media.play();status="正在播放原曲。";}
 }
 function readTime(text){var pieces=String(text).trim().split(":");if(pieces.length===2)return (Number(pieces[0])*60+Number(pieces[1]))*1000;return Number(text)*1000}
 function beginSlice(){if(!sliceBefore)sliceBefore={associations:Project.copy(associations),selected:selectedAssociation,a:a,b:b}}
 function finishSlice(){
  if(!sliceBefore)return;
  var before=sliceBefore;sliceBefore=null;
  if(selectedAssociation>=0 && selectedAssociation<associations.length && (a!==before.a||b!==before.b)){
   associationUndo=associationUndo.concat([before]).slice(-30);var list=Project.copy(associations),item=list[selectedAssociation];item.from=a;item.until=b;item.anchors=(item.anchors||[]).filter(function(point){return point.ms>a&&point.ms<b});associations=list;status="片段范围已更新；可点“撤销片段修改”恢复。";
  }
  applyLoop();storeTrack();wave.requestPaint();
 }
 function deleteAssociation(index){
  if(index<0||index>=associations.length)return;associationUndo=associationUndo.concat([{associations:Project.copy(associations),selected:selectedAssociation,a:a,b:b}]).slice(-30);
  var list=Project.copy(associations);list.splice(index,1);associations=list;selectedAssociation=Math.min(index,list.length-1);if(selectedAssociation>=0)selectAssociation(selectedAssociation);storeTrack();status="关联已删除；可点“撤销片段修改”恢复。";
 }
 function undoAssociation(){if(!associationUndo.length)return;var previous=associationUndo[associationUndo.length-1];associationUndo=associationUndo.slice(0,-1);associations=previous.associations;selectedAssociation=previous.selected;a=previous.a;b=previous.b;applyLoop();storeTrack();status="已恢复上一步片段修改。";wave.requestPaint()}
 function fitSlice(){if(!usable)return;var padding=Math.max(150,(b-a)*.08);viewStart=Math.max(0,a-padding);viewEnd=Math.min(media.duration,b+padding);viewportPeaks=[];wave.requestPaint();if(typeof media.requestWaveform==="function")media.requestWaveform(viewStart,viewEnd,Math.round(waveHost.width))}
'''+s[b:]
a=s.index('\n ColumnLayout {',a);b=s.index(' Dialog {id:trackNameDialog;',a)
wave_start=s.index('  Item {\n   id:waveHost;',a);wave_end=s.index('\n  RowLayout {',wave_start);wave=s[wave_start:wave_end]
wave=wave.replace('id:waveHost;clip:true;Layout.fillWidth:true;Layout.fillHeight:true;Layout.minimumHeight:root.compact?0:64;visible:!root.compact','id:waveHost;objectName:"referenceWaveform";clip:true;width:parent.width;height:Math.max(90,Math.min(360,root.height-290));visible:!root.compact')
a_mouse=wave.index('   MouseArea {');wave=wave[:a_mouse]+'''   MouseArea {
    id:waveMouse;objectName:"referenceWaveformMouse";anchors.fill:parent;acceptedButtons:Qt.LeftButton;hoverEnabled:true
    property real downX:0;property real downMs:0;property real downView:0;property real downSpan:0;property int handle:0;property bool moved:false;property bool panning:false
    cursorShape:root.spaceDown?Qt.OpenHandCursor:Qt.CrossCursor
    function ms(x){return Math.max(0,Math.min(root.media.duration,root.viewStart+(root.viewEnd-root.viewStart)*x/width))}
    onPressed:{if(!root.usable)return;root.forceActiveFocus();downX=mouse.x;downMs=ms(mouse.x);downView=root.viewStart;downSpan=root.viewEnd-root.viewStart;moved=false;panning=root.spaceDown;root.beginSlice();var ax=(root.a-root.viewStart)/(downSpan||1)*width,bx=(root.b-root.viewStart)/(downSpan||1)*width;handle=Math.abs(mouse.x-ax)<8?1:Math.abs(mouse.x-bx)<8?2:0;}
    onPositionChanged:{if(!pressed||!root.usable)return;if(Math.abs(mouse.x-downX)>3)moved=true;
     if(panning){root.spacePanned=root.spacePanned||moved;var left=Math.max(0,Math.min(root.media.duration-downSpan,downView-(mouse.x-downX)/width*downSpan));root.viewStart=left;root.viewEnd=left+downSpan;wave.requestPaint();return;}
     if(handle===1)root.a=Math.min(root.b-1,ms(mouse.x));else if(handle===2)root.b=Math.max(root.a+1,ms(mouse.x));else if(moved){root.selectedAssociation=-1;root.a=Math.min(downMs,ms(mouse.x));root.b=Math.max(downMs,ms(mouse.x));}
    }
    onReleased:{if(!root.usable)return;if(panning){root.sliceBefore=null;wave.requestPaint();return;}if(handle||moved)root.finishSlice();else{root.sliceBefore=null;root.media.seek(ms(mouse.x));}}
    onCanceled:{root.sliceBefore=null}
    onWheel:{root.zoom(wheel.angleDelta.y>0?.8:1.25,wheel.x/width);wheel.accepted=true}
   }
   Label {anchors.centerIn:parent;visible:!root.usable||!root.media.path;text:"将 WAV、MP3、FLAC 拖到这里";color:theme.muted}
  }
'''
body='''
 ColumnLayout {
  anchors.fill:parent;anchors.margins:8;spacing:6
  RowLayout {Layout.fillWidth:true
   Label {text:"原曲参考";font.bold:true;color:theme.text}
   Desk.DeskComboBox {objectName:"referenceTracks";Layout.fillWidth:true;Layout.minimumWidth:50;model:root.tracks.map(function(t){return t.name});currentIndex:root.selectedTrack;onActivated:root.selectTrack(currentIndex)}
   Desk.DeskButton {text:"打开";enabled:root.usable;onClicked:{root.addingAudio=false;audioDialog.open()}}
   Desk.DeskButton {text:"添加";visible:!root.compact;enabled:root.usable;onClicked:{root.addingAudio=true;audioDialog.open()}}
   Desk.DeskButton {text:"项目";enabled:root.usable;onClicked:projectMenu.open()}
   Desk.DeskButton {text:typeof panelFloating==="boolean"&&panelFloating?"停靠":"悬浮";visible:!root.narrow;onClicked:{if(typeof root.setPanelFloating==="function")root.setPanelFloating(!root.panelFloating)}}
  }
  Flow {Layout.fillWidth:true;Layout.preferredHeight:implicitHeight;spacing:5
   Desk.DeskComboBox {objectName:"referenceTransportTarget";width:90;model:["原曲","乐谱","一起播放"];currentIndex:root.transportTarget;onActivated:root.transportTarget=currentIndex}
   Desk.DeskButton {objectName:"referenceJointPlay";width:82;text:root.audioProject&&root.audioProject.playing||root.transportTarget===1&&root.observer&&root.observer.playing?"停止":root.media&&root.media.playing?"暂停":"播放";enabled:root.usable;onClicked:root.toggleReferencePlayback()}
   Label {width:82;height:28;text:root.usable?root.time(root.shownPosition):"0:00.000";verticalAlignment:Text.AlignVCenter;color:theme.text}
   Common.DragNumber {objectName:"referenceSpeed";width:100;value:root.usable?root.media.speed*100:100;minimum:50;maximum:150;sensitivity:.5;caption:"速度 ";suffix:"%";enabled:root.usable&&(!root.audioProject||!root.audioProject.playing);onEdited:root.media.speed=value/100;onEditingFinished:{root.storeTrack();root.persist()}}
   Common.DragNumber {objectName:"referenceVolume";width:112;value:root.usable?root.media.volume*100:80;minimum:0;maximum:100;caption:"音量 ";suffix:"%";rangeIndicator:true;enabled:root.usable&&(!root.audioProject||!root.audioProject.playing);onEdited:root.media.volume=value/100;onEditingFinished:{root.storeTrack();root.persist()}}
   Desk.DeskButton {text:"循环";visible:!root.compact;checkable:true;checked:root.looping;onClicked:{root.looping=checked;root.applyLoop()}}
  }
  ScrollView {Layout.fillWidth:true;Layout.fillHeight:true;visible:!root.compact;clip:true
   Column {width:root.width-32;spacing:6
    Flow {width:parent.width;spacing:6;visible:root.tracks.length>1
     CheckBox {text:"参加播放";checked:root.selectedTrack>=0&&root.tracks[root.selectedTrack].participate!==false;enabled:!root.audioProject||!root.audioProject.playing;onClicked:root.trackOption("participate",checked)}
     CheckBox {text:"静音";checked:root.selectedTrack>=0&&!!root.tracks[root.selectedTrack].mute;enabled:!root.audioProject||!root.audioProject.playing;onClicked:root.trackOption("mute",checked)}
     CheckBox {text:"独听";checked:root.selectedTrack>=0&&!!root.tracks[root.selectedTrack].solo;enabled:!root.audioProject||!root.audioProject.playing;onClicked:root.trackOption("solo",checked)}
     Common.DragNumber {objectName:"referenceMasterVolume";width:130;minimum:0;maximum:100;value:root.jointVolume*100;caption:"总音量 ";suffix:"%";rangeIndicator:true;onEdited:{root.jointVolume=value/100;if(root.audioProject&&typeof root.audioProject.volume==="number")root.audioProject.volume=value/100}onEditingFinished:root.storeTrack()}
    }
    RowLayout {width:parent.width;visible:root.transportTarget===2
     Desk.DeskComboBox {objectName:"referencePlaybackMode";enabled:!root.audioProject||!root.audioProject.playing;Layout.fillWidth:true;model:["开头对齐，各自播放","音频跟随乐谱","乐谱跟随选中音频"];currentIndex:root.playbackMode;onActivated:root.playbackMode=currentIndex}
     Label {text:root.tracks.filter(function(t){return t.participate!==false&&!t.mute}).length+" 条音轨";color:theme.muted}
    }
WAVE
    Flow {width:parent.width;spacing:5
     Common.DragNumber {objectName:"referenceSliceStart";width:126;value:root.a;minimum:0;maximum:Math.max(0,root.b-1);sensitivity:10;caption:"开始 ";formatter:root.time;parser:root.readTime;onEditingStarted:root.beginSlice();onEdited:root.a=value;onEditingFinished:root.finishSlice()}
     Common.DragNumber {objectName:"referenceSliceEnd";width:126;value:root.b;minimum:root.a+1;maximum:root.usable?root.media.duration:1;sensitivity:10;caption:"结束 ";formatter:root.time;parser:root.readTime;onEditingStarted:root.beginSlice();onEdited:root.b=value;onEditingFinished:root.finishSlice()}
     Desk.DeskButton {text:"片段视图";onClicked:root.fitSlice()}
     Desk.DeskButton {text:"全曲视图";enabled:root.usable;onClicked:{root.viewStart=0;root.viewEnd=root.media.duration;root.viewportPeaks=[];wave.requestPaint()}}
     Desk.DeskButton {text:"播放头设为开始";onClicked:{root.beginSlice();root.a=Math.min(root.b-1,root.shownPosition);root.finishSlice()}}
     Desk.DeskButton {text:"播放头设为结束";onClicked:{root.beginSlice();root.b=Math.max(root.a+1,root.shownPosition);root.finishSlice()}}
     Desk.DeskButton {text:"书签";enabled:root.usable;onClicked:{var list=Project.copy(root.bookmarks);list.push({ms:root.shownPosition,name:root.time(root.shownPosition)});root.bookmarks=list}}
     Desk.DeskButton {text:"边界淡入淡出";checkable:true;checked:root.fade;onClicked:{root.fade=checked;root.applyLoop()}}
    }
    Flow {width:parent.width;spacing:5
     Desk.DeskButton {objectName:"referenceAssociate";text:"关联当前选段";enabled:root.usable&&root.hasScore&&root.b>root.a;onClicked:root.associate()}
     Desk.DeskButton {objectName:"referenceLocate";text:"跳到乐谱";enabled:root.selectedAssociation>=0;onClicked:root.locate()}
     Desk.DeskButton {text:"从当前谱位定位音频";enabled:root.selectedAssociation>=0;onClicked:root.seekScore()}
     Desk.DeskButton {text:"内部对齐点";enabled:root.selectedAssociation>=0;onClicked:associationDialog.open()}
     Desk.DeskButton {text:"撤销片段修改";enabled:root.associationUndo.length>0;onClicked:root.undoAssociation()}
    }
    ListView {objectName:"referenceAssociations";width:parent.width;height:root.associations.length?Math.min(150,root.associations.length*(root.narrow?84:56)):30;clip:true;model:root.associations;currentIndex:root.selectedAssociation;ScrollBar.vertical:ScrollBar{}
     delegate:Rectangle {width:ListView.view.width;height:root.narrow?84:56;color:index===root.selectedAssociation?theme.selected:theme.field;border.color:theme.subtleLine
      MouseArea {anchors.fill:parent;onClicked:root.selectAssociation(index);onDoubleClicked:{root.selectAssociation(index);root.playAssociation()}}
      Column {x:6;y:5;width:parent.width-12;spacing:4
       Label {width:parent.width;text:modelData.name+" · "+root.time(modelData.from)+"–"+root.time(modelData.until);elide:Text.ElideRight;color:theme.text}
       Row {spacing:4
        Label {height:26;width:root.narrow?90:160;verticalAlignment:Text.AlignVCenter;text:"第 "+(modelData.occurrence||1)+" 遍"+(modelData.stale?" · 待核对":"")+(modelData.active===false?" · 未参加":"");color:theme.muted;font.pixelSize:11}
        Desk.DeskButton {text:"播放";implicitWidth:48;onClicked:{root.selectAssociation(index);root.playAssociation()}}
        Desk.DeskButton {text:"修改";implicitWidth:48;onClicked:{root.selectAssociation(index);associationDialog.open()}}
        Desk.DeskButton {text:"删除";implicitWidth:48;onClicked:root.deleteAssociation(index)}
       }
      }
     }
     Label {visible:root.associations.length===0;anchors.centerIn:parent;text:"拖出音频片段，选中乐谱小节，再点“关联当前选段”。";color:theme.muted;font.pixelSize:11}
    }
    Desk.DeskButton {objectName:"referencePlayAssociation";visible:root.selectedAssociation>=0;text:"播放选中片段";onClicked:root.playAssociation()}
    Label {width:parent.width;wrapMode:Text.Wrap;text:root.audioProject&&root.audioProject.playing?root.audioProject.status:root.status;color:theme.muted;font.pixelSize:11}
   }
  }
 }
'''.replace('WAVE',wave)
s=s[:a]+body+s[b:]
s=s.replace('内部锚点','内部对齐点').replace('锚点须位于片段内部，且谱位和原曲时间顺序一致','将乐谱光标和音频播放头放在片段内，两边的对齐点须按时间先后排列')
s=s.replace('Dialog {\n  id:associationDialog;title:"关联与内部对齐点";modal:true;width:340;height:380;', 'Dialog {\n  id:associationDialog;title:"片段与乐谱对应";modal:true;width:Math.min(380,root.width-16);height:Math.min(460,root.height-24);')
s=s.replace('   ListView {Layout.fillWidth:true;Layout.fillHeight:true;clip:true;model:root.selectedAssociation<0', '''   Label {Layout.fillWidth:true;wrapMode:Text.Wrap;text:"内部对齐点：标出录音中的这一刻，对应谱子的这一拍。先点乐谱位置，再点波形位置，最后添加。中间位置也会按这些点对齐。";color:theme.muted;font.pixelSize:11}
   Desk.DeskButton {text:"添加当前两个位置为对齐点";onClicked:root.addAnchor()}
   ListView {Layout.fillWidth:true;Layout.fillHeight:true;clip:true;model:root.selectedAssociation<0''')
s=s.replace('var list=Project.copy(root.associations);list.splice(root.selectedAssociation,1);root.associations=list;root.selectedAssociation=list.length?0:-1;associationDialog.close()', 'root.deleteAssociation(root.selectedAssociation);associationDialog.close()')
s=s.replace('onVisibleChanged:{if(!visible&&usable&&pauseWhenHidden)media.pause()}', 'onVisibleChanged:{if(!visible){spaceDown=false;spacePanned=false;if(usable&&pauseWhenHidden)media.pause();storeTrack();persist()}}')
s=s.replace('function selectTrack(index){','function selectTrack(index){\n  associationUndo=[];sliceBefore=null;')
s=s.replace('if(added){drop.acceptProposedAction();', 'if(added){drop.acceptProposedAction();')
p.write_text(s,encoding='utf8')
