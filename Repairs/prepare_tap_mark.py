# coding: utf-8
"""Capture and extend the reviewed Tap module and small native entry points."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def mirror(path,old,new):
    src=HOST/path
    dst=ROOT/'native'/path
    text=dst.read_text(encoding='utf8') if dst.exists() else src.read_text(encoding='utf8')
    if new in text:return
    assert text.count(old)==1,(path,old,text.count(old))
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(text.replace(old,new).encode('utf8'))
mirror('mscore/taptempo/taptempo.h','class QWidget;','class QWidget;\nnamespace Ms { class Element; }')
mirror('mscore/taptempo/taptempo.h','      QWidget* createButton(QWidget* parent, QAction* action);','      QWidget* createButton(QWidget* parent, QAction* action);\n      QWidget* createTapControl(QWidget* parent);\n   signals:\n      void tapRecorded(qint64 monotonicMs);\n   public:')
mirror('mscore/taptempo/taptempo.cpp','void TapTempo::tap() {','QWidget* TapTempo::createTapControl(QWidget* parent) {\n      auto button = new TapButton(parent); button->setDefaultAction(getAction("tap-tempo"));\n      button->setText(tr("Tap · 点击一拍")); button->setToolButtonStyle(Qt::ToolButtonTextBesideIcon); return button;\n      }\nvoid TapTempo::tap() {\n      emit tapRecorded(_clock.elapsed());')
mirror('mscore/taptempo/taptempo.cpp','button->setDefaultAction(action); button->setToolButtonStyle(Qt::ToolButtonTextOnly);','button->setDefaultAction(action); button->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);')
mirror('mscore/taptempo/taptempo.cpp','horizontalAdvance("TAP · 9999")+32','horizontalAdvance("TAP · 9999")+54')
mirror('mscore/shortcut.cpp','QT_TRANSLATE_NOOP("action","Estimate tempo without changing the score")','QT_TRANSLATE_NOOP("action","Estimate tempo without changing the score"),\n         Icons::countin_ICON')
mirror('mscore/scoreview.cpp','#include "scoreview.h"','#include "scoreview.h"\n#include "taptempo/tapmark.h"')
mirror('mscore/scoreview.cpp','      createElementPropertyMenu(obj, popup);','      createElementPropertyMenu(obj, popup);\n      if (obj->isTempoText() || (obj->isTextLine() && static_cast<TextLine*>(obj)->ritEnabled())\n          || (obj->isTextLineSegment() && static_cast<TextLine*>(obj->propertyDelegate(Pid::RIT_PLAY))->ritEnabled()))\n            popup->addAction(tr("用 Tap 设置速度…"))->setData("tap-mark");')
mirror('mscore/scoreview.cpp','''      const QByteArray& cmd(a->data().toByteArray());
      if (cmd == "cut"''','''      const QByteArray& cmd(a->data().toByteArray());
      if (cmd == "tap-mark") { showTapMarkDialog(obj); return; }
      if (cmd == "cut"''')
mirror('mscore/inspector/inspector.cpp','#include "scrubproperty.h"','#include "scrubproperty.h"\n#include "../taptempo/tapmark.h"')
mirror('mscore/inspector/inspector.cpp','      tt.setupUi(addWidget());','      tt.setupUi(addWidget());\n      auto tap = new QPushButton(tr("用 Tap 设置速度…"), tt.panel); tap->setObjectName("tempoTapMark");\n      auto tapGrid = qobject_cast<QGridLayout*>(tt.panel->layout());\n      tapGrid->addWidget(tap, tapGrid->rowCount(), 0, 1, 3);\n      connect(tap, &QPushButton::clicked, this, [this] { showTapMarkDialog(inspector->element()); });')
mirror('mscore/inspector/inspectorTextLine.cpp','#include <QPushButton>','#include <QPushButton>\n#include "../taptempo/tapmark.h"')
mirror('mscore/inspector/inspectorTextLine.cpp','      mapSignals(il, ppList);','      auto tap = new QPushButton(tr("用 Tap 设置起速／终速…"), ttl.panel); tap->setObjectName("ritTapMark");\n      grid->addWidget(tap, grid->rowCount(), 0, 1, 3);\n      connect(tap, &QPushButton::clicked, this, [this] { showTapMarkDialog(inspector->element()); });\n      mapSignals(il, ppList);')
mirror('mscore/inspector/inspectorTextLine.cpp','      findChild<QCheckBox*>("ritPlay")->setEnabled','      findChild<QPushButton*>("ritTapMark")->setEnabled(line->ritEnabled());\n      findChild<QCheckBox*>("ritPlay")->setEnabled')
mirror('mscore/performanceeditor/parameteredit.cpp','#include "parameteredit.h"','#include "parameteredit.h"\n#include "../taptempo/tapmark.h"')
start='''                  QString text = point.text->xmlText();'''
src=HOST/'mscore/performanceeditor/parameteredit.cpp';dst=ROOT/'native/mscore/performanceeditor/parameteredit.cpp'
s=dst.read_text(encoding='utf8') if dst.exists() else src.read_text(encoding='utf8')
begin=s.index(start);end=s.index('                  point.text->undoSetTempo',begin)
s=s[:begin]+'''                  const QString text = tapTempoText(point.text->xmlText(), point.bpm, visibleNew);
                  static_cast<Element*>(point.text)->undoChangeProperty(Pid::TEXT, text);
'''+s[end:]
dst.write_bytes(s.encode('utf8'))
