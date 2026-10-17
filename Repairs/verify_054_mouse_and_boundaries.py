from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mtest/mscore/performanceeditor/handsymbol_tests.inc';s=p.read_text(encoding='utf8')
a='QCOMPARE(view->getEditData().grips,4);view->changeState(ViewState::NORMAL);'
b='''QCOMPARE(view->getEditData().grips,4);view->updateGrips();
      const auto textOriginal=right->getProperty(Pid::HAND_TEXT_OFFSET),lineOriginal=right->offset();const int textUndo=score->undoStack()->getCurIdx();
      auto textPoint=view->matrix().map(view->getEditData().grip[3].center()).toPoint(),textMoved=textPoint+QPoint(18,10);
      QTest::mousePress(view,Qt::LeftButton,Qt::NoModifier,textPoint);QMouseEvent textMotion(QEvent::MouseMove,textMoved,textMoved,view->mapToGlobal(textMoved),Qt::NoButton,Qt::LeftButton,Qt::NoModifier);QApplication::sendEvent(view,&textMotion);QApplication::sendEvent(view,&textMotion);QTest::mouseRelease(view,Qt::LeftButton,Qt::NoModifier,textMoved);
      QVERIFY(right->getProperty(Pid::HAND_TEXT_OFFSET)!=textOriginal);QCOMPARE(right->offset(),lineOriginal);QVERIFY(!right->getProperty(Pid::HAND_TEXT_AUTO).toBool());QCOMPARE(score->undoStack()->getCurIdx(),textUndo+1);score->undoRedo(true,&ed);QCOMPARE(right->getProperty(Pid::HAND_TEXT_OFFSET),textOriginal);QVERIFY(right->getProperty(Pid::HAND_TEXT_AUTO).toBool());
      view->changeState(ViewState::NORMAL);'''
assert a in s;s=s.replace(a,b,1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/performanceeditor/freeslur_tests.inc';s=p.read_text(encoding='utf8');at=s.rfind('\n}')
s=s[:at]+'''
 auto ritScore=main->readScore(QString(TESTROOT)+"/mtest/mscore/performanceeditor/freeslur.mscx");QVERIFY(ritScore);main->setCurrentScoreView(main->appendScore(ritScore));
 auto breakLine=new LayoutBreak(ritScore);breakLine->setLayoutBreakType(LayoutBreak::Type::LINE);breakLine->setParent(ritScore->firstMeasure());ritScore->startCmd();ritScore->undoAddElement(breakLine);ritScore->endCmd();
 auto rit=new TextLine(ritScore,true);rit->setTrack(0);rit->setTick(Fraction(0,1));rit->setTicks(ritScore->firstMeasure()->nextMeasure()->endTick());rit->setBeginText("rit.");rit->setProperty(Pid::RIT_MODE,true);rit->setProperty(Pid::RIT_PLAY,true);ritScore->startCmd();ritScore->undoAddElement(rit);ritScore->endCmd();ritScore->doLayout();
 System* endSystem=nullptr;auto endPosition=rit->linePos(Grip::END,&endSystem);auto last=ritScore->firstMeasure()->nextMeasure();QCOMPARE(endSystem,last->system());QVERIFY(std::abs(endPosition.x()-last->x()-last->width())<.01);QCOMPARE(rit->spannerSegments().size(),size_t(2));
 if(!artifacts.isEmpty()){main->currentScoreView()->grab().save(artifacts+"/rit-boundaries-054.png");}
 ritScore->startCmd();rit->undoChangeProperty(Pid::SPANNER_TICKS,ritScore->firstMeasure()->endTick());ritScore->endCmd();ritScore->doLayout();endPosition=rit->linePos(Grip::END,&endSystem);QCOMPARE(endSystem,ritScore->firstMeasure()->system());QCOMPARE(rit->spannerSegments().size(),size_t(1));QVERIFY(std::isfinite(endPosition.x()));
'''+s[at:];p.write_bytes(s.encode())
