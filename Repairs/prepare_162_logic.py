from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];NATIVE=ROOT/'P2/native'
def edit(name,old,new):
    path=NATIVE/name;text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError('Expected '+name+' '+old[:70])
    path.write_bytes(text.replace(old,new,1).encode('utf8'))
edit('mscore/performanceeditor/spectrumpane.h','    SpectrumCanvas *_canvas = nullptr;','    QWidget *_canvas = nullptr;')
edit('mscore/performanceeditor/spectrumpane.cpp','    if (object == this && _displayControls &&','    if(object==_canvas && event->type()==QEvent::Leave)clearHover();\n    if (object == this && _displayControls &&')
edit('mscore/performanceeditor/spectrumpane.cpp','void SpectrumPane::pointer(QMouseEvent *e, bool release) {','void SpectrumPane::pointer(QMouseEvent *e, bool release) {\n    hoverChanged(e->localPos(),_display->currentIndex()==1);')
edit('mscore/performanceeditor/spectrumpane.cpp','void SpectrumPane::hideEvent(QHideEvent *) {','void SpectrumPane::hideEvent(QHideEvent *) {\n    clearHover();')
edit('mscore/performanceeditor/spectrumpane.cpp','                p.setBrush(QColor(black ? "#161616" : "#f1f1f1"));','                p.setBrush(shown==_hoverKey?palette().highlight().color():QColor(black ? "#161616" : "#f1f1f1"));')
path=NATIVE/'mscore/performanceeditor/spectrumpane.cpp';text=path.read_text('utf8')
start=text.index('    if (_harmonics->isChecked() && _hasPick)');end=text.index('    p.setPen(accent);',start)
text=text[:start]+'    paintMidi(p,bounds,overlay);\n    paintReferences(p,bounds,overlay);\n'+text[end:]
path.write_bytes(text.encode('utf8'))
edit('mscore/performanceeditor/spectrumpane.cpp','    if (_clip.isEmpty())\n            _from = value;','    if (!usesScoreTimeline())\n            _from = value;') if '    if (_clip.isEmpty())\n            _from = value;' in path.read_text('utf8') else edit('mscore/performanceeditor/spectrumpane.cpp','        if (_clip.isEmpty())\n            _from = value;','        if (!usesScoreTimeline())\n            _from = value;')
edit('mscore/performanceeditor/spectrumpane.cpp','    if (_clip.isEmpty()) {\n        const int duration = qBound','    if (!usesScoreTimeline()) {\n        const int duration = qBound')
edit('mscore/performanceeditor/spectrumpane.cpp','int SpectrumPane::linkedTimelineWidth() const { return isVisible() && !_clip.isEmpty() ? sourceWidth() : -1; }','int SpectrumPane::linkedTimelineWidth() const { return isVisible() && usesScoreTimeline() ? sourceWidth() : -1; }')
edit('mscore/performanceeditor/spectrumpane.cpp','    if (property("linkedTimelineWidth").toInt() != width) {','    const int end=timelineEndTick();\n    if (property("linkedTimelineWidth").toInt() != width || property("spectrumTimelineEnd").toInt()!=end) {\n        setProperty("spectrumTimelineEnd",end);')
start=path.read_text('utf8').index('void SpectrumPane::editorTimelineZoomed(');text=path.read_text('utf8');end=text.index('double SpectrumPane::timeAtX(',start)
text=text[:start]+'''void SpectrumPane::editorTimelineZoomed(double,double) {
    if(isVisible() && _display->currentIndex()==1)viewChanged();
}
'''+text[end:];path.write_bytes(text.encode('utf8'))
edit('mscore/performanceeditor/spectrumpane.cpp','''    return _clip.isEmpty() ? _from + (x - gutter) / plotWidth() * _span
                           : audioAt(_clip, _editor->tickForX(x, false));''','''    if(!_clip.isEmpty())return audioAt(_clip,_editor->tickForX(x,false));
    if(_display->currentIndex()==1 && _editor->score())return _editor->score()->tempomap()->tick2time(_editor->tickForX(x,false))*1000.;
    return _from+(x-gutter)/plotWidth()*_span;''')
