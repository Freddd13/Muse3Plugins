# -*- coding: utf-8 -*-
from pathlib import Path
stage=Path(__file__).resolve().parent/'next-1.4'
def edit(name,changes):
    p=stage/name;s=p.read_text(encoding='utf-8')
    for old,new in changes:
        assert old in s,(name,old[:80]);s=s.replace(old,new,1)
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
edit('mscore/scoreview.cpp',[(
'''                  const bool editingSelection = note->selected() && !score()->isPlaying();
                  note->draw(&painter, editingSelection || !note->visible()
                        ? note->curColor() : preview);
                  // Retain a distinct native playback mark without hiding the role color.
                  if (note->mark()) {
                        painter.save();
                        painter.setPen(QPen(note->curColor(), score()->spatium() * 0.08));
                        const QRectF box = note->bbox();
                        painter.drawLine(box.bottomLeft(), box.bottomRight());
                        painter.restore();
                        }''',
'''                  // Resolve every native state (playback, selection, drop, invisible) first.
                  // Only the ordinary color is replaced; curColor remains the authority.
                  note->draw(&painter, note->curColor(note->visible(),preview));'''),(
'''                  p.setFont(entry.chordFont);p.drawText(entry.primaryBox,Qt::AlignCenter,entry.chord);''',
'''                  if (!entry.chordPicture.isNull()) {
                        p.save();p.translate(entry.primaryBox.topLeft());
                        p.drawPicture(QPointF(),active ? entry.activeChordPicture : entry.chordPicture);p.restore();
                        }
                  else {p.setFont(entry.chordFont);p.drawText(entry.primaryBox,Qt::AlignCenter,entry.chord);}''')])
edit('mscore/events.cpp',[(
'''void ScoreView::mousePressEvent(QMouseEvent* ev)
      {
''',
'''void ScoreView::mousePressEvent(QMouseEvent* ev)
      {
      if (ev->button()==Qt::LeftButton && ev->modifiers()==Qt::NoModifier && !fotoMode()
            && state==ViewState::NORMAL && activateNotePreview(toLogical(ev->pos()))) {
            ev->accept();return;
            }
''')])
edit('mscore/notepreview.h',[(
'#include <QFontMetricsF>', '#include <QFontMetricsF>\n#include <QPicture>'),(
'      QFont chordFont;',
'''      QPicture chordPicture;
      QPicture activeChordPicture;
      QSizeF renderedChordSize;
      QString renderedChordKey;
      QFont chordFont;'''),(
'                  && chordFont == other.chordFont && degreeFont == other.degreeFont',
'''                  && renderedChordKey == other.renderedChordKey && renderedChordSize == other.renderedChordSize
                  && chordFont == other.chordFont && degreeFont == other.degreeFont'''),(
'      const auto a = size(entry.chord, entry.chordFont), b = size(entry.degree, entry.degreeFont);',
'      const auto a = entry.renderedChordSize.isEmpty() ? size(entry.chord, entry.chordFont) : entry.renderedChordSize, b = size(entry.degree, entry.degreeFont);')])
edit('mscore/plugin/api/scoreobserver.h',[(
'      Q_INVOKABLE void setActiveScorePreview(int tick);',
'''      Q_INVOKABLE void setActiveScorePreview(int tick);
      Q_INVOKABLE QVariantMap previewStatus() const { return property("previewStatus").toMap(); }''')])
