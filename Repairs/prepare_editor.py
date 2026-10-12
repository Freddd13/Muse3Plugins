# coding: utf-8
from pathlib import Path
host=Path(r'E:/programming/funcodes/muse3_dev/MuseScore');out=Path('Repairs/native/mscore/performanceeditor');out.mkdir(parents=True,exist_ok=True)
names=['performanceeditor.h','performanceeditor.cpp','performanceinteraction.cpp','performancepainting.cpp','performanceoverlay.cpp','performancewheel.cpp','performanceview.h','performanceview.cpp','performancesettings.h','performancesettings.cpp','performancecontrols.cpp','performanceeditor.cmake']
for name in names:
 p=out/name
 if not p.exists():p.write_bytes((host/'mscore/performanceeditor'/name).read_bytes())
def edit(name,old,new):
 p=out/name;s=p.read_text(encoding='utf8')
 if new in s:return
 if s.count(old)!=1:raise RuntimeError(name+': cannot identify '+old[:65])
 p.write_bytes(s.replace(old,new).encode('utf8'))
edit('performanceinteraction.cpp','      std::stable_sort(result.begin(), result.end(), [this, point, parameter, lane, onScore](int a, int b) {','''      int nearestTick=-1;double nearestColumn=1e20;
      if(parameter)for(int i:result){double d=std::abs(xForNote(i,onScore)-point.x());if(d<nearestColumn){nearestColumn=d;nearestTick=_notes[i].tick;}}
      std::stable_sort(result.begin(), result.end(), [this, point, parameter, lane, onScore,nearestTick](int a, int b) {''')
edit('performanceinteraction.cpp','            if (parameter) {\n                  const int da','''            if (parameter) {
                  const bool chosenA=_notes[a].tick==nearestTick&&_notes[a].selected,chosenB=_notes[b].tick==nearestTick&&_notes[b].selected;
                  if(chosenA!=chosenB)return chosenA;
                  const int da''')
edit('performanceinteraction.cpp','if (mouse->button() == Qt::LeftButton && mouse->x() >= PerformanceViewport::gutter && (!parameter || _parameter->currentIndex() == 0)) {','if (mouse->button() == Qt::LeftButton && mouse->modifiers()==Qt::NoModifier && mouse->x() >= PerformanceViewport::gutter && (!parameter || _parameter->currentIndex() == 0)) {')
edit('performanceeditor.h','      bool _cycleOnClick = false;','''      bool _cycleOnClick = false;
      bool _gestureMoved = false;
      double _dragSensitivity = 1.;
      bool _relativeActual = false;
      int _keyboardMode = 1;
      QSet<int> _disabledTracks, _usedPitches;
      bool _peekHeld=false, _peekAll=false;
      int _peekKey=0;
      QVector<QPair<int,QRectF>> _visibleScoreNotes;
      QTransform _visibleScoreMatrix;
      QRect _visibleScoreRect;
      ScoreContentState _visibleScoreState;
      void setupUsabilityControls();
      void showTrackFilter();
      void quickFilter(int mode);
      void rebuildPitchRows();
      void rebuildVisibleScoreNotes();
      bool peekKeyEvent(QObject*,QEvent*);
      int keyboardPitch(QPointF) const;
      void paintOriginalVelocity(QPainter&,const QRectF&,bool);
      friend class PerformancePeekKeys;
      bool _bandResizing=false;
      int _bandResizeHeight=0;''')
edit('performanceeditor.cpp','_noteGesture = false; _cycleOnClick = false; _scoreGesture = onScore;','_noteGesture = false; _cycleOnClick = false; _gestureMoved=false; _scoreGesture = onScore;')
edit('performanceeditor.cpp','      if (!_dragging) return;\n      QElapsedTimer gestureTimer; gestureTimer.start();','''      if (!_dragging) return;
      if(!_gestureMoved&&QLineF(_press,point).length()<QApplication::startDragDistance())return;
      _gestureMoved=true;
      QElapsedTimer gestureTimer; gestureTimer.start();''')
