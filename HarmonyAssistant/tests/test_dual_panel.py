"""Shared QML detail surface; one observer and one analysis state across both views."""
from pathlib import Path
base=Path(__file__).resolve().parent
script=(base/'test_modern_panel.py').read_text(encoding='utf-8')
add=r'''
script=script.replace('    function fixture()',r"""
    property bool detailPanelVisible:false
    property var detailPanelHost:fixtureDetails.contentItem
    signal panelDetailClosed()
    Window {id:fixtureDetails; objectName:"fixtureDetails"; width:360; height:740; visible:root.detailPanelVisible}
    function showDetailPanel(show){detailPanelVisible=show}
    function fixture()""")
script=script.replace(' QTimer.singleShot(1400,app.quit)',' QTimer.singleShot(1500,dual_begin)')
extra=r"""
import traceback
def qt_failure(kind,value,trace):
 traceback.print_exception(kind,value,trace)
 app.exit(1)
sys.excepthook=qt_failure

def invoke(method):
 QMetaObject.invokeMethod(root,method)

def dual_begin():
 window.resize(1100,150);root.setWidth(1100);root.setHeight(150)
 invoke('syncDetailPanel')
 QTimer.singleShot(80,dual_check)

def dual_check():
 assert root.property('dualDetailActive')
 assert root.property('detailPanelVisible')
 summary=root.findChild(QQuickItem,'harmonySummary')
 details=next((w for w in QGuiApplication.allWindows() if w.objectName()=='fixtureDetails'),None)
 assert details is not None,'detail test window missing'
 assert summary.window() is details
 assert root.findChild(QQuickItem,'harmonyRibbonGroup').window() is window
 assert len(root.findChildren(QObject,'harmonyConfiguration'))==1
 assert root.property('currentNotes').toVariant()
 image=details.grabWindow();assert not image.isNull();image.save(str(HERE/'panel-dual-details.png'))
 image=window.grabWindow();assert not image.isNull();image.save(str(HERE/'panel-dual-ribbon.png'))
 window.resize(740,150);root.setWidth(740);root.setHeight(150)
 QTimer.singleShot(50,dual_narrow)

def dual_narrow():
 group=root.findChild(QQuickItem,'harmonyRibbonGroup')
 assert group.x()>100,'narrow summary should remain centered'
 assert group.x()+group.width()<root.width()-124,'summary overlaps controls'
 image=window.grabWindow();assert not image.isNull();image.save(str(HERE/'panel-dual-ribbon-narrow.png'))
 invoke('toggleDetailPanel')
 QTimer.singleShot(50,dual_hidden)

def dual_hidden():
 assert not root.property('dualDetailActive')
 assert not root.property('detailPanelVisible')
 invoke('toggleDetailPanel')
 QTimer.singleShot(50,dual_restored)

def dual_restored():
 assert root.property('dualDetailActive')
 invoke('panelDetailClosed')
 assert not root.property('configuration').property('dualPanel').toBool()
 window.resize(360,1100);root.setWidth(360);root.setHeight(1100)
 invoke('syncDetailPanel')
 QTimer.singleShot(50,dual_sidebar)

def dual_sidebar():
 assert not root.property('ribbon')
 assert not root.property('detailPanelVisible')
 assert root.findChild(QQuickItem,'harmonySummary').window() is window
 print('Shared detail surface: top/side simultaneous, toggle, close and redock passed')
 app.quit()
"""
script=script.replace('QTimer.singleShot(500,checks)',extra+chr(10)+'QTimer.singleShot(500,checks)')
script=script.replace('from PyQt5.QtCore import QUrl,QMetaObject,QTimer','from PyQt5.QtCore import QUrl,QMetaObject,QTimer,QObject')
script=script.replace('from PyQt5.QtQuick import QQuickWindow','from PyQt5.QtQuick import QQuickWindow,QQuickItem')
'''
script=script.replace('# Keep the original test path',add+chr(10)+'# Keep the original test path')
exec(compile(script,str(base/'test_modern_panel.py'),'exec'))
