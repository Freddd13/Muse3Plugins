from pathlib import Path
root=Path(__file__).resolve().parent;path=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml'
s=path.read_text(encoding='utf8')
def edit(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old));s=s.replace(old,new)
edit(' property bool previewing:false',' property bool previewing:false\n property bool legacyAudition:false\n property var playbackState:editorContext&&editorContext.audition?editorContext.audition:({})')
edit('readForCapture=false;if(captureSession)captureSession.cancel();','readForCapture=false;refreshingApplication=false;if(captureSession)captureSession.cancel();')
edit(' function returnOriginal(){if(previewing',' function returnOriginal(){if(!legacyAudition&&typeof observer.finishExpressionAudition==="function"){observer.finishExpressionAudition();previewing=false;status="已结束比较，可以继续编辑乐谱。";return true;}if(previewing')
edit(' function advanceAudition(){\n  if(pendingAudition===null)return;',''' function advanceAudition(){
  if(pendingAudition===null)return;
  if(!auditionAudio&&typeof observer.auditionExpression==="function"){
   if(legacyAudition&&previewing&&!returnOriginal()){pendingAudition=null;return;}
   var chosen=pendingAudition;pendingAudition=null;legacyAudition=false;beginAudition(chosen);return;
  }''')
edit('  previewing=true;\n  var range=Project.copy(scope);','''  previewing=true;
  var range=Project.copy(scope);range.occurrence=Math.max(1,occurrence);
  if(!auditionAudio&&typeof observer.auditionExpression==="function"){
   var prepared=candidate||{revision:revision,scope:scope,velocity:[],tempos:[]};
   var playing=observer.auditionExpression(materials,prepared,range,useCandidate);
   if(playing.error){previewing=false;fail(playing.error);}else status="正在播放："+(useCandidate?"拟采用效果":"谱中效果")+"。切换效果会接着当前拍位播放。";
   return;
  }
  legacyAudition=true;''')
