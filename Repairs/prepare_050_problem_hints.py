from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
def replace(old,new):
 global s
 assert old in s,old[:70];s=s.replace(old,new)
replace('import "Rules.js" as Rules','import "Rules.js" as Rules\nimport "Presentation.js" as Presentation')
replace('    property var issues:[]','    property var issues:[]\n    property var hintGroups:Presentation.groups(issues)\n    property int hintTick:-1\n    property var nearbyIssues:issues.filter(function(issue){return issue.tick===root.hintTick})')
replace('    onCurrentChanged:publishMarkers()','''    onCurrentChanged:{if(observer&&typeof observer.setActiveScorePreview==="function")observer.setActiveScorePreview(current?current.tick:-1);if(problemHint.visible)positionProblemHint()}
    onHintGroupsChanged:publishMarkers()''')
start=s.index('    function publishMarkers() {');end=s.index('    function persist()',start)
s=s[:start]+'''    function publishMarkers() {
        if(!observer || typeof observer.setScorePreview!=="function")return
        if(!config.scoreHints || !activeSurface){observer.setScorePreview([]);return}
        var markers=[]
        hintGroups.forEach(function(group){
            if(!group.note)return
            var marker=Rules.clone(group.note)
            marker.degree=group.indexes.length+"项";marker.color="";marker.label="";marker.active=false;marker.chord=""
            marker.chordTick=group.tick;marker.chordUntil=group.tick+1;marker.degreeFont="Arial";marker.chordScale=.85
            marker.onTop=true;marker.avoidScoreContent=true;marker.avoidOtherPreviews=true;marker.chordMask=true
            marker.leader=root.config.hintLines===true;marker.chordColor=root.stale?String(theme.muted):String(theme.text)
            markers.push(marker)
        })
        observer.setScorePreview(markers)
        if(typeof observer.setActiveScorePreview==="function")observer.setActiveScorePreview(current?current.tick:-1)
    }
    function positionProblemHint() {
        if(!current||!current.notes.length||!observer||typeof observer.scoreLocation!=="function")return
        var note=current.notes[0],point=observer.scoreLocation(note.tick,note.track)
        if(point.x===undefined)return
        var left=point.screenX+8,top=point.screenY+8,right=point.screenX+point.screenWidth-8,bottom=point.screenY+point.screenHeight-8
        problemHint.x=Math.max(left,Math.min(right-problemHint.width,point.x+point.width+12))
        problemHint.y=Math.max(top,Math.min(bottom-problemHint.height,point.y+point.height+8))
    }
    function openProblemHint(tick) {
        var index=issues.findIndex(function(issue){return issue.tick===tick})
        if(index<0)return
        hintTick=tick
        if(!current||current.tick!==tick)list.currentIndex=index
        positionProblemHint();problemHint.show();problemHint.raise()
    }
'''+s[end:]
replace('    function locate() {','    function locate(keepScoreFocus) {')
replace('if(typeof root.focusPanel==="function")root.focusPanel()\n    }\n    function ignore()', 'if(!keepScoreFocus && typeof root.focusPanel==="function")root.focusPanel()\n    }\n    function ignore()')
replace('        onPreviewActivated:root.locate()','        onPreviewActivated:root.openProblemHint(tick)')
replace('if(!activeSurface) {cancel();refresh.stop()}','if(!activeSurface) {cancel();refresh.stop();problemHint.hide()}')
replace('''        pendingData=null;dirtyStart=-1;dirtyEnd=-1;switchingScore=false;publishMarkers()''','''        pendingData=null;dirtyStart=-1;dirtyEnd=-1;switchingScore=false;problemHint.hide();publishMarkers()''')
replace('MouseArea {anchors.fill:parent;onClicked:{list.currentIndex=index;if(!root.observer || !root.observer.playing)root.locate()}}','MouseArea {anchors.fill:parent;onClicked:{list.currentIndex=index;if(!root.observer || !root.observer.playing){root.locate();if(root.config.scoreHints)root.openProblemHint(modelData.tick)}}}')
replace('text:"在谱面提示当前问题"','text:"在谱面显示问题位置"')
needle='''                Desk.DeskSwitch {text:"在谱面显示问题位置";checked:root.config.scoreHints;onClicked:{var c=Rules.clone(root.config);c.scoreHints=checked;root.config=c;root.persist();root.publishMarkers()}}'''
replace(needle,needle+'''
                Desk.DeskSwitch {text:"提示与相关音之间画细线";checked:root.config.hintLines===true;onClicked:{var c=Rules.clone(root.config);c.hintLines=checked;root.config=c;root.persist();root.publishMarkers()}}''')
needle='    Window {id:floatingDetails;'
popup='''    Window {
        id:problemHint;objectName:"arrangementProblemHint";title:"编配提示";width:350;height:300;flags:Qt.Tool;color:theme.background
        ColumnLayout {
            anchors.fill:parent;anchors.margins:10;spacing:6
            Label {Layout.fillWidth:true;wrapMode:Text.WordWrap;font.bold:true;color:theme.text;text:root.current?"第 "+root.current.bar+" 小节 · "+root.current.title:"编配提示"}
            ListView {Layout.fillWidth:true;Layout.preferredHeight:Math.min(90,root.nearbyIssues.length*30);clip:true;model:root.nearbyIssues
                delegate:ItemDelegate {width:parent.width;height:30;text:modelData.title;highlighted:root.current&&root.current.id===modelData.id;onClicked:{list.currentIndex=root.issues.findIndex(function(issue){return issue.id===modelData.id});root.locate(true)}}
            }
            ScrollView {Layout.fillWidth:true;Layout.fillHeight:true;clip:true
                Text {width:problemHint.width-28;wrapMode:Text.WordWrap;color:theme.text;text:root.current?root.current.basis:""}
            }
            RowLayout {Layout.fillWidth:true
                Desk.DeskButton {text:"定位相关音";enabled:!!root.current;onClicked:root.locate(true)}
                Desk.DeskButton {text:"忽略此处";enabled:!!root.current;onClicked:{root.ignore();problemHint.hide()}}
                Item {Layout.fillWidth:true}
                Desk.DeskButton {text:"关闭";onClicked:problemHint.hide()}
            }
        }
    }
    Timer {interval:200;repeat:true;running:problemHint.visible;onTriggered:root.positionProblemHint()}
'''
replace(needle,popup+needle)
p.write_text(s,encoding='utf8',newline='\n')