edit('mscore/plugin/api/scoreobserver.cpp',[(
'#include <QFontMetricsF>', '#include <QFontMetricsF>\n#include <QFontInfo>\n#include <QPainter>\n#include <memory>'),(
'      if (!eventPitch) result.insert("tpc", note->tpc1());',
'''      auto attack=note;
      QSet<const Ms::Note*> visited;
      while (attack->tieBack() && attack->tieBack()->startNote() && !visited.contains(attack)) {
            visited.insert(attack);attack=attack->tieBack()->startNote();
            }
      result.insert("attackTick",attack->chord()->tick().ticks());
      if (!eventPitch) result.insert("tpc", note->tpc1());'''),(
'      result.insert("analysisNotes", context);',
'''      result.insert("analysisNotes", context);
      QVariantList parts,windows;
      for (const auto part:_score->parts()) if (part->startTrack()<endTrack && part->endTrack()>firstTrack)
            parts.append(QVariantMap{{"startTrack",part->startTrack()},{"endTrack",part->endTrack()}});
      for (const auto& window:_pedals) if (window.firstTrack<endTrack && window.endTrack>firstTrack)
            windows.append(QVariantMap{{"start",window.start},{"end",window.end},{"firstTrack",window.firstTrack},{"endTrack",window.endTrack}});
      result.insert("parts",parts);result.insert("pedalWindows",windows);
      result.insert("scoreEnd",_score->lastMeasure() ? _score->lastMeasure()->endTick().ticks() : 0);'''),(
'      QHash<const System*,QMap<int,QVector<int>>> groups;',
'''      QHash<const System*,QMap<int,QVector<int>>> groups;
      // Private style/chord list: parsing unknown symbols must not modify the user's score.
      std::unique_ptr<Ms::MasterScore> scratch;
      QHash<QString,NotePreviewEntry> rendered;
      int hidden=0;QString fontFallback;'''),(
'''            entry.chordFont=QFont(family);entry.chordFont.setPixelSize(qMax(5,qRound(sp*1.65*scale)));
            entry.chordFont.setLetterSpacing(QFont::AbsoluteSpacing,-sp*.02);
            entry.degreeFont=QFont("Arial");entry.degreeFont.setPixelSize(qMax(5,qRound(sp*1.45*scale)));''',
'''            entry.chordFont=QFont(family);entry.chordFont.setPointSizeF(_score->styleD(Sid::chordSymbolAFontSize)*scale);
            QString degreeFamily=value.value("degreeFont","Arial").toString().left(64);
            entry.degreeFont=QFont(degreeFamily);entry.degreeFont.setPixelSize(qMax(5,qRound(sp*1.45*scale)));
            const QFontInfo resolved(entry.chordFont);
            if (resolved.family().compare(family,Qt::CaseInsensitive)!=0) fontFallback=resolved.family();'''),(
'            entry.chordBox=QRectF(QPointF(),layoutPreviewChord(entry,qBound(0,value.value("chordOrder").toInt(),3)));',
'''            if (!entry.chord.isEmpty()) {
                  const QString renderKey=entry.chord+"\\t"+family+"\\t"+QString::number(scale,'g',12)+"\\t"
                        +entry.chordColor.name()+entry.highlightColor.name();
                  if (!rendered.contains(renderKey)) {
                        if (!scratch) scratch=std::make_unique<Ms::MasterScore>(_score->style());
                        Harmony harmony(scratch.get());
                        if (!value.value("chordFont").toString().isEmpty()) harmony.setProperty(Pid::FONT_FACE,family);
                        harmony.setProperty(Pid::FONT_SIZE,_score->styleD(Sid::chordSymbolAFontSize)*scale);
                        harmony.setHarmony(entry.chord);harmony.calculateBoundingRect();
                        const auto nativeBox=harmony.bbox();
                        NotePreviewEntry glyphs;glyphs.renderedChordSize=nativeBox.size();glyphs.renderedChordKey=renderKey;
                        auto record=[&](const QColor& color,QPicture& picture) {
                              harmony.setColor(color);QPainter painter(&picture);painter.translate(-nativeBox.topLeft());
                              static_cast<const Element&>(harmony).draw(&painter);painter.end();
                              };
                        record(entry.chordColor,glyphs.chordPicture);record(entry.highlightColor,glyphs.activeChordPicture);
                        rendered.insert(renderKey,glyphs);
                        }
                  const auto& glyphs=rendered[renderKey];entry.chordPicture=glyphs.chordPicture;
                  entry.activeChordPicture=glyphs.activeChordPicture;entry.renderedChordSize=glyphs.renderedChordSize;
                  entry.renderedChordKey=glyphs.renderedChordKey;
                  }
            entry.chordBox=QRectF(QPointF(),layoutPreviewChord(entry,qBound(0,value.value("chordOrder").toInt(),3)));''')])
# Replace whole-group lane selection with greedy local lanes and real height spacing.
p=stage/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
a=s.index('                  QVector<QRectF> best;int bestCount=-1;');b=s.index('\n                  }\n            }\n      if (owner==&_baseOwner)',a)
s=s[:a]+'''                  for (int index:group) {
                        auto& entry=markers[index];QRectF placed;
                        for (int lane=0;lane<6;++lane) {
                              const QRectF candidate(positions[index].x(),top-lane*(height+sp*.5),entry.chordBox.width(),height);
                              bool collision=!page->bbox().contains(candidate);
                              for (const auto& box:occupied[page])
                                    if (box.adjusted(-sp*.15,-sp*.12,sp*.15,sp*.12).intersects(candidate)){collision=true;break;}
                              if (!collision) for (const auto element:page->items(candidate)) {
                                    if (!element->visible() || element->isStaffLines() || element->isPage() || element->isSystem() || element->isMeasure()) continue;
                                    if (element->pageBoundingRect().adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)){collision=true;break;}
                                    }
                              if (!collision){placed=candidate;break;}
                              }
                        entry.chordBox=placed.isEmpty() ? QRectF() : placed.translated(-positions[index]);
                        if (placed.isEmpty()) ++hidden;
                        else {occupied[page].append(placed);chordBoxes[page].append(placed);}
                        entry.bounds=entry.chordBox.isEmpty() ? QRectF() : entry.chordBox.translated(entry.anchor);
                        }
''' + s[b:]
s=s.replace('      if (owner==&_baseOwner){_baseColors=colors;_baseChordBoxes=chordBoxes;}',
'''      if (owner==&_baseOwner){_baseColors=colors;_baseChordBoxes=chordBoxes;
            setProperty("previewStatus",QVariantMap{{"hidden",hidden},{"fontFallback",fontFallback}});}''',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