edit('  if(previewing||applying||refreshingApplication)return;','  if((previewing&&legacyAudition)||applying||refreshingApplication)return;')
edit('Component.onDestruction:{if(previewing&&observer)observer.returnWorkflowSource();cancel()}','Component.onDestruction:{if(previewing&&observer)returnOriginal();cancel()}')
edit('   Desk.DeskButton {text:root.advancedSettings?"收起设置":"更多设置";onClicked:root.advancedSettings=!root.advancedSettings}','   Desk.DeskButton {text:"设置";onClicked:{root.advancedSettings=true;expressionSettings.open()}}')
# Detailed recording/alignment options have their own scrolling window.
begin=s.index('  GridLayout {\n   visible:root.advancedSettings&&!root.compact;columns:2;Layout.fillWidth:true')
end=s.index('  RowLayout {\n   Layout.fillWidth:true\n   Desk.DeskButton {text:"重新对应"',begin)
settings=s[begin:end].replace('visible:root.advancedSettings&&!root.compact;columns:2;Layout.fillWidth:true','columns:2;width:parent.width')
s=s[:begin]+s[end:]
marker=' property string issueKind:"missing"'
dialog=''' Dialog {id:expressionSettings;title:"录制与对应设置";modal:false;width:Math.max(300,Math.min(420,root.width));height:440;standardButtons:Dialog.Close
  ScrollView {anchors.fill:parent;clip:true
'''+settings+'''  }
 }
'''
edit(marker,dialog+marker)
# Keep the main actions in a stable position and give every primary button equal width.
begin=s.index('  GridLayout {\n   columns:2;visible:!root.compact;Layout.fillWidth:true',s.index('objectName:"expressionApplicationScope"'))
end=s.index('\n }\n Dialog {id:expressionSettings',begin)
s=s[:begin]+'''  Label {visible:!root.compact&&root.previewing;Layout.fillWidth:true;elide:Text.ElideRight;color:theme.accent;text:(root.playbackState.playing?"正在播放：":"已暂停：")+(root.playbackState.mode==="candidate"?"拟采用效果":"谱中效果")}
  RowLayout {visible:!root.compact;Layout.fillWidth:true
   Desk.DeskButton {objectName:"expressionOriginalAudition";Layout.fillWidth:true;text:"谱中效果";enabled:root.notes.length>0&&!root.busy&&!root.stale;onClicked:root.audition(false)}
   Desk.DeskButton {objectName:"expressionCandidateAudition";Layout.fillWidth:true;text:"拟采用效果";enabled:root.candidate!==null&&!root.busy&&!root.stale;onClicked:root.audition(true)}
   Desk.DeskButton {objectName:"expressionStop";text:"停止";visible:root.previewing;onClicked:root.stopAudition()}
  }
  RowLayout {visible:!root.compact;Layout.fillWidth:true
   Desk.DeskButton {objectName:"expressionApplyVelocity";Layout.fillWidth:true;text:"使用力度";enabled:root.candidate!==null&&root.candidate.velocity.length>0&&!root.busy&&!root.stale;onClicked:root.applyPart("velocity")}
   Desk.DeskButton {objectName:"expressionApplyTempo";Layout.fillWidth:true;text:"使用速度";visible:root.config.rubato;enabled:root.candidate!==null&&root.candidate.tempos.length>0&&!root.busy&&!root.stale;onClicked:root.applyPart("tempo")}
   Desk.DeskButton {text:"更多";onClicked:applicationMenu.open()}
  }
  CheckBox {visible:!root.compact;objectName:"expressionKeepManual";text:"保留手动调整";checked:root.config.keepManual===true;onClicked:root.editConfig("keepManual",checked)}
  Label {visible:!root.compact;Layout.fillWidth:true;elide:Text.ElideRight;text:root.candidate?"可使用力度 "+root.candidate.velocity.length+" 个音 · 速度 "+root.candidate.tempos.length+" 处":"选中谱段后导入 MIDI，或直接录制。";color:theme.muted}
  RowLayout {visible:!root.compact&&root.previewing;Layout.fillWidth:true
   Desk.DeskButton {objectName:"expressionReturn";text:"结束比较";onClicked:{root.pendingAudition=null;auditionRetry.stop();root.returnOriginal()}}
   Item {Layout.fillWidth:true}
  }
''' +s[end:]
edit(' Menu {id:projectMenu',''' Menu {id:applicationMenu
  MenuItem {text:"查看每个音的变化";enabled:root.candidate!==null;onTriggered:changes.open()}
  MenuItem {objectName:"expressionRestoreVelocity";text:"恢复应用前力度";enabled:root.savedVelocityCount>0&&!root.busy;onTriggered:root.restoreVelocity(false)}
  MenuItem {text:"以当前力度为比较起点";enabled:!root.busy;onTriggered:root.restoreVelocity(true)}
  MenuItem {text:"重新比较已使用的结果";enabled:!root.busy&&!root.stale;onTriggered:{root.appliedProgress=({velocity:{},tempos:{}});root.build()}}
  MenuItem {text:"试听时播放参考音频";checkable:true;checked:root.auditionAudio;enabled:root.audioProject&&root.audioProject.available;onTriggered:root.auditionAudio=checked}
 }
 Menu {id:projectMenu''')
# Keep progress when saving an expression workspace, and reset it for newly imported performances.
edit('anchors:manualAnchors,links:links,mode:mode,role:role','anchors:manualAnchors,links:links,applied:appliedProgress,mode:mode,role:role')
edit('workspace=String(url);loadedSourceHash=data.sha256||"";','workspace=String(url);appliedProgress=data.applied||({velocity:{},tempos:{}});loadedSourceHash=data.sha256||"";')
path.write_text(s,encoding='utf8',newline='\n');print('Expression playback controls and main operation layout updated')
