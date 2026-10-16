// Copyright (C) 2026 Freddd13 and contributors; GPL version 2.
#include <QtTest>
#include <QTemporaryDir>
#include <QElapsedTimer>
#include <QAudioDeviceInfo>
#include <sndfile.h>
#include "mediaproject.h"
#include "audioreader.h"
#include "pcmring.h"
#include <cmath>
#include <array>
namespace {
KumoReferenceMix output=nullptr;void* context=nullptr;
int rate(){return 44100;}
bool attach(KumoReferenceMix fn,void* ctx){if(output)return false;context=ctx;output=fn;return true;}
void detach(void* ctx){if(context==ctx){output=nullptr;context=nullptr;}}
}
class TestReferenceProject:public QObject {
      Q_OBJECT
      QTemporaryDir folder;
      QString wav,flac;
      void makeTone(const QString& path,int format,int sampleRate,int channels){
            SF_INFO info={};info.channels=channels;info.samplerate=sampleRate;info.format=format|SF_FORMAT_PCM_16;
            auto file=sf_open(path.toUtf8().constData(),SFM_WRITE,&info);QVERIFY(file);QVector<float> pcm(sampleRate*4*channels);
            for(int i=0;i<sampleRate*4;++i)for(int c=0;c<channels;++c)pcm[i*channels+c]=float(.1*std::sin(2*3.141592653589793*440*i/sampleRate));
            QCOMPARE(sf_writef_float(file,pcm.constData(),sampleRate*4),sf_count_t(sampleRate*4));sf_close(file);
            }
      QVariantMap plan(int lanes=1,double speed=1,double start=0){
            QVariantMap piece{{"from",500},{"until",1500},{"at",0},{"duration",1000/speed},{"fade",false}};
            QVariantList clips;for(int i=0;i<lanes;++i)clips.append(QVariantMap{{"path",i%2?flac:wav},{"volume",1.},{"pieces",QVariantList{piece}}});
            return {{"clips",clips},{"joint",true},{"volume",.5},{"startFrame",int(start)}};
            }
private slots:
      void initTestCase(){wav=folder.filePath("tone.wav");flac=folder.filePath("tone.flac");makeTone(wav,SF_FORMAT_WAV,44100,2);makeTone(flac,SF_FORMAT_FLAC,48000,1);}
      void boundedRingWrap(){KumoAudio::PcmRing ring(8);std::atomic_bool canceled{false};float input[12],result[12];for(int i=0;i<12;++i)input[i]=float(i);QVERIFY(ring.push(input,6,canceled));QCOMPARE(ring.pop(result,5),5u);QVERIFY(ring.push(input,6,canceled));QCOMPARE(ring.available(),7u);QCOMPARE(ring.pop(result,6),6u);QCOMPARE(result[0],10.f);QCOMPARE(result[2],0.f);canceled=true;QVERIFY(!ring.push(input,6,canceled));}
      void eightLanesShareOneClock(){
            ReferenceMediaProject project(nullptr,{1,rate,attach,detach});QElapsedTimer preparation;preparation.start();auto result=project.start(plan(8));QVERIFY2(result["ok"].toBool(),qPrintable(result["error"].toString()));QTRY_VERIFY_WITH_TIMEOUT(project.property("prepared").toBool(),10000);auto prepared=preparation.elapsed();
            QCOMPARE(project.diagnostics()["audioTracks"].toInt(),8);QCOMPARE(project.diagnostics()["boundedBytes"].toLongLong(),qint64(9)*131072*8);
            int frame=0;QVector<float> pcm;std::array<float,256> block{};QElapsedTimer cost;cost.start();qint64 callbackNanoseconds=0,maximumNanoseconds=0;
            while(frame<44100){unsigned n=qMin(128,44100-frame);std::fill(block.begin(),block.end(),0.f);QVERIFY(output);QElapsedTimer callbackCost;callbackCost.start();output(context,block.data(),n,frame,true);auto elapsed=callbackCost.nsecsElapsed();callbackNanoseconds+=elapsed;maximumNanoseconds=qMax(maximumNanoseconds,elapsed);for(unsigned i=0;i<n*2;++i)pcm.append(block[i]);frame+=int(n);if(frame%1024==0)QTest::qWait(1);}
            QCOMPARE(project.diagnostics()["underruns"].toULongLong(),qulonglong(0));QCOMPARE(project.position(),1000.);qInfo()<<"8 tracks prepared ms"<<prepared<<"callback total us"<<callbackNanoseconds/1000<<"maximum period us"<<maximumNanoseconds/1000<<"bounded bytes"<<project.diagnostics()["boundedBytes"];
            double energy=0;for(float v:pcm)energy+=v*v;QVERIFY(energy/pcm.size()>.025);project.stop();QVERIFY(!output);QVERIFY(!project.playing());
            }
      void preparationCancellation(){ReferenceMediaProject project(nullptr,{1,rate,attach,detach});for(int i=0;i<20;++i){QVERIFY(project.start(plan(8,.5))["ok"].toBool());project.stop();}QVERIFY(!output);QVERIFY(project.start(plan(1))["ok"].toBool());QTRY_VERIFY(project.property("prepared").toBool());project.stop();}
      void preRollDoesNotStartAudioEarly(){ReferenceMediaProject project(nullptr,{1,rate,attach,detach});QVERIFY(project.start(plan(1,1,256))["ok"].toBool());QTRY_VERIFY(project.property("prepared").toBool());float block[256]={};output(context,block,128,0,true);QCOMPARE(project.position(),0.);output(context,block,128,128,true);QCOMPARE(project.position(),0.);output(context,block,128,256,true);QVERIFY(project.position()>0);project.stop();}
      void seekStopsOldOutput(){ReferenceMediaProject project(nullptr,{1,rate,attach,detach});QVERIFY(project.start(plan())["ok"].toBool());QTRY_VERIFY(project.property("prepared").toBool());float block[256]={};output(context,block,128,0,true);output(context,block,128,22050,true);QTRY_VERIFY(!project.playing());QVERIFY(project.status().contains(QString::fromUtf8("位置改变")));}
      void invalidPlansKeepStopped(){ReferenceMediaProject project(nullptr,{1,rate,attach,detach});auto p=plan();auto clips=p["clips"].toList();auto clip=clips[0].toMap();clip["path"]=folder.filePath("missing.wav");clips[0]=clip;p["clips"]=clips;QVERIFY(project.start(p).contains("error"));QVERIFY(!project.playing());p=plan();clips=p["clips"].toList();clip=clips[0].toMap();auto pieces=clip["pieces"].toList();pieces.append(pieces.front());clip["pieces"]=pieces;clips[0]=clip;p["clips"]=clips;QVERIFY(project.start(p).contains("error"));}
      void liveMasterGainDoesNotWaitForThePreparedBuffer(){
            ReferenceMediaProject project(nullptr,{1,rate,attach,detach});QVERIFY(project.start(plan(1))["ok"].toBool());QTRY_VERIFY_WITH_TIMEOUT(project.property("prepared").toBool(),10000);
            std::array<float,256> block{};QVERIFY(output);output(context,block.data(),128,0,true);
            project.setVolume(0.);std::fill(block.begin(),block.end(),0.f);output(context,block.data(),128,128,true);for(auto sample:block)QCOMPARE(sample,0.f);
            project.setVolume(1.);std::fill(block.begin(),block.end(),0.f);output(context,block.data(),128,256,true);QVERIFY(std::any_of(block.begin(),block.end(),[](float sample){return std::abs(sample)>.001f;}));project.stop();
            }
      void continuousSpeedPreservesPitch(){
            std::atomic_bool cancel{false};QVector<float> pcm;QString error;
            std::vector<KumoAudio::Segment> segments{{500,1000,.75,false},{1000,1500,1.,false},{1500,2500,1.25,false}};
            QVERIFY2(KumoAudio::streamSequence(wav,segments,44100,[&](const float* data,int count){for(int i=0;i<count*2;++i)pcm.append(data[i]);return true;},cancel,&error),qPrintable(error));
            double expected=.5/.75+.5+1./1.25;QVERIFY(std::abs(double(pcm.size()/2)/44100-expected)<.025);
            int crossings=0,from=4410,until=pcm.size()/2-4410;for(int i=from+1;i<until;++i)if(pcm[(i-1)*2]<=0&&pcm[i*2]>0)++crossings;double frequency=double(crossings)*44100/(until-from);qInfo()<<"continuous speed pitch"<<frequency<<"seconds"<<double(pcm.size()/2)/44100;QVERIFY(std::abs(frequency-440)<3);
            }
      void realDeviceEightLanes(){
            if(QAudioDeviceInfo::defaultOutputDevice().isNull())QSKIP("No audio output device available");
            ReferenceMediaProject project(nullptr,{1,rate,attach,detach});auto p=plan(8);p["joint"]=false;p["volume"]=0.;QVERIFY(project.start(p)["ok"].toBool());QTRY_VERIFY(project.position()>250);QVERIFY(project.playing());QCOMPARE(project.diagnostics()["underruns"].toULongLong(),qulonglong(0));project.stop();
            }
      void independentGroupLoop(){
            if(QAudioDeviceInfo::defaultOutputDevice().isNull())QSKIP("No audio output device available");
            ReferenceMediaProject project(nullptr,{1,rate,attach,detach});auto p=plan(2);p["joint"]=false;p["loop"]=true;p["volume"]=0.;auto clips=p["clips"].toList();for(int i=0;i<clips.size();++i){auto c=clips[i].toMap();c["pieces"]=QVariantList{QVariantMap{{"from",500},{"until",750},{"at",0},{"duration",250},{"fade",true}}};clips[i]=c;}p["clips"]=clips;QVERIFY(project.start(p)["ok"].toBool());QTest::qWait(1600);QVERIFY2(project.playing(),qPrintable(project.status()));QVERIFY(project.position()>=0&&project.position()<250);QCOMPARE(project.diagnostics()["underruns"].toULongLong(),qulonglong(0));project.stop();
            }
};
QTEST_GUILESS_MAIN(TestReferenceProject)
#include "tst_referenceproject.moc"
