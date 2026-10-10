import os,sys,json
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software'
os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QTimer,QMetaObject
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
base=Path(__file__).resolve().parents[1]
out=base/'tests/out';out.mkdir(exist_ok=True)
app=QGuiApplication(sys.argv)
app.setOrganizationName("ArrangementTests");app.setOrganizationDomain("tests.local");app.setApplicationName("ArrangementPanel")
engine=QQmlApplicationEngine();warnings=[]
engine.warnings.connect(lambda ws:warnings.extend(w.toString() for w in ws))
engine.addImportPath(str(base.parent/'HarmonyAssistant/tests/qml'))
source=(base/'ArrangementAssistant_MS3.qml').read_text(encoding='utf-8')
fixture=r'''
    property int selections:0
    property bool detailPanelVisible:false
    property var detailPanelHost:detailHost
    function showDetailPanel(value) {detailPanelVisible=value;detailWindow.visible=value}
    function newScoreObserver(){return fixtureObserver}
    function focusPanel(){}
    function fixtureStart() {root.curScore=fixtureScore;root.run();root.start(false)}
    function fixtureDirty(){root.markDirty()}
    function fixtureTop(){root.width=1000;root.height=76;root.syncDetail()}
    function fixtureSettings(){settings.open()}
    function fixtureRole(){roleDialog.open()}
    function fixturePlaying(value){fixtureObserver.playing=value;fixtureObserver.positionChanged()}
    QtObject {
        id:fixtureScore
        property var selection:({select:function(note){root.selections++}})
        function newCursor(){return {track:0,element:{notes:[{}]},rewindToTick:function(tick){}}}
    }
    QtObject {
        id:fixtureObserver
        property var score:null
        property bool playing:false
        property bool surfaceVisible:true
        property int tick:0
        signal positionChanged()
        function analysisRevision(){return '1:1'}
        function analysisScope(whole){return {start:0,end:1920,firstTrack:0,endTrack:8,firstMeasure:1,lastMeasure:1,piano:true,part:'Piano',noncontiguous:false}}
        function loadConfiguration(name){return {}}
        function saveConfiguration(name,value){return true}
        function analysisRange(start,end,first,last,next,limit,revision){
            return {revision:revision,done:true,nextTick:end,notes:[
                {tick:0,attackTick:0,end:480,logicalEnd:480,track:0,index:0,pitch:60,tpc:14,id:'a',onSeconds:0,endSeconds:.5,measure:1,beat:1},
                {tick:0,attackTick:0,end:480,logicalEnd:480,track:0,index:1,pitch:79,tpc:15,id:'b',onSeconds:0,endSeconds:.5,measure:1,beat:1},
                {tick:120,attackTick:120,end:480,logicalEnd:480,track:4,index:0,pitch:36,tpc:14,id:'c',onSeconds:.125,endSeconds:.5,measure:1,beat:1.25}
            ],rests:[],meters:[{tick:0,end:1920,measure:1,denominator:4}],harmonies:[],hands:[],pedals:[],parts:[],tempos:[]}
        }
    }
    Window {id:detailWindow;width:370;height:720;visible:false;color:theme.background;Item{id:detailHost;anchors.fill:parent}}
'''
source=source.rsplit('}',1)[0]+fixture+'}\n'
engine.loadData(source.encode('utf-8'),QUrl.fromLocalFile(str(base/'ArrangementAssistant_MS3.qml')))
if not engine.rootObjects():
 print('\n'.join(warnings));sys.exit(1)
root=engine.rootObjects()[0];window=QQuickWindow();root.setParentItem(window.contentItem());window.resize(370,720);root.setWidth(370);root.setHeight(720);window.show()
QMetaObject.invokeMethod(root,'fixtureStart')
tries=0

def capture(name):
 image=window.grabWindow()
 if image.isNull() or not image.save(str(out/name)):raise RuntimeError('Could not capture '+name)

def ready():
 global tries
 tries+=1
 if root.property('running'):
  if tries>100: print('Analysis timeout');app.exit(1);return
  QTimer.singleShot(50,ready);return
 assert root.property('analyzed'),'Analysis not completed'
 assert root.property('issues').toVariant(), 'Expected a span issue'
 capture('right.png')
 QMetaObject.invokeMethod(root,'fixtureSettings')
 QTimer.singleShot(100,settings_capture)

def settings_capture():
 capture('settings.png')
 # Escape closes the popup; hiding/showing also validates its parent lifetime.
 from PyQt5.QtTest import QTest
 from PyQt5.QtCore import Qt
 QTest.keyClick(window,Qt.Key_Escape)
 window.resize(1000,76);QMetaObject.invokeMethod(root,'fixtureTop')
 QTimer.singleShot(150,top_capture)

def top_capture():
 capture('top.png')
 for w in app.allWindows():
  if w!=window and w.isVisible():w.grabWindow().save(str(out/'dual-details.png'))
 QMetaObject.invokeMethod(root,'fixturePlaying',__import__('PyQt5.QtCore',fromlist=['Q_ARG']).Q_ARG('QVariant',True))
 QMetaObject.invokeMethod(root,'fixtureDirty')
 assert root.property('stale')
 assert not root.property('running'),'Analysis must remain cached during playback'
 print(json.dumps({'issues':len(root.property('issues').toVariant()),'worstBatchMs':root.property('worstBatch'),'warnings':warnings},ensure_ascii=True))
 app.exit(1 if [w for w in warnings if "deprecated" not in w] else 0)
QTimer.singleShot(100,ready)
sys.exit(app.exec_())