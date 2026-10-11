// SPDX-License-Identifier: GPL-2.0-or-later
#include <QtTest>
#include <QTemporaryDir>
#include <QFile>
#include <QProcess>
#include <QAudioDeviceInfo>
#include <sndfile.h>
#include "audioreader.h"
#include "mediasession.h"
#include <cmath>
class TestMedia:public QObject {
 Q_OBJECT
 QTemporaryDir dir;
 QString wav,flac;
 void tone(const QString& path,int format,int rate,int channels) {
  SF_INFO info={};info.channels=channels;info.samplerate=rate;info.format=format|SF_FORMAT_PCM_16;
  SNDFILE* file=sf_open(path.toUtf8().constData(),SFM_WRITE,&info);QVERIFY(file);
  QVector<float> samples(rate*3*channels);
  for(int f=0;f<rate*3;++f)for(int c=0;c<channels;++c)samples[f*channels+c]=float(.4*std::sin(2*3.141592653589793*440*f/rate));
  QCOMPARE(sf_writef_float(file,samples.constData(),rate*3),sf_count_t(rate*3));sf_close(file);
 }
 double frequency(const QVector<float>& samples,int rate) {
  int begin=rate/5,end=qMin(samples.size()/2,rate*2),crossings=0;
  for(int i=begin+1;i<end;++i)if(samples[(i-1)*2]<=0&&samples[i*2]>0)++crossings;
  return double(crossings)*rate/(end-begin);
 }
private slots:
 void initTestCase(){wav=dir.path()+"/tone.wav";flac=dir.path()+"/tone.flac";tone(wav,SF_FORMAT_WAV,44100,2);tone(flac,SF_FORMAT_FLAC,48000,1);}
 void wavAndFlac(){
  for(QString path:{wav,flac}){KumoAudio::Reader r;QString error;QVERIFY2(r.open(path,&error),qPrintable(error));QCOMPARE(r.frames(),qint64(r.rate()*3));QVERIFY(r.seek(r.rate()));QVector<float> b(100*r.channels());QCOMPARE(r.read(b.data(),100),qint64(100));}
 }
 void unicodePath(){
  QString path=dir.path()+QString::fromUtf8("/钢琴原曲.wav");QVERIFY(QFile::copy(wav,path));KumoAudio::Reader r;QString e;QVERIFY2(r.open(path,&e),qPrintable(e));
 }
 void tempoAndPitch_data(){QTest::addColumn<double>("speed");for(double s:{.5,.75,1.,1.25,1.5})QTest::newRow(qPrintable(QString::number(s)))<<s;}
 void tempoAndPitch(){
  QFETCH(double,speed);std::atomic_bool cancel{false};QVector<float> pcm;QString e;
  QVERIFY2(KumoAudio::stream(wav,{0,3000,speed,false},44100,[&](const float* p,int frames){for(int i=0;i<frames*2;++i)pcm.append(p[i]);return true;},cancel,&e),qPrintable(e));
  QVERIFY(std::abs(double(pcm.size()/2)/44100-3./speed)<.003);
  QVERIFY(std::abs(frequency(pcm,44100)-440)<1.5);
 }
 void sampleClockConversion(){
  std::atomic_bool cancel{false};QVector<float> pcm;QString e;
  QVERIFY(KumoAudio::stream(flac,{500,2500,.75,false},44100,[&](const float* p,int n){for(int i=0;i<n*2;++i)pcm.append(p[i]);return true;},cancel,&e));
  QVERIFY(std::abs(double(pcm.size()/2)/44100-2./.75)<.003);QVERIFY(std::abs(frequency(pcm,44100)-440)<1.5);
 }
 void cancellation(){
  std::atomic_bool cancel{false};int blocks=0;QString e;
  QVERIFY(!KumoAudio::stream(wav,{0,3000,.5,false},44100,[&](const float*,int){if(++blocks==2)cancel=true;return !cancel;},cancel,&e));QCOMPARE(blocks,2);
 }
 void invalidFiles(){KumoAudio::Reader r;QString e;QVERIFY(!r.open(dir.path()+"/missing.wav",&e));QVERIFY(!e.isEmpty());}
 void asynchronousWaveform(){
  ReferenceMediaSession session(nullptr);QSignalSpy ready(&session,&ReferenceMediaSession::fileReady);
  session.open(wav);QTRY_COMPARE(ready.count(),1);QTRY_COMPARE(session.waveform().size(),4096);
  QCOMPARE(session.duration(),3000.);session.seek(1000);QCOMPARE(session.position(),1000.);
  session.setSpeed(.75);QCOMPARE(session.speed(),.75);session.pause();QVERIFY(!session.playing());
 }
 void repeatedLoadAndClose(){
  for(int i=0;i<8;++i){ReferenceMediaSession s(nullptr);s.open(wav);s.open(flac);s.pause();}
 }
 void mp3Vbr(){
  QString path=dir.path()+"/vbr.mp3";QProcess encoder;encoder.start("ffmpeg",{"-v","error","-i",wav,"-codec:a","libmp3lame","-q:a","3",path});QVERIFY(encoder.waitForFinished(10000));QCOMPARE(encoder.exitCode(),0);
  KumoAudio::Reader reader;QString error;QVERIFY2(reader.open(path,&error),qPrintable(error));QVERIFY(std::abs(double(reader.frames())/reader.rate()-3)<.04);QVERIFY(reader.seek(44100));
  std::atomic_bool cancel{false};QVector<float> pcm;QVERIFY(KumoAudio::stream(path,{500,2500,.75,false},44100,[&](const float* p,int n){for(int i=0;i<n*2;++i)pcm.append(p[i]);return true;},cancel,&error));QVERIFY(std::abs(frequency(pcm,44100)-440)<2);
 }
 void viewportAndCancellation(){
  ReferenceMediaSession s(nullptr);QSignalSpy ready(&s,&ReferenceMediaSession::fileReady),tiles(&s,&ReferenceMediaSession::waveformReady);
  s.open(wav);QTRY_COMPARE(ready.count(),1);s.requestWaveform(100,900,800);s.requestWaveform(900,1500,800);QTRY_COMPARE(tiles.count(),1);QCOMPARE(tiles[0][0].toDouble(),900.);QCOMPARE(tiles[0][2].toList().size(),800);
  s.requestWaveform(900,1500,800);QCOMPARE(tiles.count(),2);
 }
 void realOutputMuted(){
  if(QAudioDeviceInfo::defaultOutputDevice().isNull())QSKIP("No audio device; offline DSP remains tested");
  ReferenceMediaSession s(nullptr);s.open(wav);QTRY_VERIFY(s.duration()>0);s.setVolume(0);s.play();
  QVERIFY2(s.playing(),qPrintable(s.status()));QTest::qWait(350);QVERIFY(s.position()>0);
  s.seek(1200);QTest::qWait(180);QVERIFY(s.position()>=1200);s.setLoop(900,1100,true);QTest::qWait(450);
  QVERIFY(s.position()>=900 && s.position()<=1100);s.pause();QVERIFY(!s.playing());
 }
};
QTEST_GUILESS_MAIN(TestMedia)
#include "tst_media.moc"
