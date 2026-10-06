# -*- coding: utf-8 -*-
"""One-time 0.3 -> 0.4 native migration, never an installer."""
from pathlib import Path
R=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
HERE=Path(__file__).resolve().parent
def write(name,value):
    with (R/name).open('w',encoding='utf-8',newline='\n') as f:f.write(value)
def replace(name,old,new):
    text=(R/name).read_text(encoding='utf-8');assert old in text,name;write(name,text.replace(old,new,1))
write('mscore/notepreview.h',(HERE/'notepreview-0.4.h.inc').read_text(encoding='utf-8'))
replace('mscore/scoreview.h','      void setNotePreviewColors(QObject* owner, const NotePreviewColors& colors);','      void setNotePreviewColors(QObject* owner, const NotePreviewColors& colors);\n      void setActiveNotePreview(QObject* owner, int tick);\n      bool activateNotePreview(const QPointF& canvasPosition);')
replace('mscore/events.cpp','void ScoreView::mouseDoubleClickEvent(QMouseEvent* mouseEvent)\n      {','''void ScoreView::mouseDoubleClickEvent(QMouseEvent* mouseEvent)
      {
      if (mouseEvent->button()==Qt::LeftButton && !fotoMode() && activateNotePreview(toLogical(mouseEvent->pos()))) {
            mouseEvent->accept();return;
            }''')
text=(R/'mscore/scoreview.cpp').read_text(encoding='utf-8')
text=text.replace('                  drawLabel(previewEntry->chord, previewEntry->chordBox, true);','')
needle='      if (dropRectangle.isValid())\n'
assert needle in text
text=text.replace(needle,'''      if (!score()->printing() && !fotoMode()) {
            _notePreviewLayers.forEachChord([&](const NotePreviewEntry& entry) {
                  const auto box=entry.chordBox.translated(entry.anchor);
                  if (!box.intersects(fr)) return;
                  p.save();p.translate(box.topLeft());
                  p.setPen(Qt::NoPen);
                  p.setBrush(entry.chordActive ? entry.highlightBackground : QColor(255,255,255,235));
                  p.drawRoundedRect(QRectF(QPointF(),box.size()),entry.spatium*.18,entry.spatium*.18);
                  p.setPen(entry.chordActive ? entry.highlightColor : entry.chordColor);
                  p.setFont(entry.chordFont);p.drawText(entry.primaryBox,Qt::AlignCenter,entry.chord);
                  p.setFont(entry.degreeFont);p.drawText(entry.secondaryBox,Qt::AlignCenter,entry.degree);
                  p.restore();
                  });
            }
''' + needle,1)
needle='void ScoreView::onElementDestruction(Element* e)'
text=text.replace(needle,'''void ScoreView::setActiveNotePreview(QObject* owner, int tick)
      {
      const auto dirty=_notePreviewLayers.setActiveChord(owner,tick);
      if (!dirty.isEmpty()) dataChanged(dirty);
      }
bool ScoreView::activateNotePreview(const QPointF& canvasPosition)
      { return _notePreviewLayers.activate(canvasPosition); }

''' + needle,1)
write('mscore/scoreview.cpp',text)
replace('mscore/plugin/api/scoreobserver.h','      QObject _baseOwner;','      QObject _baseOwner;\n      int _activePreviewTick = -1;')
replace('mscore/plugin/api/scoreobserver.h','      Q_INVOKABLE void setScorePreview(const QVariantList& notes);','''      Q_INVOKABLE void setScorePreview(const QVariantList& notes);
      Q_INVOKABLE void setActiveScorePreview(int tick);
      Q_INVOKABLE void activatePreview(int tick, int track) { emit previewActivated(tick, track); }''')
replace('mscore/plugin/api/scoreobserver.h','      void positionChanged();','      void positionChanged();\n      void previewActivated(int tick, int track);')
text=(R/'mscore/plugin/api/scoreobserver.cpp').read_text(encoding='utf-8')
a=text.index('void ScoreObserver::applyPreview(');b=text.index('void ScoreObserver::setNotePreviewColors(',a)
text=text[:a]+(HERE/'preview-apply-0.4.cpp.inc').read_text(encoding='utf-8')+'\n'+text[b:]
text=text.replace('#include <QUrl>','#include <QUrl>\n#include <QtMath>\n#include <climits>')
text=text.replace('clearPreview(this); clearPreview(&_baseOwner); _baseColors.clear(); _previewViews.clear();','clearPreview(this); clearPreview(&_baseOwner); _baseColors.clear(); _previewViews.clear(); _activePreviewTick=-1;')
write('mscore/plugin/api/scoreobserver.cpp',text)
replace('mscore/plugin/qmlplugin.h','      Q_INVOKABLE void setPanelFloating(bool floating);','      Q_INVOKABLE void setPanelFloating(bool floating);\n      Q_INVOKABLE void focusPanel();')
replace('mscore/plugin/qmlplugin.cpp','bool QmlPlugin::panelFloating() const','''void QmlPlugin::focusPanel()
      {
      if (!_panelDock) return;
      _panelDock->show();_panelDock->raise();_panelDock->activateWindow();
      if (_panelDock->widget()) _panelDock->widget()->setFocus(Qt::OtherFocusReason);
      }
bool QmlPlugin::panelFloating() const''')
print('Native fixed annotations, indexed highlight and focus bridge applied')
