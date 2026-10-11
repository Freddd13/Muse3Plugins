#include <QtTest>
#include <QTemporaryDir>
#include <QFile>
#include "../native/mscore/workflow/midiinput.h"
class TestMidiInput:public QObject {
 Q_OBJECT
 QTemporaryDir dir;
 QString write(const QByteArray& track,int division=480){
  QByteArray bytes=QByteArray::fromHex("4d5468640000000600000001");bytes.append(char(division>>8));bytes.append(char(division));bytes.append("MTrk");int size=track.size();for(int i=3;i>=0;--i)bytes.append(char(size>>(i*8)));bytes.append(track);
  QString path=dir.filePath(QUuid::createUuid().toString()+".mid");QFile file(path);if(!file.open(QIODevice::WriteOnly))return {};file.write(bytes);return path;
 }
private slots:
 void runningStatusTempoAndControls(){
  auto path=write(QByteArray::fromHex("00903c5081703c408170803c0000ff51030f42408360b0407f00903e6000803c008360803e0000ff2f00"));
  std::atomic_bool cancel{false};auto r=Ms::readPerformanceMidi(path,cancel);QVERIFY2(!r.contains("error"),qPrintable(r["error"].toString()));auto notes=r["notes"].toList();QCOMPARE(notes.size(),3);
  QCOMPARE(notes[0].toMap()["velocity"].toInt(),80);QVERIFY(notes[0].toMap()["ambiguous"].toBool());QVERIFY(notes[1].toMap()["ambiguous"].toBool());
  QCOMPARE(notes[2].toMap()["seconds"].toDouble(),1.5);QCOMPARE(notes[2].toMap()["endSeconds"].toDouble(),2.5);QCOMPARE(r["sha256"].toString().size(),64);QVERIFY(r["events"].toList().size()>notes.size());
 }
 void smpte(){auto path=write(QByteArray::fromHex("00903c508360803c0000ff2f00"),int(0xe728));std::atomic_bool c{false};auto r=Ms::readPerformanceMidi(path,c);QVERIFY(!r.contains("error"));QCOMPARE(r["notes"].toList()[0].toMap()["endSeconds"].toDouble(),.48);}
 void invalidAndCanceled(){std::atomic_bool c{false};auto path=write(QByteArray::fromHex("003c5000ff2f00"));QVERIFY(Ms::readPerformanceMidi(path,c).contains("error"));c=true;QVERIFY(Ms::readPerformanceMidi(path,c).contains("error"));}
 void releaseVelocityZero(){auto path=write(QByteArray::fromHex("00903c4083603c0000ff2f00"));std::atomic_bool c{false};auto r=Ms::readPerformanceMidi(path,c);QVERIFY(!r.contains("error"));auto n=r["notes"].toList()[0].toMap();QCOMPARE(n["off"].toInt(),480);QVERIFY(!n["unreleased"].toBool());}
};
QTEST_GUILESS_MAIN(TestMidiInput)
#include "tst_midiinput.moc"
