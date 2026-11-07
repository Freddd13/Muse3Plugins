"""One-time editor wiring for the MIDI track workspace; preserve host changes."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/'muse3_dev/MuseScore'
NATIVE=ROOT/'P2/native'
def edit(name,old,new):
    path=NATIVE/name
    if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((HOST/name).read_bytes())
    text=path.read_text('utf8')
    if new in text:return
    if text.count(old)!=1:raise RuntimeError((name,text.count(old),old[:80]))
    path.write_text(text.replace(old,new),encoding='utf8')

edit('mscore/performanceeditor/performanceeditor.h','\nclass RollWritingBar;','\nclass RollWritingBar;\nclass MidiTrackPane;')
edit('mscore/performanceeditor/performanceeditor.h','      RollWritingBar* _rollWriting=nullptr;','      RollWritingBar* _rollWriting=nullptr;\n      friend class MidiTrackPane;\n      MidiTrackPane* _midiTracks=nullptr;')
edit('mscore/performanceeditor/performanceeditor.h','      ~PerformanceEditor() override;','      ~PerformanceEditor() override;\n      void showMidiTracks(bool);\n      int timelineEndTick() const;')
for name in ('performanceeditor.cpp','performancepainting.cpp','performanceinteraction.cpp'):
    edit('mscore/performanceeditor/'+name,'#include "rollwriting.h"','#include "rollwriting.h"\n#include "miditrackpane.h"')
edit('mscore/performanceeditor/performanceux.cpp','#include "performanceeditor.h"','#include "performanceeditor.h"\n#ifdef SCRIPT_INTERFACE\n#include "miditrackpane.h"\n#endif')
edit('mscore/performanceeditor/performanceeditor.cpp','      _rollWriting=new RollWritingBar(this,writeToggle,noteArea);noteLayout->insertWidget(1,_rollWriting);','      _rollWriting=new RollWritingBar(this,writeToggle,noteArea);noteLayout->insertWidget(1,_rollWriting);\n      _midiTracks=new MidiTrackPane(this,noteArea,noteLayout);')
edit('mscore/performanceeditor/performanceeditor.cpp','      if(_rollWriting)_rollWriting->shutdown();','      if(_midiTracks)_midiTracks->shutdown();\n      if(_rollWriting)_rollWriting->shutdown();')
edit('mscore/performanceeditor/performanceeditor.cpp','void PerformanceEditor::resizeEvent(QResizeEvent* event)', '''void PerformanceEditor::showMidiTracks(bool on)
      {
#ifdef SCRIPT_INTERFACE
      if(_midiTracks)_midiTracks->setWorkspaceVisible(on);
#endif
      }
int PerformanceEditor::timelineEndTick() const
      {
      int end=comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick;
#ifdef SCRIPT_INTERFACE
      if(_midiTracks)end=qMax(end,_midiTracks->endTick());
#endif
      return end;
      }
void PerformanceEditor::resizeEvent(QResizeEvent* event)''')
# The native end stays intact; only the editor's scrollable canvas includes MIDI.
path=NATIVE/'mscore/performanceeditor/performanceeditor.cpp'
text=path.read_text('utf8')
text=text.replace('qBound(0,tick,comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick)','qBound(0,tick,timelineEndTick())')
text=text.replace('(comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick) - (until - from)','timelineEndTick() - (until - from)')
path.write_text(text,encoding='utf8')
edit('mscore/performanceeditor/performancepainting.cpp','      if(_rollWriting)_rollWriting->contextChanged();','      if(_midiTracks)_midiTracks->contextChanged();\n      if(_rollWriting&&(!_midiTracks||!_midiTracks->active()))_rollWriting->contextChanged();')
edit('mscore/performanceeditor/performancepainting.cpp','(comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick) - span','timelineEndTick() - span')
edit('mscore/performanceeditor/performancepainting.cpp','            if(_rollWriting)_rollWriting->paint(painter,area);','            if(_rollWriting&&(!_midiTracks||!_midiTracks->active()))_rollWriting->paint(painter,area);\n            if(_midiTracks)_midiTracks->paintNotes(painter,area);')
edit('mscore/performanceeditor/performancepainting.cpp','                  if (!geometry.rect.adjusted(-3, -3, 3, 3).intersects(clip)) continue;','''#ifdef SCRIPT_INTERFACE
                  if(_midiTracks&&!_midiTracks->scoreVisible())continue;
#endif
                  if (!geometry.rect.adjusted(-3, -3, 3, 3).intersects(clip)) continue;''')
edit('mscore/performanceeditor/performancepainting.cpp','            _lane = laneRect(); paintLane(painter, _lane, false);','''            _lane = laneRect();
#ifdef SCRIPT_INTERFACE
            const bool midiValues=_midiTracks&&_midiTracks->paintValues(painter,_lane);
            if(!midiValues)
#endif
            paintLane(painter, _lane, false);''')
edit('mscore/performanceeditor/performancepainting.cpp','      const int tick = _seeking ? _seekTick : _playTick;','''#ifdef SCRIPT_INTERFACE
      const bool midiCursor=_midiTracks&&_midiTracks->paintPlayhead(painter,widget);
      const int tick=midiCursor?-1:(_seeking?_seekTick:_playTick);
#else
      const int tick = _seeking ? _seekTick : _playTick;
#endif''')
edit('mscore/performanceeditor/performanceinteraction.cpp','      if(notes&&_rollWriting&&_rollWriting->handle(event))return true;','      if(_midiTracks&&_midiTracks->handle(event,parameter,ruler))return true;\n      if(notes&&_rollWriting&&(!_midiTracks||!_midiTracks->active())&&_rollWriting->handle(event))return true;')
edit('mscore/performanceeditor/performanceux.cpp','      _usedPitches.clear();for(const auto& n:_notes)if(n.enabled)_usedPitches.insert(n.pitch);','''      _usedPitches.clear();for(const auto& n:_notes)if(n.enabled)_usedPitches.insert(n.pitch);
#ifdef SCRIPT_INTERFACE
      if(_midiTracks)_usedPitches.unite(_midiTracks->visiblePitches());
#endif''')
edit('mscore/performanceeditor/performanceeditor.cmake','if(SCRIPT_INTERFACE)','''if(SCRIPT_INTERFACE)
 list(APPEND PERFORMANCEEDITOR_SRC ${CMAKE_CURRENT_LIST_DIR}/miditrackpane.cpp ${CMAKE_CURRENT_LIST_DIR}/miditrackpane.h ${CMAKE_CURRENT_LIST_DIR}/miditrackinteraction.cpp ${CMAKE_CURRENT_LIST_DIR}/miditrackplayback.cpp ${CMAKE_CURRENT_LIST_DIR}/miditrackalignment.cpp)''')
edit('mscore/musescore.cpp','#include "performanceeditor/rollwriting.h"','#include "performanceeditor/rollwriting.h"\n#include "performanceeditor/miditrackpane.h"')
edit('mscore/musescore.cpp','      if (!menuView->actions().contains(rollWritingAction())) menuView->addAction(rollWritingAction());','      if (!menuView->actions().contains(rollWritingAction())) menuView->addAction(rollWritingAction());\n      if (!menuView->actions().contains(midiTracksAction())) menuView->addAction(midiTracksAction());')

# Hand MIDI notes to the existing notation draft so quantization, undo and
# boundary handling remain shared with direct roll writing.
edit('mscore/performanceeditor/rollwriting.h','  QVariantList _rows, _before,','  QVariantList _importRows;\n  int _importTrack=-1;\n  QVariantList _rows, _before,')
edit('mscore/performanceeditor/rollwriting.h','  void shutdown();','  void shutdown();\n  void openMidiDraft(const QVariantList&,int track,bool selectedScope);')
edit('mscore/performanceeditor/rollwritingmodel.cpp','void RollWritingBar::readScope(const QVariantMap &requested) {','''void RollWritingBar::openMidiDraft(const QVariantList& rows,int track,bool selectedScope) {
  if(rows.isEmpty()){setMessage(tr("这条轨道还没有可写入的音符。"));return;}
  _mode->setCurrentIndex(1);_importRows=rows;_importTrack=track;
  setWritingEnabled(true);
  if(!selectedScope) {
    int from=INT_MAX,until=0;for(const auto& value:rows){const auto n=value.toMap();from=qMin(from,n.value("start").toInt());until=qMax(until,n.value("end").toInt());}
    readScope({{"start",from},{"end",qMin(until,_editor->_endTick)},{"firstTrack",track},{"endTrack",track+1}});
  }
}
void RollWritingBar::readScope(const QVariantMap &requested) {''')
edit('mscore/performanceeditor/rollwritingmodel.cpp','  _pendingLocations.clear();\n  selectSourceNotes();','''  _pendingLocations.clear();
  if(!_importRows.isEmpty()) {
    const int target=_importTrack;
    _rows.erase(std::remove_if(_rows.begin(),_rows.end(),[target](const QVariant& value){return value.toMap().value("track").toInt()==target;}),_rows.end());
    for(const auto& value:_importRows){auto n=value.toMap();if(n.value("start").toInt()<scope.value("start").toInt()||n.value("start").toInt()>=scope.value("end").toInt())continue;n["end"]=qMin(n.value("end").toInt(),scope.value("end").toInt());n["rawEnd"]=n["end"];n["track"]=target;n["id"]=freshId();_rows.append(n);}
    _importRows.clear();_track->setCurrentIndex(qMax(0,_track->findData(target)));_precision->setChecked(true);_followDynamics->setChecked(false);_hasChanges=true;_selected.clear();
    setMessage(tr("MIDI已放入草稿。检查网格与目标声部，试听后点“使用草稿”。"));
  }
  selectSourceNotes();''')
print('Prepared MIDI editor wiring')
