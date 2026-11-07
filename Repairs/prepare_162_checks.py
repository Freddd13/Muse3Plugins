from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
name='mtest/mscore/spectrum/tst_spectrum.cpp';path=NATIVE/name
if name not in files:
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((HOST/name).read_bytes());files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest()
text=path.read_text('utf8')
text=text.replace('double frequency = 440, bool harmonics = false, double startAt = 0, bool pulse = false) {','double frequency = 440, bool harmonics = false, double startAt = 0, bool pulse = false, int seconds = 0) {',1)
text=text.replace('const int frames = rate * (pulse?8:2);','const int frames = rate * (seconds>0?seconds:(pulse?8:2));',1)
addition=r'''
    void canonicalTuningAndPitchReuse162() {
        auto value=options(tone("canonical-162"));request(value);
        QTRY_VERIFY_WITH_TIMEOUT(!_session->property("busy").toBool(),10000);
        QCOMPARE(_session->property("info").toMap()["computedBlocks"].toInt(),1);
        value["tuning"]=444.;value["rows"]=720;value["columns"]=768;
        value["lowPitch"]=48.;value["highPitch"]=84.;value["from"]=450.;value["until"]=1700.;
        request(value);QTRY_VERIFY_WITH_TIMEOUT(!_session->property("busy").toBool(),10000);
        auto info=_session->property("info").toMap();QCOMPARE(info["computedBlocks"].toInt(),0);QCOMPARE(info["cachedBlocks"].toInt(),1);QCOMPARE(info["canonicalRows"].toInt(),1024);
        const auto result=image();QCOMPARE(result.size(),QSize(768,720));int row=-1,maximum=-1;
        for(int y=0;y<result.height();++y)if(result.constScanLine(y)[300]>maximum){maximum=result.constScanLine(y)[300];row=y;}
        const double pitch=84.-(row+.5)/720.*36.;
        QVERIFY(qAbs(pitch-(69.-12.*std::log2(444./440.)))<.5);QVERIFY(maximum>200);
        qInfo()<<"162 tuning/range reuse"<<info["workerMilliseconds"]<<"ms"<<pitch;
    }
    void wholeTrackPreparationAndCancel162() {
        auto value=options(tone("whole-162",22050,1,false,440,false,0,false,40));value["preload"]=true;
        request(value);QTRY_VERIFY_WITH_TIMEOUT(!_session->property("busy").toBool(),10000);
        const auto first=image();QVERIFY(!first.isNull());
        QTRY_VERIFY_WITH_TIMEOUT(!_session->property("backgroundBusy").toBool(),30000);
        auto info=_session->property("info").toMap();QCOMPARE(info["totalBlocks"].toInt(),10);QCOMPARE(info["preparedBlocks"].toInt(),10);QCOMPARE(first.cacheKey(),image().cacheKey());
        value["from"]=33100.;value["until"]=34300.;value["preload"]=false;request(value);
        QTRY_VERIFY_WITH_TIMEOUT(!_session->property("busy").toBool(),10000);
        info=_session->property("info").toMap();QCOMPARE(info["computedBlocks"].toInt(),0);QCOMPARE(info["cachedBlocks"].toInt(),1);
        QVERIFY(_session->property("cacheOptions").toMap()["usedMemoryKiB"].toInt()<=8192);
        const auto retained=image();
        value["path"]=tone("cancel-162",22050,1,false,220,false,0,false,40);value["fftSize"]=32768;value["preload"]=true;request(value);
        QVERIFY(QMetaObject::invokeMethod(_session,"cancel"));
        QTRY_VERIFY_WITH_TIMEOUT(!_session->property("busy").toBool(),10000);
        QVERIFY(!_session->property("backgroundBusy").toBool());QCOMPARE(image().cacheKey(),retained.cacheKey());
    }
'''
if 'void canonicalTuningAndPitchReuse162()' not in text:text=text.replace('    void oppositeStereoAndResampled() {',addition+'\n    void oppositeStereoAndResampled() {',1)
path.write_bytes(text.encode('utf8'));record.write_text(json.dumps(files,indent=2),encoding='utf8')
print('Prepared native spectrum cache and cancellation checks')
