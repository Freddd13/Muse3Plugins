import os,sys,json
from pathlib import Path
os.environ['QT_QUICK_BACKEND']='software';os.environ['QML_DISABLE_DISK_CACHE']='1'
from PyQt5.QtCore import QUrl,QMetaObject,QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtTest import QTest
import traceback
rootdir=Path(__file__).resolve().parents[2];out=rootdir/'P1/out/expression';out.mkdir(parents=True,exist_ok=True)
app=QGuiApplication(sys.argv);app.setOrganizationName("Kumo");app.setOrganizationDomain("kumo.local");engine=QQmlApplicationEngine();warnings=[]
engine.addImportPath(str(rootdir/'HarmonyAssistant/tests/qml'))
engine.warnings.connect(lambda ws:warnings.extend(w.toString() for w in ws))
source=(rootdir/'PerformanceExpression/PerformanceExpression_MS3.qml').read_text(encoding='utf8')
engine.loadData(source.encode(),QUrl.fromLocalFile(str(rootdir/'PerformanceExpression/PerformanceExpression_MS3.qml')))
if not engine.rootObjects():print('\n'.join(warnings));sys.exit(1)
root=engine.rootObjects()[0];window=QQuickWindow();root.setParentItem(window.contentItem());window.show()
def capture(name,w,h):
 window.resize(w,h);root.setWidth(w);root.setHeight(h);app.processEvents();QTest.qWait(150)
 image=window.grabWindow();assert not image.isNull();assert image.save(str(out/name))
def checks():
 try:
  capture('expression-side.png',440,720);capture('expression-top.png',900,130)
  bad=[w for w in warnings if any(x in w for x in ('ReferenceError','TypeError','binding loop','Cannot','is not a type','non-existent','Unexpected'))]
  assert not bad,bad
  print('Expression QML theme/stable side/top layout parse passed.');app.exit(0)
 except Exception:traceback.print_exc();print('\n'.join(warnings));app.exit(1)
QTimer.singleShot(250,checks)
sys.exit(app.exec_())
