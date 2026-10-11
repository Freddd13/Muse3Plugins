#include <QtTest>
#include <QFile>
#include <QTemporaryDir>
#include <QDataStream>
#include "../native/mscore/workflow/referencefactory.h"
class TestFactory:public QObject {
 Q_OBJECT
private slots:
 void lazyLoad(){
  QObject owner;auto media=Ms::createReferenceMedia(&owner);QVERIFY(media);QCOMPARE(media->parent(),&owner);
  if(qEnvironmentVariableIsSet("KUMO_EXPECT_MISSING")){QVERIFY(!media->property("available").toBool());QVERIFY(!media->property("status").toString().isEmpty());return;}
  QVERIFY2(media->property("available").toBool(),qPrintable(media->property("status").toString()));
  QTemporaryDir dir;QFile wav(dir.filePath("fixture.wav"));QVERIFY(wav.open(QIODevice::WriteOnly));
  QDataStream data(&wav);data.setByteOrder(QDataStream::LittleEndian);data.writeRawData("RIFF",4);data<<quint32(36+44100*4);data.writeRawData("WAVEfmt ",8);data<<quint32(16)<<quint16(1)<<quint16(2)<<quint32(44100)<<quint32(176400)<<quint16(4)<<quint16(16);data.writeRawData("data",4);data<<quint32(176400);for(int i=0;i<88200;++i)data<<qint16(0);wav.close();
  QSignalSpy ready(media,SIGNAL(fileReady(QVariantMap)));QVERIFY(ready.isValid());
  QVERIFY(QMetaObject::invokeMethod(media,"open",Q_ARG(QString,wav.fileName())));QTRY_COMPARE(ready.count(),1);QCOMPARE(media->property("duration").toDouble(),1000.);
 }
};
QTEST_GUILESS_MAIN(TestFactory)
#include "tst_factory.moc"
