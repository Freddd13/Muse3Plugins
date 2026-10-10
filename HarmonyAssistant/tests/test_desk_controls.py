"""Real pointer/keyboard input in both host palette modes, including popup selection."""
import os,sys
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software';os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QPoint,QPointF,Qt
from PyQt5.QtGui import QGuiApplication,QPalette,QColor
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow,QQuickItem
from PyQt5.QtTest import QTest
base=Path(__file__).resolve().parent.parent
app=QGuiApplication(sys.argv)
def find(item,predicate):
    if predicate(item):return item
    for child in item.childItems():
        found=find(child,predicate)
        if found:return found
def click(window,item):
    point=item.mapToItem(window.contentItem(),QPointF(item.width()/2,item.height()/2))
    QTest.mouseClick(window,Qt.LeftButton,Qt.NoModifier,QPoint(round(point.x()),round(point.y())))
def type_text(window,text):
    for character in text:QTest.keyClick(window,Qt.Key(ord(character.upper())))
for dark in [False,True]:
    palette=QPalette()
    palette.setColor(QPalette.Window,QColor('#30343a' if dark else '#efefef'))
    palette.setColor(QPalette.WindowText,QColor('#eceef0' if dark else '#222222'))
    app.setPalette(palette)
    engine=QQmlApplicationEngine()
    engine.loadData(b'''import QtQuick 2.9
Item {
    width:320;height:260
    property int choice:-1
    property int spinResult:-1
    UiTheme {id:theme}
    Rectangle {anchors.fill:parent;color:theme.background}
    Column {x:12;y:12;width:296;spacing:12
        DeskComboBox {objectName:"choice";width:parent.width;model:["one","two","three"];onActivated:parent.parent.choice=currentIndex}
        DeskSwitch {objectName:"switch";text:"enabled"}
        DeskSpinBox {objectName:"spin";width:parent.width;from:0;to:200;value:15;editable:true;onValueModified:parent.parent.spinResult=value}
        DeskTextField {objectName:"field";width:parent.width;text:"#112233";maximumLength:7}
        DeskButton {text:"settings";checkable:true;checked:true}
    }
}''',QUrl.fromLocalFile(str(base/'desk-control-fixture.qml')))
    assert engine.rootObjects(),'load'
    root=engine.rootObjects()[0];window=QQuickWindow();window.resize(320,260);root.setParentItem(window.contentItem());window.show();QTest.qWait(100)
    control=root.findChild(QQuickItem,'choice');click(window,control);QTest.qWait(80)
    delegate=find(window.contentItem(),lambda item:item.property('text')=='two' and 'Delegate' in item.metaObject().className())
    assert delegate,'popup delegate'
    click(window,delegate);QTest.qWait(50)
    assert root.property('choice')==1 and control.property('currentIndex')==1,'popup selection emits activation'
    control=root.findChild(QQuickItem,'switch');click(window,control);assert control.property('checked'),'toggle'
    control=root.findChild(QQuickItem,'spin');click(window,control)
    QTest.keyClick(window,Qt.Key_A,Qt.ControlModifier);type_text(window,'120');QTest.keyClick(window,Qt.Key_Return);QTest.qWait(40)
    assert control.property('value')==120,('numeric entry',control.property('value'))
    control=root.findChild(QQuickItem,'field');click(window,control)
    QTest.keyClick(window,Qt.Key_A,Qt.ControlModifier);type_text(window,'#aabbcc');QTest.keyClick(window,Qt.Key_Return)
    assert control.property('text')=='#aabbcc','color input'
    assert window.grabWindow().save(str(base/'tests'/('desk-dark.png' if dark else 'desk-light.png')))
    window.close();engine.clearComponentCache()
print('Inspector controls: popup/toggle/numeric/color input passed in light and dark palettes')
