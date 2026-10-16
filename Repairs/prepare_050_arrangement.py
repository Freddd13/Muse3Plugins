from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'ArrangementAssistant/ArrangementAssistant_MS3.qml';s=p.read_text(encoding='utf8')
def replace(old,new):
 global s
 assert old in s,old[:75];s=s.replace(old,new)
replace('property int preferredRibbonHeight:76','property int preferredRibbonHeight:36\n    property bool independentPanelSurfaces:true\n    property string summaryPanelTitle:"编配检查摘要"')
replace('    property var owner:null','''    property var owner:null
    property string ownerId:""
    property string contentRevision:""
    property bool switchingScore:false
    property var scoreCache:({})
    property var cachedScores:[]
    property bool dualDetailActive:ribbon && typeof root.detailPanelVisible==="boolean" && root.detailPanelVisible
    property bool dualSummaryActive:!ribbon && typeof root.summaryPanelVisible==="boolean" && root.summaryPanelVisible''')
replace('property bool activeSurface:visible && (!observer || observer.surfaceVisible)','property bool activeSurface:(visible || dualDetailActive || dualSummaryActive || floatingDetails.visible) && (!observer || observer.surfaceVisible)')
replace('''    function syncDetail() {
        if(typeof root.showDetailPanel==="function")root.showDetailPanel(ribbon && config.dualPanel)
    }''','''    function syncSurfaces() {
        if(observer && typeof observer.auxiliarySurfaceVisible==="boolean") {
            observer.auxiliarySurfaceVisible=dualDetailActive || dualSummaryActive || floatingDetails.visible
            observer.enabled=visible || observer.auxiliarySurfaceVisible
        }
    }
    function syncDetail() {
        if(!started)return
        if(typeof root.showDetailPanel==="function")root.showDetailPanel(ribbon && config.dualPanel)
        if(typeof root.showSummaryPanel==="function")root.showSummaryPanel(!ribbon && config.dualPanel)
        syncSurfaces()
    }
    function openDetails() {
        if(!ribbon) {if(typeof root.focusPanel==="function")root.focusPanel();return}
        if(typeof root.showDetailPanel==="function") {var c=Rules.clone(config);c.dualPanel=true;config=c;persist();root.showDetailPanel(true)}
        else floatingDetails.show()
    }
    function hideSummary() {
        if(dualSummaryActive) {root.showSummaryPanel(false);var c=Rules.clone(config);c.dualPanel=false;config=c;persist()}
        else if(typeof root.hidePanel==="function")root.hidePanel()
        syncSurfaces()
    }
    function auxiliaryClosed() {var c=Rules.clone(config);c.dualPanel=false;config=c;persist();syncSurfaces()}
    onDualDetailActiveChanged:syncSurfaces()
    onDualSummaryActiveChanged:syncSurfaces()
    Connections {target:root;ignoreUnknownSignals:true;onPanelDetailClosed:root.auxiliaryClosed();onPanelSummaryClosed:root.auxiliaryClosed()}''')
replace('            list.currentIndex=issues.length?0:-1;work.stop();workerToken=0;publishMarkers()','            list.currentIndex=issues.length?0:-1;work.stop();workerToken=0;contentRevision=typeof observer.analysisContentRevision==="function"?observer.analysisContentRevision():revision;publishMarkers()')
start=s.index('    function newScore() {');end=s.index('    onRun: {',start)
s=s[:start]+'''    function rememberScore() {
        if(!ownerId)return
        scoreCache[ownerId]={scope:scope,config:Rules.clone(config),issues:issues,roles:roles,imported:imported,
            counts:counts,analyzed:analyzed,requested:requested,cachedData:cachedData,stale:stale||running,
            contentRevision:contentRevision,current:list.currentIndex,status:status}
        var order=cachedScores.filter(function(key){return key!==root.ownerId});order.push(ownerId)
        while(order.length>4)delete scoreCache[order.shift()]
        cachedScores=order
    }
    function newScore() {
        if(switchingScore)return
        switchingScore=true
        if(observer)observer.score=curScore
        var id=curScore?(observer&&typeof observer.analysisScoreId==="function"?observer.analysisScoreId():(owner===curScore?ownerId:"score-"+Date.now())):""
        if(id===ownerId){owner=curScore;switchingScore=false;return}
        rememberScore();cancel();refresh.stop();owner=curScore;ownerId=id
        var saved=scoreCache[id]
        if(saved) {
            scope=saved.scope;config=saved.config;issues=saved.issues;roles=saved.roles;imported=saved.imported
            counts=saved.counts;analyzed=saved.analyzed;requested=saved.requested;cachedData=saved.cachedData
            contentRevision=saved.contentRevision;revision=observer.analysisRevision()
            stale=saved.stale || (typeof observer.analysisContentRevision==="function" && contentRevision!==observer.analysisContentRevision())
            list.currentIndex=Math.min(saved.current,issues.length-1);status=stale?"正在检查更新":saved.status
        } else {
            var c=Rules.clone(config);c.roles={};c.handOverrides=[];c.ignored=[];c.chords=[];config=c
            scope={start:0,end:0,firstTrack:0,endTrack:8};imported=[];issues=[];roles=[];counts={harmony:0,counterpoint:0,playability:0}
            analyzed=false;requested=false;cachedData=null;stale=false;revision="";contentRevision="";status="选择谱段，点击更新结果开始检查"
        }
        pendingData=null;dirtyStart=-1;dirtyEnd=-1;switchingScore=false;publishMarkers()
        if(requested && stale && config.autoRefresh && activeSurface && !observer.playing)refresh.restart()
    }
'''+s[end:]
replace('''        if(owner!==curScore)newScore()
        else if(observer && requested && observer.analysisRevision()!==revision)markDirty(state.startLayoutTick,state.endLayoutTick)''','''        newScore()
        if(observer && requested && observer.analysisRevision()!==revision)markDirty(state.startLayoutTick,state.endLayoutTick)''')
