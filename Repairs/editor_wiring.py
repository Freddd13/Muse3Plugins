# coding: utf-8
from pathlib import Path
root=Path('Repairs/native/mscore/performanceeditor')
def edit(n,a,b):
 p=root/n;s=p.read_text(encoding='utf8')
 if a not in s:
  if b in s:return
  raise RuntimeError(n+': '+a[:90])
 if s.count(a)!=1:raise RuntimeError('ambiguous '+n+': '+a[:90])
 p.write_text(s.replace(a,b),encoding='utf8')
edit('performanceview.h','      double pixelsPerQuarter = 72, rowHeight = 12, topPitch = 72;','''      double pixelsPerQuarter = 72, rowHeight = 12, topPitch = 72;
      QVector<int> pitchRows;
      double pitchIndex(double pitch) const;
      double pitchAtIndex(double index) const;
      double pitchY(double pitch) const { return (pitchIndex(topPitch)-pitchIndex(pitch))*rowHeight; }
      double rowMaximum() const { return pitchRows.isEmpty()?127:pitchRows.size()-1; }
      bool showsPitch(int pitch) const { return pitchRows.isEmpty()||pitchRows.contains(pitch); }''')
p=root/'performanceview.cpp';s=p.read_text(encoding='utf8');marker='namespace Ms {';assert s.count(marker)==1
if 'PerformanceViewport::pitchIndex' not in s:s=s.replace(marker,marker+'''
double PerformanceViewport::pitchIndex(double pitch) const
      {
      if(pitchRows.isEmpty()) return pitch;
      if(pitch<=pitchRows.front()) return pitch-pitchRows.front();
      for(int i=1;i<pitchRows.size();++i) if(pitch<=pitchRows[i]) return i-1+(pitch-pitchRows[i-1])/double(pitchRows[i]-pitchRows[i-1]);
      return pitchRows.size()-1+pitch-pitchRows.back();
      }
double PerformanceViewport::pitchAtIndex(double index) const
      {
      if(pitchRows.isEmpty()) return index;
      if(index<=0) return pitchRows.front()+index;
      int i=int(index);
      if(i>=pitchRows.size()-1) return pitchRows.back()+index-(pitchRows.size()-1);
      return pitchRows[i]+(index-i)*(pitchRows[i+1]-pitchRows[i]);
      }
''');p.write_text(s,encoding='utf8')
edit('performanceeditor.cpp','      applyAppearance(); status();','      setupUsabilityControls(); applyAppearance(); status();')
edit('performanceeditor.cpp','_viewport.topPitch = 127 - value / 100.0','_viewport.topPitch = _viewport.pitchAtIndex(_viewport.rowMaximum() - value / 100.0)')
edit('performanceeditor.cpp','      _layoutIndex.clear();','      _visibleScoreNotes.clear(); _layoutIndex.clear();')
edit('performanceeditor.cpp','{ return isVisible() || (_band->isChecked() && _view && _view->isVisible()); }','{ return isVisible() || ((_band->isChecked()||_peekHeld) && _view && _view->isVisible()); }')
edit('performanceeditor.cpp','      if (note.base < 0) return _axis->currentIndex() ? edit.raw : qBound(1, edit.raw, 127);','      if (note.base < 0) return rangeKind()==1 ? edit.raw : qBound(1, edit.raw, 127);')
edit('performanceeditor.cpp','_number->setSuffix(velocity && _axis->currentIndex() ? " %" : QString());','_number->setSuffix(velocity && rangeKind()==1 ? " %" : QString());')
edit('performanceeditor.cpp','_number->setRange(velocity ? (_axis->currentIndex() ? NoteVelocity::minOffset : 1) : 5,\n                  velocity ? (_axis->currentIndex() ? NoteVelocity::maxOffset : 127) : 999);','_number->setRange(velocity ? (rangeKind()==1 ? NoteVelocity::minOffset : 1) : 5,\n                  velocity ? (rangeKind()==1 ? NoteVelocity::maxOffset : 127) : 999);')
edit('performanceinteraction.cpp','{ return note.base >= 0 || (_axis->currentIndex() ? note.type == Note::ValueType::OFFSET_VAL : note.type == Note::ValueType::USER_VAL); }','{ return note.base >= 0 || (rangeKind()==1 ? note.type == Note::ValueType::OFFSET_VAL : note.type == Note::ValueType::USER_VAL); }')
# Resolve exact-onset candidates once. BeginGesture was independently redoing the distance search.
edit('performanceeditor.cpp','            double distance = 13;','            if(forcedAnchor<0&&_tool->currentIndex()==0){const auto candidates=hits(point,true,onScore);if(!candidates.isEmpty())_anchor=candidates.front();}\n            double distance = _anchor>=0 ? -1 : 13;')
edit('performanceinteraction.cpp','const double middle = _viewport.topPitch - _noteCanvas->height() / (2 * _viewport.rowHeight);','const double middle = _viewport.pitchIndex(_viewport.topPitch) - _noteCanvas->height() / (2 * _viewport.rowHeight);')
edit('performanceinteraction.cpp','_viewport.topPitch = middle + _noteCanvas->height() / (2 * _viewport.rowHeight);','_viewport.topPitch = _viewport.pitchAtIndex(middle + _noteCanvas->height() / (2 * _viewport.rowHeight));')
edit('performanceinteraction.cpp','if (!selection && _score && _score->nstaves() && _scope->currentIndex() != 2)','if (!selection && _viewport.pitchRows.isEmpty() && _score && _score->nstaves() && _scope->currentIndex() != 2)')
edit('performanceinteraction.cpp','double(_noteCanvas->height()) / (high - low + 7)','double(_noteCanvas->height()) / (_viewport.pitchIndex(high) - _viewport.pitchIndex(low) + 7)')
edit('performanceinteraction.cpp','_viewport.topPitch = (low + high) / 2.0 + _noteCanvas->height() / _viewport.rowHeight / 2 - 0.5;','_viewport.topPitch = _viewport.pitchAtIndex((_viewport.pitchIndex(low) + _viewport.pitchIndex(high)) / 2 + _noteCanvas->height() / _viewport.rowHeight / 2 - .5);')
edit('performanceinteraction.cpp','const double pitch = _viewport.topPitch - wheel->position().y() / _viewport.rowHeight; _viewport.rowHeight = qBound(2.0, _viewport.rowHeight * factor, 36.0); _viewport.topPitch = pitch + wheel->position().y() / _viewport.rowHeight;','const double pitch = _viewport.pitchIndex(_viewport.topPitch) - wheel->position().y() / _viewport.rowHeight; _viewport.rowHeight = qBound(2.0, _viewport.rowHeight * factor, 36.0); _viewport.topPitch = _viewport.pitchAtIndex(pitch + wheel->position().y() / _viewport.rowHeight);')
edit('performanceinteraction.cpp','_viewport.topPitch += wheel->angleDelta().y() / 40.0','_viewport.topPitch = _viewport.pitchAtIndex(_viewport.pitchIndex(_viewport.topPitch)+wheel->angleDelta().y() / 40.0)')
p=root/'performanceinteraction.cpp';s=p.read_text(encoding='utf8').replace('PerformanceKeyboard::pitchAt(help->pos(), _viewport.topPitch, _viewport.rowHeight, PerformanceViewport::gutter)','keyboardPitch(help->pos())').replace('PerformanceKeyboard::pitchAt(mouse->pos(), _viewport.topPitch, _viewport.rowHeight, PerformanceViewport::gutter)','keyboardPitch(mouse->pos())');p.write_text(s,encoding='utf8')
edit('performancepainting.cpp','_viewport.topPitch = qBound(qMin(127.0, rows - 1), _viewport.topPitch, 127.0);','const double maximum=_viewport.rowMaximum();\n            _viewport.topPitch = _viewport.pitchAtIndex(qBound(qMin(maximum, rows - 1), _viewport.pitchIndex(_viewport.topPitch), maximum));')
edit('performancepainting.cpp','qRound((128 - rows) * 100)','qRound((_viewport.rowMaximum()+1 - rows) * 100)')
edit('performancepainting.cpp','qRound((127 - _viewport.topPitch) * 100)','qRound((_viewport.rowMaximum() - _viewport.pitchIndex(_viewport.topPitch)) * 100)')
p=root/'performancepainting.cpp';s=p.read_text(encoding='utf8').replace('_viewport.topPitch - _noteCanvas->height() / _viewport.rowHeight','_viewport.pitchAtIndex(_viewport.pitchIndex(_viewport.topPitch) - _noteCanvas->height() / _viewport.rowHeight)').replace('_viewport.topPitch - widget->height() / _viewport.rowHeight','_viewport.pitchAtIndex(_viewport.pitchIndex(_viewport.topPitch) - widget->height() / _viewport.rowHeight)').replace('(_viewport.topPitch - note.pitch) * _viewport.rowHeight','_viewport.pitchY(note.pitch)').replace('(_viewport.topPitch - pitch) * _viewport.rowHeight','_viewport.pitchY(pitch)')
s=s.replace('if (!note.inScope || (!note.enabled && !_ghostVoices)) continue;','if (!note.inScope || (!note.enabled && !_ghostVoices) || !_viewport.showsPitch(note.pitch)) continue;')
s=s.replace('for (int pitch = low; pitch <= high; ++pitch) {','for (int pitch = low; pitch <= high; ++pitch) {\n                  if(!_viewport.showsPitch(pitch))continue;',1)
s=s.replace('if (PerformanceKeyboard::isBlack(pitch) != black) continue;','if (PerformanceKeyboard::isBlack(pitch) != black || !_viewport.showsPitch(pitch)) continue;')
s=s.replace('painter.drawPolygon(PerformanceKeyboard::shape(pitch, _viewport.topPitch, _viewport.rowHeight, PerformanceViewport::gutter));','''if(_keyboardMode==1&&!_usedPitches.contains(pitch))painter.setOpacity(.28);
                  if(_keyboardMode==2&&!_viewport.pitchRows.isEmpty())painter.drawRect(QRectF(0,_viewport.pitchY(pitch),PerformanceViewport::gutter*(black?.58:1.),_viewport.rowHeight));
                  else painter.drawPolygon(PerformanceKeyboard::shape(pitch, _viewport.topPitch, _viewport.rowHeight, PerformanceViewport::gutter));''')
