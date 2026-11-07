from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];N=ROOT/'P2/native'
def edit(name,old,new):
    path=N/name;text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError('Missing '+name+' '+old[:45])
    path.write_text(text.replace(old,new,1),encoding='utf8',newline='\n')
edit('mscore/referenceaudio/CMakeLists.txt','mediaproject.cpp mediaproject.h','mediaproject.cpp mediaproject.h mediaexport.cpp mediaexport.h mediaexportfactory.h')
edit('mscore/referenceaudio/mediaplugin.cpp','#include "mediafactory.h"','#include "mediafactory.h"\n#include "mediaexportfactory.h"\n#include "mediaexport.h"')
edit('mscore/referenceaudio/mediaplugin.cpp','public KumoSpectrumFactory {','public KumoSpectrumFactory,public KumoMediaExportFactory {')
edit('mscore/referenceaudio/mediaplugin.cpp','Q_INTERFACES(KumoMediaFactory KumoMediaProjectFactory KumoSpectrumFactory)','Q_INTERFACES(KumoMediaFactory KumoMediaProjectFactory KumoSpectrumFactory KumoMediaExportFactory)')
edit('mscore/referenceaudio/mediaplugin.cpp','public:QObject* createSpectrum','public:QObject* createAudioExport(QObject* p)override{return new ReferenceAudioExport(p);}\n QObject* createSpectrum')
edit('mscore/workflow/referencefactory.h','QObject* createReferenceMedia(QObject* parent);','QObject* createReferenceAudioExport(QObject* parent); QObject* createReferenceMedia(QObject* parent);')
edit('mscore/workflow/referencefactory.cpp','#include "../referenceaudio/mediafactory.h"','#include "../referenceaudio/mediafactory.h"\n#include "../referenceaudio/mediaexportfactory.h"')
edit('mscore/workflow/referencefactory.cpp','QObject* createReferenceMedia(QObject* parent) {','QObject* createReferenceAudioExport(QObject* parent){\n if(!personalFeaturesEnabled())return new MissingMedia(parent,QObject::tr("个人扩展功能已关闭。"));\n auto loader=module();auto factory=qobject_cast<KumoMediaExportFactory*>(loader->instance());\n return factory?factory->createAudioExport(parent):new MissingMedia(parent,QObject::tr("请更新随程序提供的原曲组件后导出视频声音。"));\n}\nQObject* createReferenceMedia(QObject* parent) {')
edit('mtest/mscore/spectrum/tst_spectrum.cpp','#include "referenceaudio/spectrumfactory.h"','#include "referenceaudio/spectrumfactory.h"\n#include "referenceaudio/mediaexportfactory.h"')
edit('mtest/mscore/spectrum/tst_spectrum.cpp','    void cleanupTestCase() {',r'''    void videoAudioExport164(){
        auto factory=qobject_cast<KumoMediaExportFactory*>(_loader.instance());QVERIFY(factory);QScopedPointer<QObject> render(factory->createAudioExport(this));QVERIFY(render);
        const auto path=tone("video-source-164",22050,1,false,330,false,0,false,4),destination=_dir.filePath(QString::fromUtf8("视频 声音164.f32"));
        const QVariantList pieces{QVariantMap{{"from",100.},{"until",600.},{"at",0.},{"duration",500.}},QVariantMap{{"from",800.},{"until",1200.},{"at",700.},{"duration",400.}}};
        const QVariantMap request{{"path",path},{"destination",destination},{"sampleRate",48000},{"duration",1100.},{"pieces",pieces}};QSignalSpy finished(render.data(),SIGNAL(finished(QVariantMap)));
        QVERIFY(QMetaObject::invokeMethod(render.data(),"render",Q_ARG(QVariantMap,request)));QTRY_COMPARE_WITH_TIMEOUT(finished.count(),1,10000);const auto result=finished[0][0].toMap();QVERIFY2(!result.contains("error"),qPrintable(result.value("error").toString()));QCOMPARE(result.value("frames").toLongLong(),52800LL);
        QFile output(destination);QVERIFY(output.open(QIODevice::ReadOnly));const auto bytes=output.readAll();QCOMPARE(bytes.size(),52800*8);const auto samples=reinterpret_cast<const float*>(bytes.constData());double energy=0;for(int i=1000;i<20000;++i)energy+=double(samples[i*2])*samples[i*2];QVERIFY(std::sqrt(energy/19000)>.25);for(int i=24500;i<33300;++i)QCOMPARE(samples[i*2],0.f);QCOMPARE(samples[4000],samples[4001]);
        qInfo()<<"Video reference audio frames"<<result.value("frames")<<"ms"<<result.value("milliseconds");
        output.close();QFile previous(destination);QVERIFY(previous.open(QIODevice::WriteOnly|QIODevice::Truncate));previous.write("keep");previous.close();finished.clear();auto invalid=request;invalid["sampleRate"]=0;QVERIFY(QMetaObject::invokeMethod(render.data(),"render",Q_ARG(QVariantMap,invalid)));QTRY_COMPARE(finished.count(),1);QVERIFY(finished[0][0].toMap().contains("error"));QVERIFY(previous.open(QIODevice::ReadOnly));QCOMPARE(previous.readAll(),QByteArray("keep"));previous.close();
        const auto folder=qEnvironmentVariable("P2_REFERENCE_LONG_AUDIO");QVERIFY(!folder.isEmpty());auto longRequest=request;longRequest["path"]=QDir(folder).filePath("long.mp3");longRequest["duration"]=180000.;longRequest["pieces"]=QVariantList{QVariantMap{{"from",0.},{"until",180000.},{"at",0.},{"duration",180000.}}};finished.clear();QVERIFY(QMetaObject::invokeMethod(render.data(),"render",Q_ARG(QVariantMap,longRequest)));QTest::qWait(20);QElapsedTimer cancel;cancel.start();QVERIFY(QMetaObject::invokeMethod(render.data(),"cancel"));QTRY_COMPARE_WITH_TIMEOUT(finished.count(),1,3000);QVERIFY(finished[0][0].toMap().value("cancelled").toBool());QVERIFY(previous.open(QIODevice::ReadOnly));QCOMPARE(previous.readAll(),QByteArray("keep"));qInfo()<<"Video audio cancel ms"<<cancel.elapsed();
    }
    void cleanupTestCase() {''')
script=ROOT/'Repairs/sync_164.py';text=script.read_text('utf8');text=text.replace("source=ROOT/'P2/native'/name;target=HOST/name;data=source.read_bytes()","source=ROOT/'P2/native'/name;target=HOST/name\n    if not source.is_file() and original is None:continue\n    data=source.read_bytes()")
if 'target.parent.mkdir' not in text:text=text.replace('for name,source,target,data in pending:','for name,source,target,data in pending:\n    target.parent.mkdir(parents=True,exist_ok=True)')
script.write_text(text,encoding='utf8',newline='\n')
text=(ROOT/'Repairs/run_spectrum_162.py').read_text('utf8').replace('repair-162','repair-164').replace("str(OUT/'long-audio')","str(ROOT/'P2/out/repair-162/long-audio')")
(ROOT/'Repairs/run_spectrum_164.py').write_text(text,encoding='utf8',newline='\n')
