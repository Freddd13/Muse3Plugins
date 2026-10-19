// SPDX-License-Identifier: GPL-2.0-or-later
#include "audio/vst/plugin.h"
#include "audio/vst/rack.h"
#include <QApplication>
#include <QCoreApplication>
#include <QFile>
#include <QJsonDocument>
#include <QDataStream>
#include <QProcess>
#include <QTest>
#include <algorithm>
#include <cmath>
using namespace Ms::VstHost;
class Checks : public QObject {
  Q_OBJECT
  QVariantMap effect;
  QString helper() const {
    return QCoreApplication::applicationDirPath() + "/MuseScoreVstHost.exe";
  }
  QVariantMap scan(const QString &path) {
    QProcess p;
    p.start(helper(), {"--scan", path});
    if (!p.waitForFinished(60000))
      return {{"error", "timeout"}};
    return QJsonDocument::fromJson(p.readAllStandardOutput())
        .toVariant()
        .toMap();
  }
private Q_SLOTS:
  void ariaSerializationCounterKeepsSoundChanges() {
    auto configuration = [](int counter, double volume, const QString& vendor) {
      const auto xml = QString("<AriaSave productID=\"1016\"><Settings sc=\"%1\" quality=\"1\"/>"
                               "<Slot id=\"0\" sc=\"%1\"><Main value=\"%2\"/></Slot>"
                               "<EffectSlot id=\"0\" sc=\"%1\"/></AriaSave>")
                           .arg(counter).arg(volume).toUtf8();
      QByteArray chunk("CEGP", 4);
      QDataStream length(&chunk, QIODevice::Append);
      length.setByteOrder(QDataStream::LittleEndian);
      length << quint32(xml.size());
      chunk += qCompress(xml).mid(4);
      const auto state = QJsonDocument::fromVariant(
          QVariantMap{{"chunk", QString::fromLatin1(chunk.toBase64())}}).toJson(QJsonDocument::Compact);
      const QVariantMap source{{"plugin", QVariantMap{{"format", "VST2"}, {"vendor", vendor}}},
                               {"state", QString::fromLatin1(state.toBase64())}};
      return QVariantMap{{"slots", QVariantList{QVariantMap{{"source", source}}}}};
    };
    const auto original = configuration(1, .75, "Garritan");
    const auto copy = original;
    QVERIFY(sameConfiguration(original, configuration(2, .75, "Garritan")));
    QVERIFY(!sameConfiguration(original, configuration(2, .25, "Garritan")));
    QVERIFY(!sameConfiguration(configuration(1, .75, "Other"), configuration(2, .75, "Other")));
    QCOMPARE(original, copy);
  }
  void initTestCase() {
    auto r =
        scan(QCoreApplication::applicationDirPath() + "/KumoTestEffect.dll");
    QVERIFY2(r["error"].toString().isEmpty(),
             qPrintable(r["error"].toString()));
    QCOMPARE(r["plugins"].toList().size(), 1);
    effect = r["plugins"].toList()[0].toMap();
    QVERIFY(!effect["instrument"].toBool());
  }
  void effectAndPreset() {
    QString error;
    auto p = create(Descriptor::fromValue(effect), &error);
    QVERIFY2(p && p->prepare(44100, 256, &error), qPrintable(error));
    float l[256]{}, r[256]{}, ol[256]{}, orr[256]{};
    l[0] = 1;
    r[0] = .5;
    Clock clock;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], .5f);
    QCOMPARE(orr[32], .25f);
    QCOMPARE(p->latency(), 32);
    auto state = p->state(&error);
    QVERIFY(!state.isEmpty());
    p->setParameter(0, .25);
    QVERIFY(p->process(0, l, r, ol, orr, nullptr, 0, clock));
    QVERIFY(p->restore(state, &error));
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], .5f);
  }
  void serialEffectsAndBypass() {
    for (bool bypass : {false, true}) {
      Rack rack(true);
      QStringList problems;
      QVariantMap u{{"plugin", effect}, {"bypass", bypass}};
      rack.load({{"masterEffects", QVariantList{u, u}}}, 44100, &problems);
      QVERIFY2(problems.isEmpty(), qPrintable(problems.join('\n')));
      float data[512]{};
      data[0] = 1;
      Clock c;
      c.offline = true;
      rack.mix(256, data, c);
      rack.master(256, data, c);
      QCOMPARE(rack.latency(), 64);
      QCOMPARE(data[128], bypass ? 1.f : .25f);
      for (int i = 0; i < 512; ++i)
        if (i != 128)
          QCOMPARE(data[i], 0.f);
      auto saved = rack.state();
      rack.load(saved, 44100, &problems);
      QVERIFY(problems.isEmpty());
    }
  }
  void separateProcessOffline() {
    QString error;
    auto p = createIsolated(Descriptor::fromValue(effect));
    QVERIFY2(p->prepare(44100, 256, &error, true), qPrintable(error));
    float l[256]{}, r[256]{}, ol[256]{}, orr[256]{};
    l[0] = 1;
    Clock clock;
    clock.offline = true;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], .5f);
    QCOMPARE(p->latency(), 32);
    auto state = p->state(&error);
    QVERIFY2(!state.isEmpty(), qPrintable(error));
    QVERIFY(p->restore(state, &error));
  }
  void separateProcessRealtime() {
    QString error;
    auto p = createIsolated(Descriptor::fromValue(effect));
    QVERIFY2(p->prepare(44100, 256, &error), qPrintable(error));
    float l[256]{}, r[256]{}, ol[256]{}, orr[256]{};
    Clock clock;
    l[0] = 1;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], 0.f);
    QTest::qWait(20);
    l[0] = 0;
    clock.sample = 256;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], 0.f);
    QTest::qWait(20);
    clock.sample = 512;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QCOMPARE(ol[32], .5f);
    QCOMPARE(p->latency(), 544);
  }
  void isolatedExitKeepsHostRunning() {
    QString error;
    auto p = createIsolated(Descriptor::fromValue(effect));
    QVERIFY2(p->prepare(44100, 256, &error), qPrintable(error));
    p->setParameter(1, 1);
    float l[256]{}, r[256]{}, ol[256]{}, orr[256]{};
    Clock clock;
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
    QTest::qWait(100);
    QTRY_VERIFY_WITH_TIMEOUT(!p->status().isEmpty(), 3000);
    QVERIFY(p->process(256, l, r, ol, orr, nullptr, 0, clock));
  }
  void malformedPlugin() {
    const auto r = scan(QCoreApplication::applicationFilePath());
    QVERIFY(!r["error"].toString().isEmpty());
  }
};
QTEST_MAIN(Checks)
#include "checks.moc"
