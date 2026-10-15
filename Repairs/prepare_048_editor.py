from pathlib import Path

HOST = Path(r'E:/programming/funcodes/muse3_dev/MuseScore')
ROOT = Path(__file__).resolve().parent
changed = set()

def edit(name, old, new, count=1):
    p = HOST / name
    source = p.read_text(encoding='utf-8')
    assert source.count(old) == count, (name, old[:100], source.count(old))
    p.write_text(source.replace(old, new), encoding='utf-8', newline='\n')
    changed.add(name)

def append(name, code):
    p = HOST / name
    s = p.read_text(encoding='utf-8')
    at = s.rfind('\n}')
    assert at >= 0
    p.write_text(s[:at] + '\n' + code + s[at:], encoding='utf-8', newline='\n')
    changed.add(name)

# A score-space row index survives view zoom and pan. Only layout changes rebuild it.
header = 'mscore/performanceeditor/performanceeditor.h'
edit(header, '      QVector<QPair<int,QRectF>> _visibleScoreNotes;', '''      struct ScoreNoteRow { QRectF bounds; QVector<int> indices; };
      QVector<ScoreNoteRow> _scoreNoteRows;
      void rebuildScoreNoteRows();
      QVector<QPair<int,QRectF>> _visibleScoreNotes;''')
edit(header, '      bool _relativeActual = false;', '''      bool _relativeActual = false;
      int _velocityArrangement = 0;
      bool _groupRelative = true;
      QSet<int> _collapsedVelocityStaves;
      QVector<int> _velocityStaves;
      QRectF velocityLane(int, const QRectF&, bool) const;
      double velocityY(int, const QRectF&, bool) const;
      bool velocityHeaderClick(QPointF);
      void paintVelocityHeaders(QPainter&, const QRectF&);''')
edit(header, '      QTimer _playTimer, _moveTimer, _wheelTimer;', '''      QTimer _playTimer, _moveTimer, _wheelTimer, _wheelFeedbackTimer;
      QPointer<QWidget> _wheelFeedbackSurface;
      QPointF _wheelFeedbackPoint;
      QRectF _wheelFeedbackHead;
      QString _wheelFeedbackName, _wheelFeedbackValue;
      QColor _wheelFeedbackColor;
      int _wheelFeedbackTicks = 0;
      void rememberWheelFeedback();''')
edit(header, '      bool adjustNearestScoreVelocity(ScoreView*, QWheelEvent*);', '''      static bool nearestWheelShortcut(const QWheelEvent*);
      bool adjustNearestScoreVelocity(ScoreView*, QWheelEvent*);''')

editor = 'mscore/performanceeditor/performanceeditor.cpp'
edit(editor, '      rebuildFilter(); invalidateVisual();', '      rebuildScoreNoteRows(); rebuildFilter(); invalidateVisual();')
edit(editor, '      _geometryDirty = false; invalidateVisual();', '      _geometryDirty = false; rebuildScoreNoteRows(); invalidateVisual();')
edit(editor, '&& !_view->editMode() && !_view->noteEntryMode();', '&& !_view->editMode() && (!_view->noteEntryMode() || _closestWheelActive || _wheelIndex >= 0 || _wheelFeedbackTimer.isActive());')
edit(editor, '_showValues||_closestWheelActive||(_wheelIndex>=0&&_wheelSurface==_view)', '_showValues||_closestWheelActive||(_wheelIndex>=0&&_wheelSurface==_view)||(_wheelFeedbackTimer.isActive()&&_wheelFeedbackSurface==_view)')
old='onScore&&event->type()==QEvent::Wheel&&(static_cast<QWheelEvent*>(event)->modifiers()&(Qt::AltModifier|Qt::ShiftModifier))==(Qt::AltModifier|Qt::ShiftModifier)'
edit(editor, old, 'onScore&&event->type()==QEvent::Wheel&&nearestWheelShortcut(static_cast<QWheelEvent*>(event))')
edit('mscore/events.cpp', '''      if ((event->modifiers() & (Qt::AltModifier|Qt::ShiftModifier)) == (Qt::AltModifier|Qt::ShiftModifier)
            && !(event->modifiers() & Qt::ControlModifier) && mscore) {''', '''      if (mscore && PerformanceEditor::nearestWheelShortcut(event)) {''')

ux = 'mscore/performanceeditor/performanceux.cpp'
edit(ux, '''      for(int i=0;i<_notes.size();++i){const auto& note=_notes[i];if(!noteEditable(note)||!logicalViewport.intersects(note.bounds))continue;
            QRectF bounds=matrix.mapRect(note.bounds);if(_view->rect().intersects(bounds.toAlignedRect()))_visibleScoreNotes.append({i,bounds});}''', '''      for(const auto& row:_scoreNoteRows) {
            if(!logicalViewport.intersects(row.bounds))continue;
            for(int i:row.indices) {const auto& note=_notes[i];if(!noteEditable(note)||!logicalViewport.intersects(note.bounds))continue;
                  QRectF bounds=matrix.mapRect(note.bounds);if(_view->rect().intersects(bounds.toAlignedRect()))_visibleScoreNotes.append({i,bounds});}
            }''')
