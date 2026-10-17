from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/libmscore/slur.cpp';s=p.read_text(encoding='utf8').replace('(slur()->freeAuto() || !slur()->freeNodes().isEmpty())','(slur()->freeAuto() || !slur()->freeNodes().isEmpty() || slur()->freeStartSide() || slur()->freeEndSide())',1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/performanceeditor/handsymbol_tests.inc';s=p.read_text(encoding='utf8').replace('QCOMPARE(view->getEditData().grips,3);view->changeState','QCOMPARE(view->getEditData().grips,4);view->changeState',1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/performanceeditor/freeslur_tests.inc';s=p.read_text(encoding='utf8').replace('void TestPerformanceEditor::repair054EndpointSidesAndHandText(){','''void TestPerformanceEditor::repair054EndpointSidesAndHandText(){
 if(!Ms::mscore){QCoreApplication::setOrganizationName("PerformanceRegression");QCoreApplication::setApplicationName("Repair054");QSettings::setDefaultFormat(QSettings::IniFormat);QSettings::setPath(QSettings::IniFormat,QSettings::UserScope,_directory.path());dataPath=_directory.path();MScore::noGui=true;noSeq=true;converterMode=true;initMuseScoreResources();QStringList args;MuseScore::init(args);}
''',1)
at=s.rfind('\n}');s=s[:at]+'''
 auto main=Ms::mscore;auto grand=main->readScore(QString(TESTROOT)+"/mtest/mscore/performanceeditor/repair054-crossstaff.mscx");QVERIFY(grand);main->setCurrentScoreView(main->appendScore(grand));main->resize(1250,850);main->show();
 auto firstChord=toChord(grand->firstSegment(SegmentType::ChordRest)->element(4)),lastChord=toChord(grand->tick2segment(Fraction::fromTicks(1440),false,SegmentType::ChordRest)->element(0));
 auto cross=new Slur(grand);cross->setTrack(4);cross->setTrack2(0);cross->setTick(firstChord->tick());cross->setTicks(lastChord->tick()-firstChord->tick());cross->setStartElement(firstChord);cross->setEndElement(lastChord);
 cross->setProperty(Pid::FREE_SLUR_MODE,true);cross->setProperty(Pid::FREE_SLUR_AUTO,true);cross->setProperty(Pid::FREE_SLUR_START_SIDE,-1);cross->setProperty(Pid::FREE_SLUR_END_SIDE,1);
 grand->startCmd();grand->undoAddElement(cross);grand->endCmd();grand->doLayout();QVERIFY(cross->frontSegment());auto crossGrips=cross->frontSegment()->gripsPositions();
 QVERIFY(crossGrips[int(Grip::START)].y()<firstChord->upNote()->pagePos().y());QVERIFY(crossGrips[int(Grip::END)].y()>lastChord->downNote()->pagePos().y());
 QTest::qWait(40);const auto artifacts=qEnvironmentVariable("HARMONY_TEST_ARTIFACTS");if(!artifacts.isEmpty()){main->currentScoreView()->grab().save(artifacts+"/slur-crossstaff-054.png");QVERIFY(main->savePdf(grand,artifacts+"/slur-crossstaff-054.pdf"));}
'''+s[at:];p.write_bytes(s.encode())
xml='<?xml version="1.0" encoding="UTF-8"?><museScore version="3.02"><Score><Division>480</Division><Part>'
for staff in [1,2]:xml+=f'<Staff id="{staff}"><StaffType group="pitched"><name>stdNormal</name></StaffType></Staff>'
xml+='<trackName>Piano</trackName><Instrument id="piano"><trackName>Piano</trackName><instrumentId>keyboard.piano</instrumentId><Channel/></Instrument></Part>'
for staff,pitches in [(1,[72,76,74,67]),(2,[48,52,55,50])]:
 xml+=f'<Staff id="{staff}"><Measure number="1"><voice><Clef><concertClefType>{"G" if staff==1 else "F"}</concertClefType></Clef><TimeSig><sigN>4</sigN><sigD>4</sigD></TimeSig>'
 for pitch in pitches:
  tpc={0:14,2:16,4:18,7:15}[pitch%12];xml+=f'<Chord><durationType>quarter</durationType><Note><pitch>{pitch}</pitch><tpc>{tpc}</tpc></Note></Chord>'
 xml+='</voice></Measure></Staff>'
xml+='</Score></museScore>'
p=R/'native/mtest/mscore/performanceeditor/repair054-crossstaff.mscx';p.write_bytes(xml.encode())
