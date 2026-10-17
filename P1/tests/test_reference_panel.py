import os,sys,json
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software';os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QMetaObject,QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtTest import QTest
import traceback
rootdir=Path(__file__).resolve().parents[2];out=rootdir/'P1/out/reference';out.mkdir(parents=True,exist_ok=True)
app=QGuiApplication(sys.argv);app.setOrganizationName("Kumo");app.setOrganizationDomain("kumo.local");engine=QQmlApplicationEngine();warnings=[]
engine.addImportPath(str(rootdir/'HarmonyAssistant/tests/qml'))
engine.warnings.connect(lambda ws:warnings.extend(w.toString() for w in ws))
source=(rootdir/'ReferencePlayer/ReferencePlayer.view.qml').read_text(encoding='utf8')
fixture=r"""
 property bool panelFloating:false
 property int panelDockArea:Qt.BottomDockWidgetArea
 function releaseReferenceMedia(media){}
 function newScoreObserver(){return mockObserver}
 function newReferenceMedia(){return mockMedia}
 function fixtureStart(){root.curScore=mockScore;root.run();mockMedia.open("file:///E:/piano.wav")}
 function fixtureSave(){root.associate();root.saveProject("file:///E:/reference.json");root.associations=[];root.loadProject("file:///E:/reference.json")}
 function fixtureAnchor(){mockObserver.tick=960;mockMedia.position=1200;root.addAnchor()}
 QtObject {
  id:mockScore
  property string scoreName:"Piano";property int nmeasures:8;property int nstaves:2
  property var selection:({select:function(e){}})
  function newCursor(){return {track:0,element:{},rewindToTick:function(v){}}}
 }
 QtObject {
  id:mockObserver
  property var score:null;property bool playing:false;property int tick:0
  property string saved:""
  property var documents:({})
  function referenceStructureKey(){return "fixture"}
  function workflowData(section){return documents[section]||({})}
  function setWorkflowData(section,data){documents[section]=data;return {ok:true}}
  function referenceFileLocation(path,relative){return {path:path,relative:relative||path,exists:true}}
  function expressionSelection(){return {notes:[{tick:tick}],scope:analysisScope(false)}}
  function analysisScope(whole){return {start:0,end:1920,firstTrack:0,endTrack:8,firstMeasure:1,lastMeasure:1}}
  function loadConfiguration(name){return {}}
  function saveConfiguration(name,v){return true}
  function readTextFile(url){return saved}
  function writeTextFile(url,text){saved=text;return true}
 }
 QtObject {
  id:mockMedia
  property bool available:true;property bool playing:false
  property string path:"";property string status:"Ready"
  property real duration:0;property real position:0;property real speed:1;property real volume:.8
  property var waveform:[]
  signal fileReady(var info)

  function open(url){path="E:/piano.wav";duration=6000;position=0;waveform=[.1,.2,.3,.4,.7,.5,.2,.4];fileReady({path:path,size:100,modified:5,duration:6000});waveformChanged()}
  function setLoop(a,b,enabled,fade){}
  function identity(){return {path:path,size:100,modified:5,duration:6000}}
  function play(){playing=true}
  function pause(){playing=false}
  function seek(v){position=v}
 }
"""
source=source.rsplit('}',1)[0]+fixture+'}\n'
engine.loadData(source.encode(),QUrl.fromLocalFile(str(rootdir/'ReferencePlayer/ReferencePlayer_MS3.qml')))
if not engine.rootObjects():print('\n'.join(warnings));sys.exit(1)
root=engine.rootObjects()[0];window=QQuickWindow();root.setParentItem(window.contentItem());window.show()
def capture(name,w,h):
 root.setProperty("panelDockArea",1 if h<170 else 8)
 window.resize(w,h);root.setWidth(w);root.setHeight(h)
 app.processEvents();QTest.qWait(150)
 image=window.grabWindow();assert not image.isNull();assert image.save(str(out/name))
def checks():
 try:
  QMetaObject.invokeMethod(root,'fixtureStart');app.processEvents()
  assert root.property('usable')
  capture('bottom.png',840,275);capture('sidebar.png',370,650);capture('top.png',840,90)
  root.setHeight(650)
  QMetaObject.invokeMethod(root,'fixtureSave')
  assert len(root.property('associations').toVariant())==1
  QMetaObject.invokeMethod(root,'fixtureAnchor')
  assert len(root.property('associations').toVariant()[0]['anchors'])==1
  bad=[w for w in warnings if any(x in w for x in ('ReferenceError','TypeError','binding loop','Cannot','is not a type','non-existent'))]
  assert not bad,bad
  (out/'report.json').write_text(json.dumps({'ok':True,'warnings':warnings},ensure_ascii=False,indent=2),encoding='utf8')
  print('Reference panel layout/project/anchor mock regression passed.');app.exit(0)
 except Exception as e:traceback.print_exc();print(repr(e));print('\n'.join(warnings));app.exit(1)
QTimer.singleShot(250,checks)
sys.exit(app.exec_())
