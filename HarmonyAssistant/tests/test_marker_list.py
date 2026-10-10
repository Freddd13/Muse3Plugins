"""Overflow remains visible and interactive outside the constrained score area."""
import os,sys
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software';os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QPoint,QPointF,Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow,QQuickItem
from PyQt5.QtTest import QTest
base=Path(__file__).resolve().parent.parent
app=QGuiApplication(sys.argv);engine=QQmlApplicationEngine()
engine.loadData(b'''import QtQuick 2.9
MarkerList {
    width:360;height:420;tick:540
    regions:[{start:0,end:480,part:0,chord:"G",degree:"I",bar:1,source:"auto"},
             {start:480,end:960,part:0,chord:"D/F#",degree:"V",bar:2,source:"manual"}]
    unplaced:({"0:480":true})
    property int selectedTick:-1
    property int selectedPart:-1
    onActivated:{selectedTick=tick;selectedPart=part}
}''',QUrl.fromLocalFile(str(base/'marker-list-fixture.qml')))
assert engine.rootObjects()
root=engine.rootObjects()[0];window=QQuickWindow();window.resize(360,420);root.setParentItem(window.contentItem());window.show();QTest.qWait(120)
assert root.findChild(QQuickItem,'harmonyMarkerList').property('count')==2
def blocked(item):
    if item.property('blocked') is True:return item
    for child in item.childItems():
        found=blocked(child)
        if found:return found
row=blocked(root);assert row and row.property('current'),'unplaced result remains visible and selected'
point=row.mapToItem(window.contentItem(),QPointF(row.width()/2,row.height()/2))
QTest.mouseClick(window,Qt.LeftButton,Qt.NoModifier,QPoint(round(point.x()),round(point.y())))
assert root.property('selectedTick')==480 and root.property('selectedPart')==0,'click activation'
assert window.grabWindow().save(str(base/'tests/markers-overflow.png'))
window.close()
print('Overflow list: all results, current range and pointer activation passed')
