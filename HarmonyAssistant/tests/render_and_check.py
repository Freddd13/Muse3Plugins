import os,sys,json
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software'
os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QMetaObject,QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
app=QGuiApplication(sys.argv)
app.setOrganizationName("HarmonyTests");app.setApplicationName("PanelTests")
engine=QQmlApplicationEngine()
engine.warnings.connect(lambda warnings: print('\n'.join(warning.toString() for warning in warnings)))
engine.addImportPath(str(HERE/'qml'))
source=(BASE/'HarmonyAssistant_MS3.qml').read_text(encoding='utf-8-sig')
fixture=r'''
    property var fixtureNotes: []
    property int fixtureCommands: 0
    property string testResult: ""
    QtObject {
        id: fixtureObserver
        property var score: null
        property bool playing: false
        property int tick: 480
        property bool enabled: true
        property bool surfaceVisible: true
        property var preview: []
        property int previewUpdates: 0
        signal positionChanged()
        function clearNotePreviewColors(){preview=[]}
        function setNotePreviewColors(notes){preview=notes;previewUpdates++}
        function snapshot(tick,first,end,sounding) {
            var notes=[]
            for(var t=0;t<root.timeline.length;++t){var e=Harmony.atTick(root.timeline[t],tick);if(e)notes=notes.concat(e.notes)}
            return {notes:notes,keySignature:0,bar:Math.floor(tick/1920)+1,beat:Math.floor(tick/480)%4+1}
        }
    }
    function fixture() {
        var segment0={tick:0,type:Element.SEGMENT,segmentType:Segment.ChordRest}
        var segment1={tick:480,type:Element.SEGMENT,segmentType:Segment.ChordRest}
        var segment2={tick:960,type:Element.SEGMENT,segmentType:Segment.ChordRest}
        segment0.next=segment1; segment1.next=segment2; segment2.next=null
        function chord(segment,track,pitches,tpcs,duration) {
            var c={type:Element.CHORD,track:track,parent:segment,actualDuration:{ticks:duration},notes:[]}
            for(var i=0;i<pitches.length;++i)c.notes.push({type:Element.NOTE,parent:c,track:track,pitch:pitches[i],tpc:tpcs[i],color:i===0?"#123456":"#202020"})
            return c
        }
        var bass=chord(segment0,4,[36,52,55],[14,18,15],960)
        var treble=chord(segment1,0,[59,62,69],[19,16,17],480)
        var custom=chord(segment0,8,[61],[21],960)
        segment0.elementAt=function(t){return t===4?bass:t===8?custom:null}
        segment1.elementAt=function(t){return t===0?treble:null}
        segment2.elementAt=function(t){return {type:Element.REST,track:t,parent:segment2,actualDuration:{ticks:480}}}
        var score={token:1,nstaves:3,parts:[{startTrack:0,endTrack:8,partName:"钢琴"},{startTrack:8,endTrack:12,partName:"其他乐器"}],selection:{elements:[treble.notes[0]],isRange:false}}
        score.is=function(other){return !!other && other.token===1}
        score.firstSegment=function(){return segment0}
        score.newCursor=function(){return {track:0,segment:null,keySignature:0,rewindToTick:function(t){this.segment=t===0?segment0:t===480?segment1:segment2}}}
        score.startCmd=function(){fixtureCommands++}
        score.endCmd=function(){root.scoreStateChanged({selectionChanged:false,startLayoutTick:0})}
        fixtureNotes=bass.notes.concat(treble.notes)
        curScore=score; scores=[score]; root.run()
    }
    function checkFixture() {
        var failures=[]
        function check(condition,label){if(!condition)failures.push(label)}
        check(chordText==="Cmaj13","sustained piano chord: "+chordText)
        check(currentNotes.length===6,"scope excludes other instrument")
        check(toneRows[6].present,"13 role present")
        check(fixtureCommands===0,"read-only default")
        scoreColoring.checked=true
        undoPause=false; repaintNotes()
        check(fixtureNotes[0].color!=="#123456","color applied")
        var commands=fixtureCommands
        repaintNotes()
        check(fixtureCommands===commands,"no-op recolor produces no command")
        displayTick(960,true)
        check(currentNotes.length===0,"empty beat clears tones")
        check(fixtureNotes[0].color==="#123456","original custom color restored on rest")
        displayTick(480,true)
        stopColoring()
        check(fixtureNotes[0].color==="#123456","restore button")
        scoreColoring.checked=true
        undoPause=false; repaintNotes()
        fixtureNotes[0].color="#abcdef"
        stopColoring()
        check(fixtureNotes[0].color==="#abcdef","user color edit preserved")
        scoreColoring.checked=true
        undoPause=false; repaintNotes()
        commands=fixtureCommands
        root.scoreStateChanged({undoRedo:true,startLayoutTick:0})
        check(fixtureCommands===commands,"undo callback writes nothing")
        check(!scoreColoring.checked,"undo suspends coloring")
        refreshTimer.stop()
        displayTick(480,true)
        check(fixtureCommands===commands,"undo pause survives refresh")
        stopColoring()
        curScore.selection.elements=[]
        refreshSelection()
        check(currentNotes.length===0 && chordRoot===-1,"empty selection clears display")
        curScore.selection.elements=[fixtureNotes[3]]
        refreshSelection()
        while(buildTimer.running)buildChunk()
        // Test the read-only bridge without modifying the actual Evolution process.
        playbackAvailable=true
        curScore.harmonyPlaybackTick=480
        curScore.harmonyPlaybackActive=true
        scoreColoring.checked=true
        undoPause=false; repaintNotes()
        pollHost()
        commands=fixtureCommands
        check(lastPlaying && currentNotes.length===6,"playback start")
        curScore.harmonyPlaybackTick=960
        pollHost()
        check(currentNotes.length===0,"playback enters rest")
        curScore.harmonyPlaybackTick=480
        pollHost()
        check(currentNotes.length===6,"playback repeat / backward jump")
        check(fixtureCommands===commands,"playback updates do not write score")
        curScore.harmonyPlaybackActive=false
        pollHost()
        check(!lastPlaying,"playback stop")
        stopColoring()
        refreshTimer.stop()
        playbackAvailable=false
        displayTick(480,true)
        observer=fixtureObserver
        fixtureObserver.score=curScore
        cacheDirty=false
        playbackAvailable=true
        scoreColoring.checked=true
        var original=fixtureNotes[0].color
        commands=fixtureCommands
        displayTick(480,true)
        check(chordText==="Cmaj13","native snapshot chord")
        check(fixtureObserver.preview.length===6,"native preview descriptors")
        check(fixtureNotes[0].color===original,"native preview leaves actual color unchanged")
        check(fixtureCommands===commands,"native preview has no undo command")
        fixtureObserver.playing=true
        fixtureObserver.tick=960
        followNativePosition()
        check(currentNotes.length===0 && fixtureObserver.preview.length===0,"native playback rest clears colors")
        fixtureObserver.tick=480
        followNativePosition()
        check(currentNotes.length===6 && fixtureObserver.preview.length===6,"native playback jump recolors")
        root.scoreStateChanged({undoRedo:true,startLayoutTick:0})
        check(scoreColoring.checked,"native undo preserves safe coloring preference")
        check(fixtureCommands===commands,"native playback and undo remain read-only")
        fixtureObserver.playing=false
        followNativePosition()
        refreshTimer.stop()
        displayTick(480,true)
        stopColoring()
        check(fixtureObserver.preview.length===0,"native restore clears layer")
        scoreColoring.checked=true
        repaintNotes()
        noticeText=""
        testResult=JSON.stringify({failures:failures,commands:fixtureCommands})
    }
    function hideFixture() {
        fixtureObserver.playing=true
        lastPlaying=true
        fixtureObserver.surfaceVisible=false
    }
    function showFixture() {
        var result=JSON.parse(testResult)
        result.hidden={active:surfaceActive,visible:fixtureObserver.surfaceVisible,refresh:refreshTimer.running,play:playbackTimer.running,started:started,observer:observer===fixtureObserver}
        if(surfaceActive || refreshTimer.running || playbackTimer.running)
            result.failures.push("hidden native surface stops timers")
        fixtureObserver.playing=false
        fixtureObserver.surfaceVisible=true
        testResult=JSON.stringify(result)
    }
    function checkShownFixture() {
        var result=JSON.parse(testResult)
        result.shown={active:surfaceActive,playing:lastPlaying,visible:fixtureObserver.surfaceVisible}
        if(lastPlaying) result.failures.push("showing after hidden stop restores selection mode")
        testResult=JSON.stringify(result)
    }
'''
source=source.replace('    Rectangle {\n        id:backdrop',fixture+'\n    Rectangle {\n        id:backdrop',1)
window=QQuickWindow();window.resize(360,740)
# loadData with original URL keeps relative JS/component imports working.
engine.loadData(source.encode('utf-8'),QUrl.fromLocalFile(str(BASE/'HarmonyAssistant_MS3.qml')))
if not engine.rootObjects():sys.exit('QML failed to load')
root=engine.rootObjects()[0]
root.setParentItem(window.contentItem());root.setWidth(360);root.setHeight(740)
window.show()
QMetaObject.invokeMethod(root,'fixture')
def checks():
 QMetaObject.invokeMethod(root,'checkFixture')
 QMetaObject.invokeMethod(root,'hideFixture')
 QTimer.singleShot(30,show_fixture)

