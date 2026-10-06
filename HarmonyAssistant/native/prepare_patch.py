from pathlib import Path
import difflib
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
base=Path('HarmonyAssistant/native')
changes={}
def change(path, old, new):
 text=changes.get(path,(repo/path).read_text(encoding='utf-8'))
 assert old in text, (path,old)
 changes[path]=text.replace(old,new,1)
change('libmscore/note.h','      void draw(QPainter*) const override;','      void draw(QPainter*) const override;\n      void draw(QPainter*, const QColor& screenColor) const;')
change('libmscore/note.cpp','void Note::draw(QPainter* painter) const\n      {\n      if (_hidden)','''void Note::draw(QPainter* painter) const
      {
      draw(painter, curColor());
      }

// Explicit color is used by screen-only preview layers; normal export retains curColor().
void Note::draw(QPainter* painter, const QColor& screenColor) const
      {
      if (_hidden)''')
change('libmscore/note.cpp','      QColor c(curColor());','      const QColor& c = screenColor;')
change('mscore/scoreview.h','#include "fotomode.h"','#include "fotomode.h"\n#include "notepreview.h"')
change('mscore/scoreview.h','      EditData editData;','      NotePreviewLayers _notePreviewLayers;\n      QSet<QObject*> _notePreviewOwners;\n\n      EditData editData;')
change('mscore/scoreview.h','      void onElementDestruction(Element*) override;','      void onElementDestruction(Element*) override;\n      void setNotePreviewColors(QObject* owner, const NotePreviewColors& colors);')
change('mscore/scoreview.cpp','void ScoreView::setScore(Score* s)\n      {','void ScoreView::setScore(Score* s)\n      {\n      _notePreviewLayers.clear();')
change('mscore/scoreview.cpp','            e->draw(&painter);\n            painter.translate(-pos);','''            const QColor preview = !_notePreviewLayers.empty() && e->isNote()
                  && !score()->printing() && !fotoMode()
                  ? _notePreviewLayers.color(toNote(e)) : QColor();
            if (preview.isValid()) {
                  const auto note = toNote(e);
                  const bool editingSelection = note->selected() && !score()->isPlaying();
                  note->draw(&painter, editingSelection || !note->visible()
                        ? note->curColor() : preview);
                  // Retain a distinct native playback mark without hiding the role color.
                  if (note->mark()) {
                        painter.save();
                        painter.setPen(QPen(note->curColor(), score()->spatium() * 0.08));
                        const QRectF box = note->bbox();
                        painter.drawLine(box.bottomLeft(), box.bottomRight());
                        painter.restore();
                        }
                  }
            else e->draw(&painter);
            painter.translate(-pos);''')
change('mscore/scoreview.cpp','void ScoreView::onElementDestruction(Element* e)\n      {','''void ScoreView::setNotePreviewColors(QObject* owner, const NotePreviewColors& colors)
      {
      if (!owner) return;
      if (!_notePreviewOwners.contains(owner) && !colors.isEmpty()) {
            _notePreviewOwners.insert(owner);
            connect(owner, &QObject::destroyed, this, [this, owner]() {
                  _notePreviewOwners.remove(owner);
                  const QRectF dirty = _notePreviewLayers.replace(owner, {});
                  if (!dirty.isEmpty()) dataChanged(dirty);
                  });
            }
      const QRectF dirty = _notePreviewLayers.replace(owner, colors);
      if (!dirty.isEmpty()) dataChanged(dirty);
      }

void ScoreView::onElementDestruction(Element* e)
      {
      if (e->isNote()) _notePreviewLayers.remove(toNote(e));''')
change('mscore/plugin/plugin.cmake','    ${CMAKE_CURRENT_LIST_DIR}/api/score.cpp','    ${CMAKE_CURRENT_LIST_DIR}/api/scoreobserver.cpp\n    ${CMAKE_CURRENT_LIST_DIR}/api/scoreobserver.h\n    ${CMAKE_CURRENT_LIST_DIR}/api/score.cpp')
change('mscore/plugin/api/qmlpluginapi.h','      Q_INVOKABLE Ms::PluginAPI::MsProcess* newQProcess();','      Q_INVOKABLE Ms::PluginAPI::MsProcess* newQProcess();\n      Q_INVOKABLE QObject* newScoreObserver();')
change('mscore/plugin/api/qmlpluginapi.cpp','#include "score.h"','#include "score.h"\n#include "scoreobserver.h"')
change('mscore/plugin/api/qmlpluginapi.cpp','MsProcess* PluginAPI::newQProcess()','''QObject* PluginAPI::newScoreObserver()
      {
      // Parent to the plugin instance: destruction removes every screen preview layer.
      return new ScoreObserver(this);
      }

MsProcess* PluginAPI::newQProcess()''')
patch=[]
for path,new in changes.items():
 old=(repo/path).read_text(encoding='utf-8')
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
for local,target in [('scoreobserver.h','mscore/plugin/api/scoreobserver.h'),('scoreobserver.cpp','mscore/plugin/api/scoreobserver.cpp'),('notepreview.h','mscore/notepreview.h')]:
 new=(base/local).read_text(encoding='utf-8')
 patch.extend(difflib.unified_diff([],new.splitlines(True),fromfile='/dev/null',tofile='b/'+target))
(base/'score-observer.patch').write_bytes(''.join(patch).encode('utf-8'))
print('Prepared native observer and rendering patch:',len(changes),'existing files, 3 isolated new files')