append(ux, '''void PerformanceEditor::rebuildScoreNoteRows()
      {
      _scoreNoteRows.clear();_visibleScoreRect=QRect();QHash<System*,int> rows;
      for(int i=0;i<_notes.size();++i){const auto& n=_notes[i];if(n.bounds.isEmpty())continue;
            int row=rows.value(n.system,-1);if(row<0){row=_scoreNoteRows.size();rows.insert(n.system,row);_scoreNoteRows.append({{}, {}});}
            auto& r=_scoreNoteRows[row];r.bounds=r.bounds.united(n.bounds);r.indices.append(i);}
      }
QRectF PerformanceEditor::velocityLane(int index,const QRectF& rect,bool onScore) const
      {
      if(onScore || _velocityArrangement==0 || _parameter->currentIndex()!=0)return rect;
      if(index<0 || index>=_notes.size())return {};
      const int staff=_notes[index].track/VOICES;const int row=_velocityStaves.indexOf(staff);if(row<0)return {};
      int expanded=0;for(int s:_velocityStaves)if(!_collapsedVelocityStaves.contains(s))++expanded;
      const double header=17.,body=qMax(12.,(rect.height()-header*_velocityStaves.size())/qMax(1,expanded));double top=rect.top();
      for(int s:_velocityStaves){const bool closed=_collapsedVelocityStaves.contains(s);if(s==staff)return closed?QRectF():QRectF(rect.left(),top+header,rect.width(),body);top+=header+(closed?0:body);}
      return {};
      }
double PerformanceEditor::velocityY(int index,const QRectF& rect,bool onScore) const
      {const auto lane=velocityLane(index,rect,onScore);return lane.isEmpty()?-1e6:yForValue(noteValue(index),lane,onScore);}
bool PerformanceEditor::velocityHeaderClick(QPointF point)
      {
      if(_parameter->currentIndex()!=0 || !_velocityArrangement)return false;
      const auto rect=laneRect();int expanded=0;for(int s:_velocityStaves)if(!_collapsedVelocityStaves.contains(s))++expanded;
      const double body=qMax(12.,(rect.height()-17*_velocityStaves.size())/qMax(1,expanded));double top=rect.top();
      for(int s:_velocityStaves){if(point.y()>=top&&point.y()<top+17){finishWheel();cancelGesture();if(_collapsedVelocityStaves.contains(s))_collapsedVelocityStaves.remove(s);else _collapsedVelocityStaves.insert(s);invalidateVisual();return true;}top+=17+(_collapsedVelocityStaves.contains(s)?0:body);}
      return false;
      }
void PerformanceEditor::paintVelocityHeaders(QPainter& painter,const QRectF& rect)
      {
      if(_parameter->currentIndex()!=0 || !_velocityArrangement)return;
      int expanded=0;for(int s:_velocityStaves)if(!_collapsedVelocityStaves.contains(s))++expanded;
      const double body=qMax(12.,(rect.height()-17*_velocityStaves.size())/qMax(1,expanded));double top=rect.top();
      for(int s:_velocityStaves){const bool closed=_collapsedVelocityStaves.contains(s);painter.fillRect(QRectF(rect.left(),top,rect.width(),17),_appearance.colors[PerformanceAppearance::NaturalRow]);painter.setPen(_appearance.colors[PerformanceAppearance::Text]);
            painter.drawText(QRectF(rect.left()+4,top,rect.width()-8,17),Qt::AlignVCenter,(closed?QString::fromUtf8("▸ "):QString::fromUtf8("▾ "))+tr("谱表 %1 · 记号力度／谱中力度").arg(s+1));top+=17+(closed?0:body);}
      }
''')

wheel = 'mscore/performanceeditor/performancewheel.cpp'
edit(wheel, '#include <cmath>', '#include <cmath>\n#include <QSettings>\n#include <QPainterPath>')
append(wheel, '''bool PerformanceEditor::nearestWheelShortcut(const QWheelEvent* event)
      {
      const int required=QSettings().value("performanceEditor/nearestWheelModifiers",int(Qt::AltModifier|Qt::ShiftModifier)).toInt();
      return required && (int(event->modifiers())&~int(Qt::KeypadModifier))==required;
      }
void PerformanceEditor::rememberWheelFeedback()
      {
      if(_wheelIndex<0 || _wheelIndex>=_notes.size())return;
      const auto& n=_notes[_wheelIndex];const auto e=_pending.value(n.note,{n.type,n.raw});
      _wheelFeedbackSurface=_wheelSurface;_wheelFeedbackPoint=_wheelPoint;
      _wheelFeedbackHead=_wheelSurface==_view?n.bounds:QRectF();
      _wheelFeedbackColor=MScore::selectColor[n.track%VOICES];
      _wheelFeedbackName=tr("谱表%1 · 声部%2 · %3").arg(n.track/VOICES+1).arg(n.track%VOICES+1).arg(n.name);
      const int value=n.base<0?e.raw:NoteVelocity::effective(n.base,e.type,e.raw);
      _wheelFeedbackValue=tr("力度 %1    %2%3    记号力度 %4").arg(value).arg(n.base>0?NoteVelocity::offsetFor(n.base,value):0).arg("%").arg(n.base<0?tr("读取中"):QString::number(n.base));
      }
''')
edit(wheel, '      if(view!=_view)setView(view);', '''      if(!nearestWheelShortcut(event))return false;
      if(view!=_view)setView(view);''')
