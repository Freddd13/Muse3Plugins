"""Hand mark presets and separately editable expression-sized hand text."""
from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def edit(path,changes):
 p=H/path;s=p.read_text(encoding='utf8')
 for a,b in changes:
  assert s.count(a)==1,(path,a[:85],s.count(a));s=s.replace(a,b)
 q=R/'native'/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(s.encode())
edit('libmscore/handbracket.cpp',[
 ('Style styles[4]={{.75,-1.8,.12,false},{-.75,-1.8,.12,false},{.75,-1.8,.12,false},{-.75,-1.8,.12,false}};','Style styles[4]={{.6,-2.5,.12,false},{-.6,-2.5,.12,false},{.6,-2.5,.12,false},{-.6,-2.5,.12,false}};'),
 ('if(symbol->getProperty(Pid::HAND_BRACKET_TEXT).toBool()){','if(symbol->getProperty(Pid::HAND_BRACKET_TEXT).toBool()&&symbol->getProperty(Pid::HAND_TEXT_AUTO).toBool()){'),
 ('const double x=h>=0?head.left()-h-gap*sp:head.right()-h+gap*sp;','const double x=symbol->handEnd()?head.right()+std::abs(h)+gap*sp:head.left()-std::abs(h)-gap*sp;'),
 ('baseAt(.28,0)','baseAt(.15,0)'),
 ('for(double gap:{.28,.45,.7,1.,1.4})','for(double gap:{.15,.25,.4,.6,.9})')])
edit('libmscore/symbol.h',[
 ('      QPointF _handDragOffset;','      QPointF _handDragOffset;\n      QPointF _handTextOffset,_handTextDragOriginal;\n      QString _handTextFont;\n      qreal _handTextSize=0;\n      bool _handTextAuto=true;'),
 ('return handBracket() ? 3 : 0;','return handBracket() ? (_handText?4:3) : 0;')])