replace('Component.onDestruction:{cancel();persist()}','Component.onDestruction:{cancel();persist()}')
# The same summary row can live in the top dock while the details remain on the right.
replace('id:summary;anchors.top:parent.top;anchors.left:parent.left;anchors.right:parent.right;anchors.margins:8;height:root.ribbon?52:32','''id:summary;parent:root.dualSummaryActive?root.summaryPanelHost:root
        visible:root.ribbon||root.dualSummaryActive
        anchors.top:parent.top;anchors.left:parent.left;anchors.right:parent.right;anchors.margins:4;height:28;spacing:4''')
replace('visible:root.width>620 || !root.ribbon','visible:summary.width>780')
replace('visible:root.ribbon && root.config.alignment>0','visible:root.config.alignment>0')
replace('visible:root.ribbon && root.width>750','visible:summary.width>880')
replace('visible:root.ribbon}', 'visible:true}')
replace('Layout.maximumWidth:140','Layout.maximumWidth:120')
replace('visible:!root.ribbon || root.config.alignment<2','visible:root.config.alignment<2')
replace('''        Desk.DeskButton {text:"分析";enabled:!root.running && (!root.observer || !root.observer.playing);onClicked:root.start(false)}
        Desk.DeskButton {text:root.ribbon?"详情":"设置";onClicked:{if(root.ribbon) {if(typeof root.showDetailPanel==="function")root.showDetailPanel(true);else floatingDetails.show()} else settings.open()}}''','''        Desk.DeskButton {text:"更新";enabled:!root.running && (!root.observer || !root.observer.playing);onClicked:root.start(root.requested)}
        Desk.DeskButton {text:"详情";onClicked:root.openDetails()}
        Desk.DeskButton {text:"×";ToolTip.visible:hovered;ToolTip.text:"隐藏摘要，详情继续保留";onClicked:root.hideSummary()}''')
replace('anchors.fill:parent;anchors.topMargin:root.ribbon?8:summary.height+16;anchors.margins:8','anchors.fill:parent;anchors.margins:8')
needle='''            anchors.fill:parent;spacing:6
            RowLayout {
                Layout.fillWidth:true
                Desk.DeskComboBox {id:rangeBox;'''
replacement='''            anchors.fill:parent;spacing:6
            RowLayout {
                Layout.fillWidth:true
                Label {text:"编配检查";font.bold:true;color:theme.text;Layout.fillWidth:true}
                Desk.DeskButton {text:"顶部摘要";onClicked:{var c=Rules.clone(root.config);c.dualPanel=true;root.config=c;root.persist();if(root.ribbon)root.focusPanel();else root.showSummaryPanel(true)}}
                Desk.DeskButton {text:"设置";onClicked:settings.open()}
            }
            Label {Layout.fillWidth:true;elide:Text.ElideRight;color:theme.text;text:root.requested?"检查范围：第 "+root.scope.firstMeasure+"–"+root.scope.lastMeasure+" 小节 · "+(root.scope.part||"钢琴"):"选择要检查的小节"}
            RowLayout {
                Layout.fillWidth:true
                Desk.DeskButton {objectName:"arrangementUpdate";text:"更新结果";Layout.fillWidth:true;enabled:!root.running&&(!root.observer||!root.observer.playing);onClicked:root.start(root.requested)}
                Desk.DeskButton {objectName:"arrangementNewScope";text:root.whole?"改查钢琴全谱":"改查当前选区";Layout.fillWidth:true;enabled:!root.running&&(!root.observer||!root.observer.playing);onClicked:root.start(false)}
            }
            RowLayout {
                Layout.fillWidth:true
                Desk.DeskComboBox {id:rangeBox;'''
replace(needle,replacement)
p.write_text(s,encoding='utf8',newline='\n')