edit(wheel, '      if (_dirty) refresh();', '      if (_dirty || _geometryDirty) refresh();')
edit(wheel, 'const bool closest=onScore&&(modifiers&Qt::AltModifier)&&(modifiers&Qt::ShiftModifier);', 'const bool closest=onScore&&nearestWheelShortcut(wheel);')
edit(wheel, '(modifiers & Qt::ControlModifier) ||', '((modifiers & Qt::ControlModifier)&&!closest) ||')
edit(wheel, 'if (overStrip && !_scoreLane.contains(point)) return false;', 'if (!closest && overStrip && !_scoreLane.contains(point)) return false;')
edit(wheel, '''      const int delta = wheel->angleDelta().y(); const int pixels = wheel->pixelDelta().y();''', '''      const int delta = wheel->angleDelta().y() ? wheel->angleDelta().y() : (closest ? wheel->angleDelta().x() : 0);
      const int pixels = wheel->pixelDelta().y() ? wheel->pixelDelta().y() : (closest ? wheel->pixelDelta().x() : 0);''')
edit(wheel, '      _wheelTimer.start(); wheel->accept(); return true;', '      rememberWheelFeedback();_wheelFeedbackTimer.stop();_wheelTimer.start(); wheel->accept(); return true;')
edit(wheel, '      _wheelTimer.stop(); _wheelSurface = nullptr;', '      if(_wheelIndex>=0){rememberWheelFeedback();_wheelFeedbackTicks=0;_wheelFeedbackTimer.start(30);}\n      _wheelTimer.stop(); _wheelSurface = nullptr;')
edit(wheel, '''      return QRectF(qBound(0.0, _wheelPoint.x() + 10, double(qMax(0, surface->width() - 236))),
            qBound(0.0, _wheelPoint.y() - 25, double(qMax(0, surface->height() - 24))), 232, 22);''', '''      const auto point=_wheelIndex>=0?_wheelPoint:_wheelFeedbackPoint;
      return QRectF(qBound(0.0, point.x()+16,double(qMax(0,surface->width()-276))),
            qBound(0.0,point.y()-63,double(qMax(0,surface->height()-55))),272,52);''')
start=(HOST/wheel).read_text(encoding='utf-8');a=start.index('      if (_wheelIndex < 0',start.index('void PerformanceEditor::paintWheelBadge'));b=start.index('\n      }',a)
edit(wheel,start[a:b],'''      if(_wheelFeedbackSurface!=surface || (_wheelIndex<0&&!_wheelFeedbackTimer.isActive()))return;
      painter.save();const double opacity=_wheelIndex>=0?1.:qBound(0.,(30.-_wheelFeedbackTicks)/8.,1.);painter.setOpacity(opacity);
      if(surface==_view && !_wheelFeedbackHead.isEmpty()){
            auto head=_view->matrix().mapRect(_wheelFeedbackHead).adjusted(-3,-3,3,3);painter.setBrush(Qt::NoBrush);painter.setPen(QPen(_wheelFeedbackColor,2.5));painter.drawRoundedRect(head,3,3);}
      const auto badge=wheelBadge(surface);painter.setBrush(_appearance.colors[PerformanceAppearance::Background]);painter.setPen(QPen(_wheelFeedbackColor,1.5));painter.drawRoundedRect(badge,4,4);
      painter.fillRect(QRectF(badge.left(),badge.top()+5,4,badge.height()-10),_wheelFeedbackColor);
      painter.setPen(_appearance.colors[PerformanceAppearance::Text]);QFont font=painter.font();font.setBold(false);painter.setFont(font);painter.drawText(badge.adjusted(12,3,-5,-28),Qt::AlignVCenter,_wheelFeedbackName);
      font.setBold(true);font.setPointSizeF(font.pointSizeF()>0?font.pointSizeF()+1:10);painter.setFont(font);painter.drawText(badge.adjusted(12,23,-5,-3),Qt::AlignVCenter,_wheelFeedbackValue);painter.restore();''')
edit(wheel, '      if (index < 0 || index >= _notes.size()) return;\n      buildGeometry();', '''      if (index < 0 || index >= _notes.size()) return;
      if(_view)_view->update(_view->matrix().mapRect(_notes[index].bounds).adjusted(-6,-6,6,6).toAlignedRect());
      buildGeometry();''')

# All mirrors represent the same complete source files.
for name in changed:
    dst=ROOT/'native'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((HOST/name).read_bytes())
print('Updated',len(changed),'files')