edit('mscore/performanceeditor/spectrumpane.cpp','''    return _clip.isEmpty() ? gutter + (ms - _from) / _span * plotWidth()
                           : _editor->xForTick(qRound(tickAt(_clip, ms)), false);''','''    if(!_clip.isEmpty())return _editor->xForTick(qRound(tickAt(_clip,ms)),false);
    if(_display->currentIndex()==1 && _editor->score())return _editor->xForTick(_editor->score()->tempomap()->time2tick(ms/1000.),false);
    return gutter+(ms-_from)/_span*plotWidth();''')
edit('mscore/performanceeditor/spectrumpane.cpp','''        if (_clip.isEmpty())
            _from = qMax(0., _pressFrom - delta);''','''        if (!usesScoreTimeline())
            _from = qMax(0., _pressFrom - delta);''')
edit('mscore/performanceeditor/spectrumpane.cpp','        cuts.append(_info.value("until").toDouble());','''        if(_clip.isEmpty() && overlay && _editor->score()) {
            auto tempo=_editor->score()->tempomap();
            for(const auto& entry:*tempo) {
                const double ms=tempo->tick2time(entry.first)*1000.;
                if(ms>cuts.front() && ms<_info.value("until").toDouble())cuts.append(ms);
            }
        }
        cuts.append(_info.value("until").toDouble());''')
edit('mscore/performanceeditor/spectrumpane.cpp','''        if (_display->currentIndex() == 1)
            _editor->zoomTimeline(_span / span, gutter);
        else
            _span = span;
        _from = qMax(0., _cursorMs - _span / 2);''','''        if (_display->currentIndex() == 1 && _editor->score()) {
            auto tempo=_editor->score()->tempomap();
            const double begin=qMax(0.,_cursorMs-span/2),end=qMin(_audio->property("duration").toDouble(),begin+span);
            const int first=tempo->time2tick(begin/1000.),last=tempo->time2tick(end/1000.);
            const double units=_editor->comparisonTimeActive()?2.*(end-begin)/1000.:double(last-first)/DIVISION;
            if(units>0){_editor->_viewport.pixelsPerQuarter=qBound(.01,plotWidth()/units,1000.);_editor->surfaceResized(PerformanceSurface::Notes);_editor->_scroll->setValue(first);_editor->invalidateVisual();}
        }else {_span=span;_from=qMax(0.,_cursorMs-_span/2);}''')
edit('mscore/performanceeditor/performanceeditor.cpp','      if(_timingEditor)end=qMax(end,_timingEditor->endTick());','      if(_timingEditor)end=qMax(end,_timingEditor->endTick());\n      if(_spectrum)end=qMax(end,_spectrum->timelineEndTick());')
# The renderer accumulates one fixed block at a time, including whole-recording views.
edit('mscore/referenceaudio/spectrum.cpp','r.untilMs - r.fromMs > 120000','r.untilMs - r.fromMs > 86400000')
text=path.read_text('utf8')
text=text.replace('qBound(250., _audio->property("duration").toDouble(), 120000.)','qBound(250., _audio->property("duration").toDouble(), 86400000.)')
text=text.replace('qMin(from + 120000., std::ceil(until / 20.) * 20.)','qMin(from + 86400000., std::ceil(until / 20.) * 20.)')
text=text.replace('qBound(250., _span / factor, 120000.)','qBound(250., _span / factor, 86400000.)')
path.write_bytes(text.encode('utf8'))
edit('mtest/mscore/spectrum/tst_spectrum.cpp','value["until"] = 200000.;','value["until"] = 86401000.;')
print('Prepared spectrum hover, guides and common roll time mapping')
