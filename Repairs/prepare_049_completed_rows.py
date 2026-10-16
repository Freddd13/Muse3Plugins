from pathlib import Path
root=Path(__file__).resolve().parent;p=root.parent/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8')
def patch(old,new):
 global s
 assert s.count(old)==1,(old[:90],s.count(old));s=s.replace(old,new)
patch(' property var appliedProgress:({velocity:{},tempos:{}})',' property var appliedProgress:({velocity:{},tempos:{}})\n property bool showApplied:false\n property var displayed:Progress.display(result,appliedProgress,showApplied)\n onDisplayedChanged:publishComparison()')
patch('previewVersion:previewVersion,result:result,candidate:','previewVersion:previewVersion,result:displayed.result,candidate:')
patch(' onCandidateChanged:{previewVersion++;publishComparison()}',' onCandidateChanged:{previewVersion++;publishComparison();if(candidate&&previewing&&!legacyAudition&&playbackState.playing&&playbackState.mode==="candidate"&&!applying&&!refreshingApplication){pendingAudition=true;auditionRetry.restart()}}')
patch('&&!root.stale&&!root.previewing)root.build()','&&!root.stale&&(!root.previewing||!root.legacyAudition))root.build()')
patch('if(result.matches){root.result=result;','if(result.matches){root.appliedProgress=Progress.changedMatches(root.appliedProgress,root.result,result);root.result=result;')
patch('Layout.minimumHeight:100;model:root.result.matches;currentIndex:root.selected','Layout.minimumHeight:72;model:root.displayed.rows;currentIndex:root.displayed.indexes[root.selected]===undefined?-1:root.displayed.indexes[root.selected]')
begin=s.index('   delegate:ItemDelegate {',s.index('id:matches;'));end=s.index('\n  RowLayout {',begin)
block=s[begin:end]
block=block.replace('width:parent.width;height:34;highlighted:index===root.selected','property var match:modelData.match\n    width:parent.width;height:34;highlighted:modelData.index===root.selected')
block=block.replace('modelData.original','match.original').replace('modelData.pitch','match.pitch').replace('modelData.seconds','match.seconds').replace('modelData.velocity','match.velocity').replace('modelData.confidence','match.confidence')
block=block.replace('root.selected=index;','root.selected=modelData.index;').replace('+(match.confidence<.8?', '+(modelData.applied?" · 已使用":"")+(match.confidence<.8?')
s=s[:begin]+block+s[end:]
patch('matches.positionViewAtIndex(Math.max(0,root.selected),ListView.Center)','matches.positionViewAtIndex(Math.max(0,matches.currentIndex),ListView.Center)')
patch(' Menu {id:applicationMenu',' Menu {id:applicationMenu\n  MenuItem {text:"显示已使用的对应";checkable:true;checked:root.showApplied;onTriggered:root.showApplied=checked}')
patch('  RowLayout {visible:!root.compact;Layout.fillWidth:true\n   Label {text:"使用范围"','  Label {visible:!root.compact&&root.result.matches.length>0&&!root.displayed.rows.length;Layout.fillWidth:true;wrapMode:Text.Wrap;color:theme.muted;text:"这段的演奏力度已使用。可在更多中查看已用对应，或恢复应用前力度。"}\n  RowLayout {visible:!root.compact;Layout.fillWidth:true\n   Label {text:"使用范围"')
p.write_text(s,encoding='utf8',newline='\n');print('Applied correspondences leave the pending view; comparison updates while paused or playing')
