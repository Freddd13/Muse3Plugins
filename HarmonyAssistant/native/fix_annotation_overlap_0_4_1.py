# -*- coding: utf-8 -*-
"""One-time local source migration: reserve fixed labels and prioritize score editing."""
from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def edit(name,old,new):
    p=repo/name;s=p.read_text(encoding='utf-8');assert old in s,(name,old)
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s.replace(old,new,1))

edit('mscore/plugin/api/scoreobserver.h','class ScoreView;','class ScoreView;\nclass Page;')
edit('mscore/plugin/api/scoreobserver.h','      NotePreviewColors _baseColors;',
     '      NotePreviewColors _baseColors;\n      // Geometry only; page keys are opaque and cleared with the base layer.\n      QHash<const Ms::Page*, QVector<QRectF>> _baseChordBoxes;')
edit('mscore/plugin/api/scoreobserver.cpp','#include "libmscore/chord.h"',
     '#include "libmscore/chord.h"\n#include "libmscore/harmony.h"')
edit('mscore/plugin/api/scoreobserver.cpp','      QHash<const Page*,QVector<QRectF>> occupied;',
     '      QHash<const Page*,QVector<QRectF>> occupied;\n      QHash<const Page*,QVector<QRectF>> chordBoxes;')
edit('mscore/plugin/api/scoreobserver.cpp','                  for (const auto& box : occupied[page])',
'''                  if (owner==this) for (const auto& box : _baseChordBoxes.value(page))
                        if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) return true;
                  for (const auto& box : occupied[page])''')
edit('mscore/plugin/api/scoreobserver.cpp','            entry.degree=value.value("degree").toString().left(24);',
'''            entry.degree=value.value("degree").toString().left(24);
            if (value.value("preferExistingHarmony").toBool() && (!entry.chord.isEmpty() || !entry.degree.isEmpty()))
                  for (const auto annotation : note->chord()->segment()->annotations()) {
                        if (!annotation->visible() || !annotation->isHarmony()
                              || annotation->staff()->part()!=note->staff()->part()) continue;
                        const auto harmony=toHarmony(annotation);
                        if (harmony->harmonyName().trimmed().isEmpty()) continue;
                        if (harmony->harmonyType()==HarmonyType::ROMAN) entry.degree.clear();
                        else entry.chord.clear();
                        }
''')
edit('mscore/plugin/api/scoreobserver.cpp','                              bool collision=!page->bbox().contains(candidate);',
'''                              bool collision=!page->bbox().contains(candidate);
                              if (owner==this) for (const auto& box : _baseChordBoxes.value(page))
                                    if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) {collision=true;break;}''')
edit('mscore/plugin/api/scoreobserver.cpp','                        if (!best[i].isEmpty()) occupied[page].append(best[i]);',
'''                        if (!best[i].isEmpty()) {
                              occupied[page].append(best[i]);chordBoxes[page].append(best[i]);
                              }''')
edit('mscore/plugin/api/scoreobserver.cpp','      if (owner==&_baseOwner) _baseColors=colors;',
     '      if (owner==&_baseOwner) {_baseColors=colors;_baseChordBoxes=chordBoxes;}')
edit('mscore/plugin/api/scoreobserver.cpp','_baseColors.clear(); _previewViews.clear();',
     '_baseColors.clear(); _baseChordBoxes.clear(); _previewViews.clear();')

edit('mscore/scoreview.h','      void drawElements(QPainter& p,QList<Element*>& el, Element* editElement);',
'''      void drawElements(QPainter& p,QList<Element*>& el, Element* editElement);
      QRectF previewEditBounds() const;''')
edit('mscore/scoreview.cpp','void ScoreView::drawElements(QPainter& painter, QList<Element*>& el, Element* editElement)',
'''QRectF ScoreView::previewEditBounds() const
      {
      if (!editData.element || (!editMode() && state!=ViewState::DRAG_OBJECT)) return {};
      const qreal margin=editData.element->spatium();
      return editData.element->canvasBoundingRect().adjusted(-margin,-margin,margin,margin);
      }

void ScoreView::drawElements(QPainter& painter, QList<Element*>& el, Element* editElement)''')
edit('mscore/scoreview.cpp','      std::stable_sort(el.begin(), el.end(), elementLessThan);',
     '      const auto protectedArea=previewEditBounds();\n      std::stable_sort(el.begin(), el.end(), elementLessThan);')
edit('mscore/scoreview.cpp','                        if (box.isEmpty()) return;',
     '                        if (box.isEmpty() || box.translated(e->canvasPos()).intersects(protectedArea)) return;')
edit('mscore/scoreview.cpp','      if (!score()->printing() && !fotoMode()) {\n            _notePreviewLayers.forEachChord',
     '      if (!score()->printing() && !fotoMode()) {\n            const auto protectedArea=previewEditBounds();\n            _notePreviewLayers.forEachChord')
edit('mscore/scoreview.cpp','                  if (!box.intersects(fr)) return;',
     '                  if (!box.intersects(fr) || box.intersects(protectedArea)) return;')
edit('mscore/scoreview.cpp','      { return _notePreviewLayers.activate(canvasPosition); }',
'''      {
      // Native text editing owns double clicks until it ends; hidden overlays must not seize them.
      if (editMode() || state==ViewState::DRAG_OBJECT) return false;
      return _notePreviewLayers.activate(canvasPosition);
      }''')
# The editor refreshes its own box, while a suppressed preview may extend beyond it.
edit('mscore/editelement.cpp','      editData.element->startEdit(editData);',
     '      editData.element->startEdit(editData);\n      if (!_notePreviewLayers.empty()) updateAll();')
edit('mscore/editelement.cpp','      editData.clearData();\n      mscore->updateInspector();',
     '      editData.clearData();\n      if (!_notePreviewLayers.empty()) updateAll();\n      mscore->updateInspector();')

edit('mtest/mscore/pluginhost/tst_pluginhost.cpp','root->version()=="1.2.0"','root->version()=="1.2.1"')
print('Collision reservations, existing notation preference and edit priority added.')