s=s.replace('Qt::AlignVCenter | Qt::AlignHCenter, pitchName(pitch));\n                        }','Qt::AlignVCenter | Qt::AlignHCenter, pitchName(pitch));\n                        }\n                  painter.setOpacity(1);')
s=s.replace('      if (parameter == 0) {','      if (parameter == 0) {\n            if(_relativeActual)paintOriginalVelocity(painter,rect,onScore);',1)
p.write_text(s,encoding='utf8')
p=root/'performanceoverlay.cpp';s=p.read_text(encoding='utf8').replace('if (_view->matrix().m11() > 0.5) painter.drawText','painter.drawText').replace('(_handles->isChecked() || _band->isChecked() || _wheelButton->isChecked())','(_handles->isChecked() || _band->isChecked() || _wheelButton->isChecked() || _peekHeld)').replace('!_handles->isChecked() && !_band->isChecked() && !_wheelButton->isChecked()','!_handles->isChecked() && !_band->isChecked() && !_wheelButton->isChecked() && !_peekHeld').replace('if (_overBand || before) {','if(_peekHeld)invalidateOverlay();\n            if (_overBand || before) {')
s=s.replace('_axis->currentIndex() ? "%" : ""','rangeKind()==1 ? "%" : ""').replace('_axis->currentIndex() ? "%" : " MIDI"','rangeKind()==1 ? "%" : " MIDI"')
p.write_text(s,encoding='utf8')
p=root/'performancewheel.cpp';s=p.read_text(encoding='utf8').replace('PerformanceViewport::limits(_axis->currentIndex() ? 1 : 0)','PerformanceViewport::limits(rangeKind())').replace('_axis->currentIndex() ? " %" : " MIDI"','rangeKind()==1 ? " %" : " MIDI"').replace('(modifiers & Qt::ShiftModifier) ? 8 : 1','((modifiers & Qt::ShiftModifier)&&!closest) ? 8 : 1');p.write_text(s,encoding='utf8')
edit('performanceeditor.cmake','      ${CMAKE_CURRENT_LIST_DIR}/performancecontrols.cpp','      ${CMAKE_CURRENT_LIST_DIR}/performancecontrols.cpp\n      ${CMAKE_CURRENT_LIST_DIR}/performanceux.cpp')
print('Shared pitch rows and interaction wiring prepared.')
