"""Actual pointer drag verifies snapping and rebinding after a range changes."""
import os,sys
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software'
os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QPoint,QPointF,Qt,QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow,QQuickItem
from PyQt5.QtTest import QTest
def fail(kind,error,trace):
    import traceback
    traceback.print_exception(kind,error,trace)
    sys.stderr.flush();sys.stdout.flush()
    os._exit(1)
sys.excepthook=fail
base=Path(__file__).resolve().parent.parent
app=QGuiApplication(sys.argv);engine=QQmlApplicationEngine()
engine.warnings.connect(lambda errors:print('\n'.join(e.toString() for e in errors)))
engine.loadData(b'''import QtQuick 2.9
RangeEditor {
    width:360;height:680;scoreEnd:1920;tick:240
    region:({id:"0:0",start:0,end:960,part:0,root:0,definition:0,chord:"C"})
    regions:[region];roots:["C"];rootPcs:[0];qualities:["major"]
    property int emittedEnd:-1
    onAction:{emittedEnd=end;region={id:"0:"+start,start:start,end:end,part:0,root:0,definition:0,chord:"C"}}
}''',QUrl.fromLocalFile(str(base/'range-drag-fixture.qml')))
assert engine.rootObjects(),'QML load'
root=engine.rootObjects()[0];window=QQuickWindow();window.resize(360,680)
root.setParentItem(window.contentItem());window.show()
def check():
    root.findChild(QQuickItem,'harmonyRangeEditing').setProperty('checked',True)
    def find(item,name):
        if item.objectName()==name:return item
        for child in item.childItems():
            found=find(child,name)
            if found:return found
    app.processEvents();handle=find(root,'harmonyRangeEnd')
    pos=handle.mapToItem(window.contentItem(),QPointF(handle.width()/2,handle.height()/2))
    first=QPoint(round(pos.x()),round(pos.y()))
    QTest.mousePress(window,Qt.LeftButton,Qt.NoModifier,first)
    QTest.mouseMove(window,first+QPoint(-40,0),30)
    QTest.mouseMove(window,first+QPoint(-70,0),30)
    QTest.mouseRelease(window,Qt.LeftButton,Qt.NoModifier,first+QPoint(-70,0))
    end=root.property('emittedEnd');assert 0<end<960 and end%60==0,('drag action',end)
    app.processEvents();x=handle.x()
    root.setProperty('region',{'id':'0:0','start':0,'end':480,'part':0,'root':0,'definition':0,'chord':'C'})
    app.processEvents();assert handle.x()!=x,'handle must follow changed range'
    print('Range drag/snap/rebinding passed: end',end);app.quit()
QTimer.singleShot(250,check)
sys.exit(app.exec_())
