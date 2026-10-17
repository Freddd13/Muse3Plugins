from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mscore/notepreview.h';s=p.read_text(encoding='utf8').replace('      qreal chordBaseline=0;\n','').replace('chordBaseline==other.chordBaseline && ','').replace('layoutPreviewChord(NotePreviewEntry& entry, int order)','layoutPreviewChord(NotePreviewEntry& entry, int order,qreal chordBaseline=-1)',1).replace('entry.chordBaseline,bBase=', '(chordBaseline>=0?chordBaseline:QFontMetricsF(entry.chordFont).ascent()),bBase=',1);p.write_bytes(s.encode())
p=R/'native/mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf8')
assert 'QHash<QString,NotePreviewEntry> rendered;' in s
s=s.replace('QHash<QString,NotePreviewEntry> rendered;','QHash<QString,NotePreviewEntry> rendered;QHash<QString,qreal> renderedBaselines;',1)
s=s.replace('            if (!entry.chord.isEmpty()) {','            qreal chordBaseline=-1;\n            if (!entry.chord.isEmpty()) {',1)
s=s.replace('glyphs.chordBaseline=-nativeBox.top();','renderedBaselines[renderKey]=-nativeBox.top();',1).replace('entry.chordBaseline=glyphs.chordBaseline;','chordBaseline=renderedBaselines.value(renderKey,-1);',1)
s=s.replace('layoutPreviewChord(entry,qBound(0,value.value("chordOrder").toInt(),3))','layoutPreviewChord(entry,qBound(0,value.value("chordOrder").toInt(),3),chordBaseline)',1)
s=s.replace('if(placed.isEmpty()&&entry.onTop)placed=', 'if(placed.isEmpty())placed=',1)
p.write_bytes(s.encode())
