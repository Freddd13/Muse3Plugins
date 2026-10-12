# coding: utf-8
from pathlib import Path
r=Path('Repairs/native/mscore/performanceeditor')
def edit(n,a,b):
 p=r/n;s=p.read_text(encoding='utf8');assert s.count(a)==1,(n,a[:90]);p.write_text(s.replace(a,b),encoding='utf8')
edit('performanceeditor.cpp','      if(!_gestureMoved&&QLineF(_press,point).length()<QApplication::startDragDistance())return;\n      _gestureMoved=true;','      const bool moved=QLineF(_press,point).length()>=QApplication::startDragDistance();\n      if(!_gestureMoved&&!moved&&_offsetDrag)return;\n      _gestureMoved|=moved;')
edit('performanceeditor.cpp','      if (_scoreRangePanning) { _scoreRangePanning = false;','      if(_bandResizing){_bandHeight=_bandResizeHeight;_bandResizing=false;qApp->removeEventFilter(this);if(_view){_view->releaseMouse();_view->unsetCursor();_view->update();}}\n      if (_scoreRangePanning) { _scoreRangePanning = false;')
edit('performanceeditor.cpp','      if (_scoreRangePanning && (event->type()','      if ((_scoreRangePanning||_bandResizing) && (event->type()')
edit('performanceoverlay.cpp','      if (_scoreRangePanning) {','''      if(_bandResizing){
            if(event->type()==QEvent::MouseMove){auto mouse=static_cast<QMouseEvent*>(event);invalidateOverlay();_bandHeight=qBound(48,_bandResizeHeight+mouse->y()-qRound(_press.y()),240);_view->update();return true;}
            if(event->type()==QEvent::MouseButtonRelease){_bandResizing=false;QSettings().setValue("performanceEditor/bandHeight",_bandHeight);qApp->removeEventFilter(this);_view->releaseMouse();_view->unsetCursor();return true;}
            }
      if (_scoreRangePanning) {''')
edit('performanceoverlay.cpp','            if (mouse->button() == Qt::LeftButton) {','''            if (mouse->button() == Qt::LeftButton) {
                  if(QRectF(_scoreFrame.left(),_scoreFrame.bottom()-5,_scoreFrame.width(),8).contains(mouse->pos())){finishWheel();cancelGesture();_bandResizing=true;_bandResizeHeight=_bandHeight;_press=mouse->pos();qApp->installEventFilter(this);_view->setCursor(Qt::SizeVerCursor);_view->grabMouse();return true;}''')
edit('performanceoverlay.cpp','#include <QPainter>','#include <QPainter>\n#include <QSettings>')
edit('performanceeditor.cpp','qBound(48, QSettings().value("performanceEditor/bandHeight", 48).toInt(), 144)','qBound(48, QSettings().value("performanceEditor/bandHeight", 48).toInt(), 240)')
edit('performanceeditor.cpp','tr("当前谱行下方（放不下时回到底部）")','tr("跟随选中／播放谱行下方")')
# Store the voices and the native-colour preference separately; custom palettes survive.
edit('performancesettings.h','      int mode = 0;','      bool followNativeVoices = true;\n      int mode = 0;')
edit('performancesettings.cpp','#include "performancesettings.h"','#include "performancesettings.h"\n#include "libmscore/mscore.h"\n#include <QCheckBox>')
edit('performancesettings.cpp','if (mode == 1) return voices[track % 4];','if (mode == 1) return followNativeVoices ? MScore::selectColor[track % 4] : voices[track % 4];')
edit('performancesettings.cpp','      const bool original = colors == oldColors','      followNativeVoices=settings.value("followNativeVoices",voices==PerformanceAppearance().voices||voices==oldVoices).toBool();\n      const bool original = colors == oldColors')
edit('performancesettings.cpp','      settings.setValue("mode", mode);','      settings.setValue("followNativeVoices", followNativeVoices);\n      settings.setValue("mode", mode);')
edit('performancesettings.cpp','      for (int i = 0; i < 4; ++i) add(QObject::tr("声部 %1").arg(i + 1), draft.voices[i]);','''      auto nativeVoices=new QCheckBox(QObject::tr("声部颜色跟随 MuseScore"));nativeVoices->setChecked(draft.followNativeVoices);grid->addWidget(nativeVoices,grid->rowCount(),0,1,2);
      for (int i = 0; i < 4; ++i) add(QObject::tr("自选声部色 %1").arg(i + 1), draft.voices[i]);''')
edit('performancesettings.cpp','draft.velocityWidth = width->value(); dialog.accept();','draft.velocityWidth = width->value(); draft.followNativeVoices=nativeVoices->isChecked(); dialog.accept();')
edit('performancesettings.cpp','draft = PerformanceAppearance(); width->setValue','draft = PerformanceAppearance(); nativeVoices->setChecked(true); width->setValue')
# The original-value path needs increasing time, not interval index pitch order.
edit('performanceux.cpp','      const auto candidates=onScore?_systemIndices:_intervals.query(from,until);','      auto candidates=onScore?_systemIndices:_intervals.query(from,until);std::sort(candidates.begin(),candidates.end());')
edit('performanceux.cpp','      _viewport.pitchRows.clear();if(_keyboardMode==2)','      const auto old=_viewport.pitchRows;_viewport.pitchRows.clear();if(_keyboardMode==2)')
edit('performanceux.cpp','std::sort(_viewport.pitchRows.begin(),_viewport.pitchRows.end());}\n      }','std::sort(_viewport.pitchRows.begin(),_viewport.pitchRows.end());}\n      if(old!=_viewport.pitchRows)invalidateVisual();\n      }')
edit('performancepainting.cpp','(_viewport.topPitch - _notes[_hover].pitch) * _viewport.rowHeight','_viewport.pitchY(_notes[_hover].pitch)')
# Clear stale per-track choices when moving to another score.
# Strip and number editing use the same effective display scale.
p=r/'performanceeditor.cpp';s=p.read_text(encoding='utf8').replace('力度基准','原力度').replace('建立力度基准','读取原力度');p.write_text(s,encoding='utf8')
print('Held-key display, band resizing and native voice colours prepared.')
