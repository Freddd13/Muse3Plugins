# -*- coding: utf-8 -*-
"""One-time source lifetime regression for markers sharing one sustained note."""
from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\scoreobserver\tst_scoreobserver.cpp')
s=p.read_text(encoding='utf-8')
needle='      void fixedMarkerHighlightPerformance()'
addition='''      void multipleChangesOnOneSustainedNote()
            {
            NotePreviewLayers layers;QObject owner;
            const auto source=reinterpret_cast<const Element*>(quintptr(1));
            NotePreviewEntry first;first.sourceAnchor=source;first.chord="C";
            first.chordTick=0;first.chordUntil=240;first.chordBox=QRectF(10,10,40,20);first.bounds=first.chordBox;
            auto second=first;second.chord="Am";second.chordTick=240;second.chordUntil=480;
            second.chordBox.translate(60,0);second.bounds=second.chordBox;second.chordMask=false;
            const NotePreviewMarkers markers{first,second};
            layers.replace(&owner,{{source,{Qt::red,QRectF(10,40,10,10)}}},markers);
            layers.setActiveChord(&owner,240);
            int count=0,active=-1;
            layers.forEachChord([&](const NotePreviewEntry& entry,bool enabled){++count;if(enabled)active=entry.chordTick;});
            QCOMPARE(count,2);QCOMPARE(active,240);QCOMPARE(layers.color(source),QColor(Qt::red));
            QVERIFY(layers.replace(&owner,{{source,{Qt::red,QRectF(10,40,10,10)}}},markers).isEmpty());
            layers.remove(source);count=0;
            layers.forEachChord([&](const NotePreviewEntry&,bool){++count;});
            QCOMPARE(count,0);QVERIFY(!layers.color(source).isValid());
            // Removal compares opaque identities only: source is deliberately not dereferenceable.
            }
'''
assert needle in s;s=s.replace(needle,addition+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Shared sustained source marker regression added.')
