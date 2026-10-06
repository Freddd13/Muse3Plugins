# -*- coding: utf-8 -*-
"""One-time test additions for 0.4."""
from pathlib import Path
R=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
HERE=Path(__file__).resolve().parent
def write(name,value):
    with (R/name).open('w',encoding='utf-8',newline='\n') as f:f.write(value)
# Highlight is a separate small set; never detach/copy the immutable full-score color map during playback.
write('mscore/notepreview.h',(HERE/'notepreview-0.4.h.inc').read_text(encoding='utf-8'))
p=R/'mscore/scoreview.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('[&](const NotePreviewEntry& entry) {','[&](const NotePreviewEntry& entry, bool active) {')
s=s.replace('entry.chordActive ?','active ?');write('mscore/scoreview.cpp',s)
p=R/'mtest/mscore/scoreobserver/tst_scoreobserver.cpp';s=p.read_text(encoding='utf-8')
needle='      void longScorePerformance()'
test='''      void fixedMarkerHighlightAndStyle()
            {
            NotePreviewLayers layers; QObject owner;
            const auto first=reinterpret_cast<const Element*>(quintptr(1));
            const auto second=reinterpret_cast<const Element*>(quintptr(2));
            NotePreviewEntry entry;
            entry.chord="Cmaj7";entry.degree="Imaj7";entry.spatium=5;
            entry.chordFont=QFont("Arial");entry.chordFont.setPixelSize(12);
            entry.degreeFont=entry.chordFont;
            const auto horizontal=layoutPreviewChord(entry,0);
            QVERIFY(entry.primaryBox.left()<entry.secondaryBox.left());
            layoutPreviewChord(entry,1);QVERIFY(entry.primaryBox.left()>entry.secondaryBox.left());
            const auto vertical=layoutPreviewChord(entry,2);
            QVERIFY(entry.primaryBox.top()<entry.secondaryBox.top());
            QVERIFY(vertical.height()>horizontal.height());
            layoutPreviewChord(entry,3);QVERIFY(entry.primaryBox.top()>entry.secondaryBox.top());
            entry.chordBox=QRectF(10,10,70,20);entry.bounds=entry.chordBox;
            entry.chordTick=0;entry.chordUntil=960;
            NotePreviewColors base {{first,entry}};
            entry.chordTick=960;entry.chordUntil=1440;entry.chordBox.translate(100,0);entry.bounds=entry.chordBox;
            base.insert(second,entry);layers.replace(&owner,base);
            int activeTick=-1,count=0;
            auto inspect=[&]() {activeTick=-1;count=0;layers.forEachChord([&](const NotePreviewEntry& value,bool active){
                  QCOMPARE(value.chordBox.top(),qreal(10));++count;if(active)activeTick=value.chordTick;});};
            QVERIFY(!layers.setActiveChord(&owner,480).isEmpty());inspect();QCOMPARE(activeTick,0);QCOMPARE(count,2);
            QVERIFY(layers.setActiveChord(&owner,720).isEmpty());
            layers.setActiveChord(&owner,960);inspect();QCOMPARE(activeTick,960);
            // A current note/function layer must not cover the fixed chord underneath.
            QObject foreground;layers.replace(&foreground,{{second,{Qt::blue,QRectF(100,30,20,20)}}});
            inspect();QCOMPARE(count,2);QCOMPARE(activeTick,960);
            layers.setActiveChord(&owner,1440);inspect();QCOMPARE(activeTick,-1);
            layers.remove(first);inspect();QCOMPARE(count,1);
            }
      void fixedMarkerHighlightPerformance()
            {
            NotePreviewLayers layers;QObject owner;NotePreviewColors colors;
            for(int i=0;i<6000;++i) {
                  NotePreviewEntry entry;entry.color=Qt::blue;entry.bounds=QRectF(i,30,2,2);
                  if(i%6==0){entry.chord="C";entry.chordBox=QRectF(i,10,10,8);entry.chordTick=i*80;entry.chordUntil=(i+6)*80;}
                  colors.insert(reinterpret_cast<const Element*>(quintptr(i+1)),entry);
                  }
            layers.replace(&owner,colors);QElapsedTimer timer;timer.start();
            for(int i=0;i<1000;++i)layers.setActiveChord(&owner,i*480);
            qInfo("6000 notes / 1000 fixed markers: 1000 indexed highlight changes %.3f ms",double(timer.nsecsElapsed())/1000000.0);
            }
'''
assert needle in s;s=s.replace(needle,test+needle,1);write('mtest/mscore/scoreobserver/tst_scoreobserver.cpp',s)
p=R/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8').replace('root->version()=="1.1.0"','root->version()=="1.2.0"')
needle='            observer->clearAllPreviews();QTest::qWait(30);'
extension='''            // Native fixed label hit testing must emit to its owning observer.
            auto anchor=descriptors.front().toMap();anchor["chord"]="Cmaj13";anchor["degree"]="Imaj13";
            anchor["chordTick"]=480;anchor["chordUntil"]=960;anchor["chordOrder"]=2;
            observer->setScorePreview({anchor});observer->setActiveScorePreview(600);
            QSignalSpy activation(observer,&PluginAPI::ScoreObserver::previewActivated);
            // Locate the fixed row through a separate generic layer with known hit geometry.
            NotePreviewLayers interaction;QObject interactionOwner;
            NotePreviewEntry hit;hit.chord="C";hit.chordBox=QRectF(10,10,40,20);hit.chordTick=480;hit.activationTarget=observer;
            interaction.replace(&interactionOwner,{{nullptr,hit}});
            QVERIFY(interaction.activate(QPointF(20,20)));QCOMPARE(activation.size(),1);
            QVERIFY(!interaction.activate(QPointF(90,90)));
            // The panel jump keeps dock placement; top docks open their full detail tool window.
            QVERIFY(QMetaObject::invokeMethod(panel,"openAnnotation",Q_ARG(QVariant,480),Q_ARG(QVariant,0)));
            auto editor=panel->findChild<QObject*>("harmonyConfiguration");QVERIFY(editor);
            QVERIFY(QMetaObject::invokeMethod(editor,"openColor",Q_ARG(QVariant,QString()),Q_ARG(QVariant,QString("chordColor")),Q_ARG(QVariant,QString("#ffee99"))));
            QTest::qWait(50);
            auto picker=editor->findChild<QObject*>("harmonyColorPicker");QVERIFY(picker);
            picker->setProperty("color",QColor("#224466"));
            QVERIFY(QMetaObject::invokeMethod(picker,"accept"));QTest::qWait(30);
'''
assert needle in s;s=s.replace(needle,extension+needle,1);write('mtest/mscore/pluginhost/tst_pluginhost.cpp',s)
print('Fixed annotation regressions added')