edit('performanceeditor.cpp','const double delta = _noteGesture ? (_press.y() - point.y()) * (range.maximum - range.minimum) / qMax(1.0, _gestureLane.height()) : valueForY(point.y(), _gestureLane, _scoreGesture) - valueForY(_press.y(), _gestureLane, _scoreGesture);','const double delta = (_noteGesture ? (_press.y() - point.y()) * (range.maximum - range.minimum) / qMax(1.0, _gestureLane.height()) : valueForY(point.y(), _gestureLane, _scoreGesture) - valueForY(_press.y(), _gestureLane, _scoreGesture))*_dragSensitivity;')
edit('performanceeditor.cpp','if (_cycleOnClick && QLineF(_press, _last).length() < 3)','if (_cycleOnClick && !_gestureMoved)')
edit('performanceeditor.cpp','      const int raw = _axis->currentIndex() ? qBound(NoteVelocity::minOffset, qRound(value), NoteVelocity::maxOffset) : qBound(1, qRound(value), 127);','      const bool relative=_axis->currentIndex()&&!_relativeActual;\n      const int raw = relative ? qBound(NoteVelocity::minOffset, qRound(value), NoteVelocity::maxOffset) : qBound(1, qRound(value), 127);')
edit('performanceeditor.cpp','      if (note.base < 0 && (_axis->currentIndex() ? type != Note::ValueType::OFFSET_VAL : type != Note::ValueType::USER_VAL)) return;','      if (note.base < 0 && (relative ? type != Note::ValueType::OFFSET_VAL : type != Note::ValueType::USER_VAL)) return;')
edit('performanceeditor.cpp','? (_axis->currentIndex() ? raw : NoteVelocity::offsetFor(note.base, raw))\n            : (_axis->currentIndex() ? NoteVelocity::effective(note.base, Note::ValueType::OFFSET_VAL, raw) : raw));','? (relative ? raw : NoteVelocity::offsetFor(note.base, raw))\n            : (relative ? NoteVelocity::effective(note.base, Note::ValueType::OFFSET_VAL, raw) : raw));')
edit('performanceeditor.cpp','      if (!_axis->currentIndex()) return NoteVelocity::effective(note.base, edit.type, edit.raw);','      if (!_axis->currentIndex()||_relativeActual) return NoteVelocity::effective(note.base, edit.type, edit.raw);')
edit('performancepainting.cpp','{ return _parameter->currentIndex() == 0 ? _axis->currentIndex() : _parameter->currentIndex() + 1; }','{ return _parameter->currentIndex() == 0 ? (_relativeActual?0:_axis->currentIndex()) : _parameter->currentIndex() + 1; }')
edit('performanceinteraction.cpp','note.enabled = note.inScope && staffEnabled(note.track) &&','note.enabled = note.inScope && staffEnabled(note.track) && !_disabledTracks.contains(note.track) &&')
edit('performanceinteraction.cpp','      _selectionRefreshNeeded = false; _hover = -1; updateSelection(); if (changed)','      rebuildPitchRows();_visibleScoreNotes.clear();\n      _selectionRefreshNeeded = false; _hover = -1; updateSelection(); if (changed)')
edit('performancepainting.cpp','Qt::AlignVCenter | Qt::AlignRight, pitchName(pitch)','Qt::AlignVCenter | Qt::AlignHCenter, pitchName(pitch)')
edit('performanceoverlay.cpp','if (frameTop >= 4 && frameBottom <= qMin(double(_view->height() - 12), nextTop)) top = frameTop + 26;','''if (frameTop >= 4 && frameBottom <= qMin(double(_view->height() - 12), nextTop)) top = frameTop + 26;
            else if(nextTop-frameTop>=_bandHeight+31)top=qBound(30.,frameTop+26,double(_view->height()-_bandHeight-12));''')
edit('performanceoverlay.cpp','      QVector<int> handles = _selectedIndices;','''      QVector<int> handles = _selectedIndices;
      if(_peekHeld){rebuildVisibleScoreNotes();for(auto item:_visibleScoreNotes)if(noteEditable(_notes[item.first])&&(_peekAll||QLineF(item.second.center(),_overlayPointer).length()<160)&&!handles.contains(item.first))handles.append(item.first);}''')
edit('performanceoverlay.cpp','if (_handles->isChecked() || _band->isChecked()) for (int i : handles)','if (_handles->isChecked() || _band->isChecked() || _peekHeld) for (int i : handles)')
edit('performanceoverlay.cpp','if (!_handles->isChecked() || _parameter->currentIndex() != 0) continue;','if ((!_handles->isChecked()&&!_peekHeld) || _parameter->currentIndex() != 0 || !noteEditable(note)) continue;')
edit('performanceoverlay.cpp','if (_view->matrix().m11() > 0.5) painter.drawText','painter.drawText')
# Keep notes and normal wheel editing intact; the explicit modifier opts into closest-on-screen editing.
edit('performancewheel.cpp','      const bool temporary = !onScore && (modifiers & Qt::AltModifier);','      const bool closest=onScore&&(modifiers&Qt::AltModifier)&&(modifiers&Qt::ShiftModifier);\n      const bool temporary = closest||(!onScore && (modifiers & Qt::AltModifier));')
edit('performancewheel.cpp','(onScore && (modifiers & Qt::AltModifier))','(onScore && (modifiers & Qt::AltModifier)&&!closest)')
edit('performancewheel.cpp','      else if (onScore) {','''      else if(closest){
            rebuildVisibleScoreNotes();double best=1e20;for(auto item:_visibleScoreNotes){double d=QLineF(point,item.second.center()).length();if(d<best&&noteEditable(_notes[item.first])){best=d;target=item.first;}}
            }
      else if (onScore) {''')
# Preserve a burst's target even if its endpoint or the pointer moves slightly.
edit('performancewheel.cpp','QLineF(point, _wheelPoint).length() <= 4','(closest||QLineF(point, _wheelPoint).length() <= 4)')
for name in ['performanceeditor.cpp','performanceinteraction.cpp']:
 p=out/name;s=p.read_text(encoding='utf8').replace('基准待停播','原力度需停播读取').replace('实际 MIDI 基准待停播','实际力度需停播读取').replace(' · 基准 %2',' · 原力度 %2');p.write_bytes(s.encode('utf8'))
print('Editor interaction changes prepared; additional shared controls are next.')