def show_fixture():
 QMetaObject.invokeMethod(root,'showFixture')
 QTimer.singleShot(80,finish_checks)

def finish_checks():
 QMetaObject.invokeMethod(root,'checkShownFixture')
 result=json.loads(root.property('testResult'));print(json.dumps(result,ensure_ascii=True))
 if result['failures']: app.exit(1);return
 capture(360,740,'panel-360.png')
 QTimer.singleShot(100,lambda:capture(280,740,'panel-280.png'))
 QTimer.singleShot(200,lambda:capture(460,900,'panel-460.png'))
 QTimer.singleShot(350,expanded)
 QTimer.singleShot(1000,lambda:capture(1000,150,"panel-ribbon.png"))
 QTimer.singleShot(1150,lambda:capture(900,740,"panel-wide.png"))
 QTimer.singleShot(1400,app.quit)
def expanded():
 root.setProperty('settingsExpanded',True);root.setProperty('keyboardExpanded',True)
 capture(280,1800,'panel-expanded-280.png')
 QTimer.singleShot(120,lambda:capture(360,1600,'panel-expanded-360.png'))
def capture(width,height,name):
 window.resize(width,height);root.setWidth(width);root.setHeight(height)
 QTimer.singleShot(30,lambda:save_capture(name))
def save_capture(name):
 image=window.grabWindow()
 if image.isNull():
  print("Screenshot unavailable: "+name);return
 if not image.save(str(HERE/name)):raise RuntimeError("Screenshot write failed: "+name)
QTimer.singleShot(500,checks)
sys.exit(app.exec_())