edit('libmscore/symbol.cpp',[
 ('#include "symbol.h"','#include "symbol.h"\n#include "text.h"'),
 ('      _handText = s._handText;','      _handText = s._handText;\n      _handTextOffset=s._handTextOffset;_handTextFont=s._handTextFont;_handTextSize=s._handTextSize;_handTextAuto=s._handTextAuto;'),
 ('      QFont font("FreeSerif"); font.setItalic(true); font.setPixelSize(qMax(1,qRound(.9 * spatium() * mag())));','      Text expression(score(),Tid::EXPRESSION);QFont font=expression.font();\n      if(!_handTextFont.isEmpty())font.setFamily(_handTextFont);\n      if(_handTextSize>0)font.setPointSizeF(_handTextSize);\n      if(font.pointSizeF()>0)font.setPointSizeF(font.pointSizeF()*mag());'),
 ('      return QPointF(x,y);','      return QPointF(x,y)+_handTextOffset*unit;'),
 ('      if (_handText) result.add(handTextRect());','      if (_handText && _handTextAuto) result.add(handTextRect());'),
 ('      return {pagePos()+QPointF(_handH*unit,handLeft() ? _handV*unit : 0),','      std::vector<QPointF> result {pagePos()+QPointF(_handH*unit,handLeft() ? _handV*unit : 0),'),
 ('            pagePos()+QPointF(0,handLeft() ? _handV*unit : 0)};','            pagePos()+QPointF(0,handLeft() ? _handV*unit : 0)};\n      if(_handText)result.push_back(pagePos()+handTextRect().center());return result;'),
 ('      if (handBracket() && int(ed.curGrip)>=0 && int(ed.curGrip)<3) {\n            auto data=ed.getData(this);','      if (handBracket() && int(ed.curGrip)>=0 && int(ed.curGrip)<gripsCount()) {\n            if(int(ed.curGrip)==3){auto data=ed.getData(this);data->pushProperty(Pid::HAND_TEXT_OFFSET);data->pushProperty(Pid::HAND_TEXT_AUTO);_handTextDragOriginal=_handTextOffset;_handDragging=true;return;}\n            auto data=ed.getData(this);'),
 ('      if (!handBracket() || int(ed.curGrip)<0 || int(ed.curGrip)>=3)','      if (!handBracket() || int(ed.curGrip)<0 || int(ed.curGrip)>=gripsCount())'),
 ('      if (int(ed.curGrip)==2) setOffset(offset()+ed.delta);','      if(int(ed.curGrip)==3){setProperty(Pid::HAND_TEXT_OFFSET,_handTextOffset+ed.delta/unit);setProperty(Pid::HAND_TEXT_AUTO,false);}\n      else if (int(ed.curGrip)==2) setOffset(offset()+ed.delta);'),
 ('      if (handBracket() && int(ed.curGrip)>=0 && int(ed.curGrip)<3) {\n            if (ed.key','      if (handBracket() && int(ed.curGrip)>=0 && int(ed.curGrip)<gripsCount()) {\n            if(int(ed.curGrip)==3){if(ed.key==Qt::Key_Escape&&_handDragging){setProperty(Pid::HAND_TEXT_OFFSET,_handTextDragOriginal);_handDragging=false;layout();return true;}if(ed.key==Qt::Key_Home){undoChangeProperty(Pid::HAND_TEXT_OFFSET,QPointF());undoChangeProperty(Pid::HAND_TEXT_AUTO,true);return true;}}\n            if (ed.key'),
 ('Pid::HAND_BRACKET_WIDTH,Pid::HAND_BRACKET_TEXT})','Pid::HAND_BRACKET_WIDTH,Pid::HAND_BRACKET_TEXT,Pid::HAND_TEXT_OFFSET,Pid::HAND_TEXT_FONT,Pid::HAND_TEXT_SIZE,Pid::HAND_TEXT_AUTO})'),
 ('            else if (tag == propertyName(Pid::HAND_BRACKET_TEXT)) readProperty(e,Pid::HAND_BRACKET_TEXT);','            else if (tag == propertyName(Pid::HAND_BRACKET_TEXT)) readProperty(e,Pid::HAND_BRACKET_TEXT);\n            else if (tag == propertyName(Pid::HAND_TEXT_OFFSET)) readProperty(e,Pid::HAND_TEXT_OFFSET);\n            else if (tag == propertyName(Pid::HAND_TEXT_FONT)) readProperty(e,Pid::HAND_TEXT_FONT);\n            else if (tag == propertyName(Pid::HAND_TEXT_SIZE)) readProperty(e,Pid::HAND_TEXT_SIZE);\n            else if (tag == propertyName(Pid::HAND_TEXT_AUTO)) readProperty(e,Pid::HAND_TEXT_AUTO);'),
 ('            case Pid::HAND_BRACKET_TEXT: return _handText;','            case Pid::HAND_BRACKET_TEXT: return _handText;\n            case Pid::HAND_TEXT_OFFSET:return _handTextOffset;\n            case Pid::HAND_TEXT_FONT:return _handTextFont;\n            case Pid::HAND_TEXT_SIZE:return _handTextSize;\n            case Pid::HAND_TEXT_AUTO:return _handTextAuto;'),
 ('            case Pid::HAND_BRACKET_TEXT: _handText=value.toBool();break;','            case Pid::HAND_BRACKET_TEXT: _handText=value.toBool();break;\n            case Pid::HAND_TEXT_OFFSET: {auto p=value.toPointF();if(!std::isfinite(p.x())||!std::isfinite(p.y())||std::abs(p.x())>100||std::abs(p.y())>100)return false;_handTextOffset=p;break;}\n            case Pid::HAND_TEXT_FONT:_handTextFont=value.toString().left(128);break;\n            case Pid::HAND_TEXT_SIZE:if(!std::isfinite(number)||number<0||number>96)return false;_handTextSize=number;break;\n            case Pid::HAND_TEXT_AUTO:_handTextAuto=value.toBool();break;'),
 ('            case Pid::HAND_BRACKET_TEXT: return false;','            case Pid::HAND_BRACKET_TEXT: return false;\n            case Pid::HAND_TEXT_OFFSET:return QPointF();\n            case Pid::HAND_TEXT_FONT:return QString();\n            case Pid::HAND_TEXT_SIZE:return 0.;\n            case Pid::HAND_TEXT_AUTO:return true;')])
edit('mscore/handbracketsettings.h',[
 ('namespace Ms {class Inspector;class PalettePanel;','namespace Ms {class Inspector;class PalettePanel;class Symbol;'),
 ('void completeHandBracketPalette(PalettePanel*);','void completeHandBracketPalette(PalettePanel*);\nvoid addHandTextControls(QWidget*,QGridLayout*,Inspector*);\nvoid syncHandTextControls(QWidget*,Symbol*);')])
