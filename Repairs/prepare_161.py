"""Connect N5 timing edits using explicit, guarded native files."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/'muse3_dev/MuseScore'
NATIVE=ROOT/'P2/native'
OUT=ROOT/'P2/out/repair-161'
OUT.mkdir(exist_ok=True)
FILES=['libmscore/performancetiming.cpp','libmscore/performancetiming.h',
       'mscore/performanceeditor/timingeditor.cpp','mscore/performanceeditor/timingeditor.h']
def edit(name,old,new):
    path=NATIVE/name
    before=(HOST/name).read_bytes()
    if not path.is_file():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(before)
    text=path.read_text('utf8')
    if name not in FILES:FILES.append(name)
    if new in text:return
    if old not in text:raise ValueError('Expected section: '+name+' '+old[:60])
    path.write_bytes(text.replace(old,new,1).encode('utf8'))
    if name not in FILES:FILES.append(name)
edit('libmscore/CMakeLists.txt','velocitybackup.cpp velocitybackup.h','velocitybackup.cpp velocitybackup.h performancetiming.cpp performancetiming.h')
edit('libmscore/note.cpp','#include "velocitybackup.h"','#include "velocitybackup.h"\n#include "performancetiming.h"')
edit('libmscore/note.cpp','VelocityBackup::forget(this);','VelocityBackup::forget(this);\n      PerformanceTiming::forget(this);')
edit('libmscore/note.cpp','VelocityBackup::copy(&n,this);','VelocityBackup::copy(&n,this);\n      PerformanceTiming::copy(&n,this);')
edit('libmscore/note.cpp','VelocityBackup::write(this,xml);','VelocityBackup::write(this,xml);\n      PerformanceTiming::write(this,xml);')
edit('libmscore/note.cpp','if(VelocityBackup::read(this,e))return true;','if(VelocityBackup::read(this,e))return true;\n      if(PerformanceTiming::read(this,e))return true;')
edit('libmscore/rendermidi.cpp','#include "note.h"','#include "note.h"\n#include "performancetiming.h"')
edit('libmscore/rendermidi.cpp','      if (offTime < onTime)\n','      PerformanceTiming::apply(noteEventOwner,noteEventIndex,onTime,offTime);\n      if (offTime < onTime)\n')
edit('mscore/performanceeditor/performanceeditor.h','class MidiTrackPane;','class MidiTrackPane;\nclass TimingEditor;')
edit('mscore/performanceeditor/performanceeditor.h','      friend class MidiTrackPane;','      friend class TimingEditor;\n      TimingEditor* _timingEditor=nullptr;\n      friend class MidiTrackPane;')
edit('mscore/performanceeditor/performanceeditor.cpp','#include "miditrackpane.h"','#include "miditrackpane.h"\n#include "timingeditor.h"')
edit('mscore/performanceeditor/performanceeditor.cpp','      _midiTracks=new MidiTrackPane(this,noteArea,noteLayout);','      _midiTracks=new MidiTrackPane(this,noteArea,noteLayout);\n      _timingEditor=new TimingEditor(this,noteArea);\n      if(auto row=qobject_cast<QHBoxLayout*>(noteLayout->itemAt(0)->layout()))row->insertWidget(qMax(0,row->count()-1),_timingEditor);\n      connect(writeToggle->defaultAction(),&QAction::toggled,this,[this](bool on){if(on)if(auto button=_timingEditor->findChild<QToolButton*>("performanceTimingToggle"))button->setChecked(false);});')
edit('mscore/performanceeditor/performanceeditor.cmake','if(SCRIPT_INTERFACE)\n','if(SCRIPT_INTERFACE)\n list(APPEND PERFORMANCEEDITOR_SRC ${CMAKE_CURRENT_LIST_DIR}/timingeditor.cpp ${CMAKE_CURRENT_LIST_DIR}/timingeditor.h)\n')
edit('mscore/performanceeditor/performancepainting.cpp','#include "miditrackpane.h"','#include "miditrackpane.h"\n#include "timingeditor.h"')
edit('mscore/performanceeditor/performancepainting.cpp','      if(_midiTracks)_midiTracks->contextChanged();','      if(_midiTracks)_midiTracks->contextChanged();\n      if(_timingEditor)_timingEditor->contextChanged();')
edit('mscore/performanceeditor/performancepainting.cpp','                  painter.setBrush(color); painter.setPen(note.selected ?', '''#ifdef SCRIPT_INTERFACE
                  const bool timing=_timingEditor&&_timingEditor->active();
                  if(timing)color.setAlpha(65);
                  painter.setBrush(timing?QBrush(Qt::NoBrush):QBrush(color));
#else
                  painter.setBrush(color);
#endif
                  painter.setPen(note.selected ?''')
edit('mscore/performanceeditor/performancepainting.cpp','                  if ((_viewport.rowHeight >= 16 && geometry.rect.width() >= 28) || valueInside) {','                  if (\n#ifdef SCRIPT_INTERFACE\n                      !timing &&\n#endif\n                      ((_viewport.rowHeight >= 16 && geometry.rect.width() >= 28) || valueInside)) {')
edit('mscore/performanceeditor/performancepainting.cpp','            if(_midiTracks)_midiTracks->paintNotes(painter,area);','            if(_midiTracks)_midiTracks->paintNotes(painter,area);\n            if(_timingEditor)_timingEditor->paint(painter,area);')
edit('mscore/performanceeditor/performanceinteraction.cpp','#include "miditrackpane.h"','#include "miditrackpane.h"\n#include "timingeditor.h"')
edit('mscore/performanceeditor/performanceinteraction.cpp','      if(_midiTracks&&_midiTracks->handle(event,parameter,ruler))return true;','      if(_midiTracks&&_midiTracks->handle(event,parameter,ruler))return true;\n      if(notes&&_timingEditor&&_timingEditor->handle(event))return true;')
edit('mscore/performanceeditor/performanceinteraction.cpp','            bool midiActive=false;','            bool midiActive=false,timingActive=false;')
edit('mscore/performanceeditor/performanceinteraction.cpp','            midiActive=_midiTracks&&_midiTracks->active();','            midiActive=_midiTracks&&_midiTracks->active();\n            timingActive=notes&&_timingEditor&&_timingEditor->active();')
edit('mscore/performanceeditor/performanceinteraction.cpp','if (!midiActive && !ruler &&','if (!midiActive && !timingActive && !ruler &&')
# Music-source IDs are stored against the master score even when editing a part.
edit('mscore/performanceeditor/miditrackinteraction.cpp','            _source->addItem(tr("谱表%1的音源").arg(staff + 1),\n                             QVariantMap{{"kind", "score-piano"}, {"staff", staff}});','''            {
                auto origin=_editor->_score->staff(staff);
                int masterStaff=staff;
                for(auto linked:origin->staffList())if(linked->score()==_editor->_score->masterScore()){masterStaff=linked->idx();break;}
                _source->addItem(tr("谱表%1的音源").arg(staff + 1),
                                QVariantMap{{"kind", "score-piano"}, {"staff", masterStaff}});
            }''')
edit('mscore/performanceeditor/miditrackinteraction.cpp','#include "libmscore/tempo.h"','#include "libmscore/tempo.h"\n#include "libmscore/staff.h"')
edit('mscore/performanceeditor/miditrackinteraction.cpp','''    _source->setCurrentIndex(
        source.value("kind").toString() == "score-piano"
            ? qBound(1, source.value("staff").toInt() + 1, _source->count() - 1)
            : 0);''','''    const int sourceIndex=_source->findData(source);
    _source->setCurrentIndex(sourceIndex<0?0:sourceIndex);''')
edit('mscore/performanceeditor/performanceeditor.cpp','void PerformanceEditor::completePointerGesture()\n      {','void PerformanceEditor::completePointerGesture()\n      {\n#ifdef SCRIPT_INTERFACE\n      if(_timingEditor)_timingEditor->completeGesture();\n#endif')
record={}
for name in FILES:
    target=HOST/name
    record[name]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
(OUT/'files.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('Prepared',len(FILES),'explicit files')
