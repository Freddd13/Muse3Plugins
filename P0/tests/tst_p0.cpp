#include <QtTest>
#include "../native/mscore/taptempo/tapestimate.h"
#include "../native/audio/exports/midigate.h"
using namespace Ms;
class P0ValueTests : public QObject {
      Q_OBJECT
      MidiGateData example() {
            MidiGateData d;
            MidiGateNote n;n.id="a";n.on=0;n.off=960;n.piano=true;n.known=true;n.offOrdinal=2;n.voice=0;n.staff=0;
            d.notes.append(n);d.pedals.append({0,0,0,1200,true});return d;
            }
   private slots:
      void tapStableAndUnits() {
            TapEstimate e;for(int i=0;i<8;++i)QVERIFY(e.add(i*500));
            QVERIFY(e.ready());QVERIFY(e.stable());QCOMPARE(e.bpm(),120.);QCOMPARE(e.bpm(1.5),180.);
            e.reset();for(int i=0;i<4;++i)e.add(i*750);QCOMPARE(e.bpm(1.5),120.);
            }
      void tapOutlierDebounceReset() {
            TapEstimate e;e.add(0);QVERIFY(!e.add(20));for(int i=1;i<6;++i)e.add(i*500);
            e.add(3200);QCOMPARE(e.bpm(),120.);e.add(20000);QCOMPARE(e.count(),1);QVERIFY(!e.ready());
            }
      void tapRollingLimitAndSlowBeat() {
            TapEstimate e;for(int i=0;i<40;++i)e.add(i*3000);QCOMPARE(e.count(),13);QCOMPARE(e.bpm(),20.);
            }
      void gatePedalOnlyAndImmutable() {
            auto d=example();MidiGateOptions o;o.jitter=0;MidiGateProcessor p;
            auto r=p.process(d,o);QVERIFY(r[0].newOff<960);QCOMPARE(d.notes[0].off,960);QCOMPARE(r[0].on,0);
            d.pedals.clear();r=p.process(d,o);QCOMPARE(r[0].newOff,960);
            }
      void gateBoundaryManualAndExclusion() {
            auto d=example();MidiGateOptions o;MidiGateProcessor p;d.pedals[0].up=900;
            QCOMPARE(p.process(d,o)[0].newOff,960);d.pedals[0].up=1200;d.notes[0].manual=true;
            QCOMPARE(p.process(d,o)[0].reason,QString("manual-performance"));d.notes[0].manual=false;o.excluded.insert("a");
            QCOMPARE(p.process(d,o)[0].newOff,960);
            }
      void gateRetriggerAcrossTracks() {
            auto d=example();auto n=d.notes[0];n.id="b";n.track=2;n.on=240;n.off=1000;d.notes.append(n);
            MidiGateProcessor p;auto r=p.process(d,{});QVERIFY(r[0].ambiguous);QVERIFY(r[1].ambiguous);QCOMPARE(r[0].newOff,960);
            }
      void gateSeedAndTempoMinimum() {
            auto d=example();MidiGateProcessor p;MidiGateOptions o;
            auto a=p.process(d,o),b=p.process(d,o);QCOMPARE(a[0].newOff,b[0].newOff);
            d.tempos.append({100,1000000.});o.minimumMs=200.;auto r=p.process(d,o);
            QVERIFY(p.durationMs(r[0].on,r[0].newOff)>=200.);QVERIFY(r[0].newOff<r[0].off);
            }
      void gateCancellationStopsBeforeResults() {
            auto d=example();MidiGateProcessor p;QVERIFY(p.process(d,{},[]{return true;}).isEmpty());
            }
      void gateNextAttackShortNotesUnsupported() {
            auto d=example();auto n=d.notes[0];n.id="b";n.pitch=64;n.on=240;n.off=480;d.notes.append(n);
            MidiGateProcessor p;MidiGateOptions o;o.jitter=0;auto r=p.process(d,o);QVERIFY(r[0].newOff<=240);
            d.pedals[0].supported=false;QCOMPARE(p.process(d,o)[0].newOff,960);
            d.notes[0].off=30;QCOMPARE(p.process(d,o)[0].newOff,30);
            }
      };
QTEST_GUILESS_MAIN(P0ValueTests)
#include "tst_p0.moc"
