from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=R/'native/libmscore/freeslur.cpp';s=p.read_text(encoding='utf8').replace('(slur()->freeNodes().isEmpty() && !slur()->freeAuto())','(slur()->freeNodes().isEmpty() && !slur()->freeAuto() && !slur()->freeStartSide() && !slur()->freeEndSide())',1);p.write_bytes(s.encode())
s=(H/'mtest/mscore/performanceeditor/tst_performanceeditor.cpp').read_text(encoding='utf8').replace('      void handSymbolModelAndPersistence();','      void repair054EndpointSidesAndHandText();\n      void handSymbolModelAndPersistence();',1);stage('mtest/mscore/performanceeditor/tst_performanceeditor.cpp',s)
s=(H/'mtest/mscore/performanceeditor/handsymbol_tests.inc').read_text(encoding='utf8').replace('beforeGrip.y()-.3*score->spatium()','beforeGrip.y()-1.*score->spatium()').replace('mark.handEnd() ? -.75:.75','mark.handEnd() ? -.6:.6').replace('-1.8*unit','-2.5*unit');stage('mtest/mscore/performanceeditor/handsymbol_tests.inc',s)
s=(H/'mtest/mscore/performanceeditor/notation_051_tests.inc').read_text(encoding='utf8').replace('gap>=.27*unit','gap>=.14*unit').replace('gap<=1.41*unit','gap<=.91*unit');stage('mtest/mscore/performanceeditor/notation_051_tests.inc',s)
s=(H/'mtest/mscore/performanceeditor/freeslur_tests.inc').read_text(encoding='utf8')+'''
void TestPerformanceEditor::repair054EndpointSidesAndHandText(){
 std::unique_ptr<MasterScore> score(readScore("mscore/performanceeditor/freeslur.mscx"));QVERIFY(score);score->doLayout();auto slur=addFreeSlur(score.get());
 score->startCmd();slur->undoChangeProperty(Pid::FREE_SLUR_MODE,true);slur->undoChangeProperty(Pid::FREE_SLUR_START_SIDE,-1);slur->undoChangeProperty(Pid::FREE_SLUR_END_SIDE,1);score->endCmd();score->doLayout();
 auto segment=slur->frontSegment();auto grips=segment->gripsPositions();auto a=toChord(slur->startElement())->upNote(),b=toChord(slur->endElement())->downNote();
 QVERIFY(grips[int(Grip::START)].y()<a->pagePos().y()+a->bbox().top());QVERIFY(grips[int(Grip::END)].y()>b->pagePos().y()+b->bbox().bottom());
 const auto before=freeSlurMidi(score.get());auto original=slur->getProperty(Pid::FREE_SLUR_START_SIDE);score->startCmd();slur->undoChangeProperty(Pid::FREE_SLUR_START_SIDE,1);score->endCmd();score->undoRedo(true,&ed);QCOMPARE(slur->getProperty(Pid::FREE_SLUR_START_SIDE),original);
 auto mark=new Symbol(score.get());mark->setSym(SymId::keyboardPlayWithRHEnd);mark->applyHandPreset();mark->setParent(a);mark->setTrack(0);mark->setProperty(Pid::HAND_BRACKET_TEXT,true);
 score->startCmd();score->undoAddElement(mark);mark->undoChangeProperty(Pid::HAND_TEXT_OFFSET,QPointF(1,2));mark->undoChangeProperty(Pid::HAND_TEXT_SIZE,11.);mark->undoChangeProperty(Pid::HAND_TEXT_AUTO,false);score->endCmd();score->doLayout();
 QCOMPARE(mark->gripsCount(),4);QVERIFY(mark->gripsPositions()[0].x()>a->pagePos().x()+a->bbox().right());
 const auto path=_directory.filePath("repair-054.mscx");QVERIFY(saveScore(score.get(),path));std::unique_ptr<MasterScore> restored(readCreatedScore(path));QVERIFY(restored);Slur* read=nullptr;for(auto entry:restored->spannerMap().map())if(entry.second->isSlur())read=toSlur(entry.second);QVERIFY(read);QCOMPARE(read->freeStartSide(),-1);QCOMPARE(read->freeEndSide(),1);
 Symbol* saved=nullptr;auto first=toChord(restored->firstSegment(SegmentType::ChordRest)->element(0));for(auto e:first->upNote()->el())if(e->isSymbol())saved=toSymbol(e);QVERIFY(saved);QCOMPARE(saved->getProperty(Pid::HAND_TEXT_OFFSET).toPointF(),QPointF(1,2));QCOMPARE(saved->getProperty(Pid::HAND_TEXT_SIZE).toDouble(),11.);QVERIFY(!saved->getProperty(Pid::HAND_TEXT_AUTO).toBool());QCOMPARE(freeSlurMidi(restored.get()),before);
}
''';stage('mtest/mscore/performanceeditor/freeslur_tests.inc',s)