edit('mscore/handbracketsettings.cpp',[
 ('#include <QGridLayout>','#include <QGridLayout>\n#include <QFontComboBox>\n#include <QDoubleSpinBox>\n#include <QCheckBox>\n#include <QSignalBlocker>\n#include "libmscore/text.h"'),
 ('            if(!HandBracket::setDefaults(symbol->sym(),style))return;\n            QSettings settings;const auto key=styleKey(symbol->sym());settings.setValue(key+"horizontal",style.horizontal);settings.setValue(key+"vertical",style.vertical);settings.setValue(key+"width",style.width);settings.setValue(key+"text",style.text);settings.sync();\n            if(settings.status()==QSettings::NoError)refreshHandPaletteDefaults(symbol->sym());','''            QSettings settings;
            for(auto id:{SymId::keyboardPlayWithLH,SymId::keyboardPlayWithLHEnd,SymId::keyboardPlayWithRH,SymId::keyboardPlayWithRHEnd}){
                  auto mirrored=style;mirrored.horizontal=(id==SymId::keyboardPlayWithLHEnd||id==SymId::keyboardPlayWithRHEnd?-1:1)*std::abs(style.horizontal);
                  if(!HandBracket::setDefaults(id,mirrored))return;const auto key=styleKey(id);settings.setValue(key+"horizontal",mirrored.horizontal);settings.setValue(key+"vertical",mirrored.vertical);settings.setValue(key+"width",mirrored.width);settings.setValue(key+"text",mirrored.text);refreshHandPaletteDefaults(id);
                  }settings.sync();'''),
 ('已保存。以后添加的同方向分手记号使用此形状。','已保存四种方向的默认长度，开始与结束互为镜像。')])
p=R/'native/mscore/handbracketsettings.cpp';s=p.read_text(encoding='utf8');pos=s.rfind('\n}')
s=s[:pos]+'''
void addHandTextControls(QWidget* host,QGridLayout* grid,Inspector* inspector){
 auto box=new QWidget(host);auto layout=new QGridLayout(box);layout->setContentsMargins(0,0,0,0);grid->addWidget(box,8,0,1,3);
 auto face=new QFontComboBox(box);face->setObjectName("handTextFont");layout->addWidget(new QLabel(QObject::tr("手部文字字体"),box),0,0);layout->addWidget(face,0,1);
 auto size=new QDoubleSpinBox(box);size->setObjectName("handTextSize");size->setRange(0,96);size->setSpecialValueText(QObject::tr("跟随表情文字"));size->setSuffix(" pt");size->setKeyboardTracking(false);layout->addWidget(new QLabel(QObject::tr("文字大小"),box),1,0);layout->addWidget(size,1,1);
 auto automatic=new QCheckBox(QObject::tr("手部文字自动放置"),box);automatic->setObjectName("handTextAuto");layout->addWidget(automatic,2,0,1,2);
 auto reset=new QPushButton(QObject::tr("跟随表情文字样式"),box);layout->addWidget(reset,3,0,1,2);
 auto change=[inspector](Pid id,QVariant value){for(auto e:*inspector->el())if(e->isSymbol()&&toSymbol(e)->handEligible())mscore->performanceEditor()->queueProperty(e,id,value);};
 QObject::connect(face,&QFontComboBox::currentFontChanged,box,[change](const QFont& f){change(Pid::HAND_TEXT_FONT,f.family());});
 QObject::connect(size,QOverload<double>::of(&QDoubleSpinBox::valueChanged),box,[change](double v){change(Pid::HAND_TEXT_SIZE,v);});
 QObject::connect(automatic,&QCheckBox::clicked,box,[change](bool v){change(Pid::HAND_TEXT_AUTO,v);});
 QObject::connect(reset,&QPushButton::clicked,box,[change]{change(Pid::HAND_TEXT_FONT,QString());change(Pid::HAND_TEXT_SIZE,0.);});
}
void syncHandTextControls(QWidget* host,Symbol* symbol){
 if(auto face=host->findChild<QFontComboBox*>("handTextFont")){QSignalBlocker block(face);QString family=symbol->getProperty(Pid::HAND_TEXT_FONT).toString();if(family.isEmpty()){Text expression(symbol->score(),Tid::EXPRESSION);family=expression.font().family();}face->setCurrentFont(QFont(family));}
 if(auto size=host->findChild<QDoubleSpinBox*>("handTextSize")){QSignalBlocker block(size);size->setValue(symbol->getProperty(Pid::HAND_TEXT_SIZE).toDouble());}
 if(auto automatic=host->findChild<QCheckBox*>("handTextAuto")){QSignalBlocker block(automatic);automatic->setChecked(symbol->getProperty(Pid::HAND_TEXT_AUTO).toBool());}
}
'''+s[pos:];p.write_bytes(s.encode())
edit('mscore/inspector/inspector.cpp',[
 ('      addHandBracketDefaultControls(host,grid,inspector);','      addHandBracketDefaultControls(host,grid,inspector);\n      addHandTextControls(host,grid,inspector);'),
 ('void InspectorHandSymbol::postInit()\n      {','void InspectorHandSymbol::postInit()\n      {\n      if(inspector->element()->isSymbol()&&!mscore->performanceEditor()->hasPending())syncHandTextControls(this,toSymbol(inspector->element()));')])
print('0.54 hand sources staged')
