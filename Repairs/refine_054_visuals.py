from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/libmscore/freeslur.cpp';s=p.read_text(encoding='utf8')
s=s.replace('      const auto newStart=endpoint(true,slur()->freeStartSide(),p0),newEnd=endpoint(false,slur()->freeEndSide(),p3);','''      auto routedSide=[&](bool start){auto chord=start?startChord:endChord;if(!chord||chord->measure()->system()!=system())return 0;int side=start?slur()->freeStartSide():slur()->freeEndSide();if(!side&&ups(start?Grip::START:Grip::END).off.isNull()&&!savedNodes.isEmpty())side=start?savedNodes.front().before:savedNodes.back().after;return side;};
      const int startSide=routedSide(true),endSide=routedSide(false);
      const auto newStart=endpoint(true,startSide,p0),newEnd=endpoint(false,endSide,p3);''',1)
s=s.replace('      const CubicBezier base(p0,p1,p2,p3); const double sp=spatium();','''      const double reach=qBound(.5*spatium(),std::abs(p3.x()-p0.x())*.12,2.*spatium());
      if(startSide&&ups(Grip::BEZIER1).off.isNull())p1.setY(p0.y()+startSide*reach);
      if(endSide&&ups(Grip::BEZIER2).off.isNull())p2.setY(p3.y()+endSide*reach);
      const CubicBezier base(p0,p1,p2,p3); const double sp=spatium();''',1)
s=s.replace('points.front().locked=!ups(Grip::START)', 'points.front().locked=startSide||!ups(Grip::START)',1).replace('points.back().locked=!ups(Grip::END)','points.back().locked=endSide||!ups(Grip::END)',1)
p.write_bytes(s.encode())
p=R/'native/libmscore/symbol.cpp';s=p.read_text(encoding='utf8').replace('if(_handTextSize>0)font.setPointSizeF(_handTextSize);','if(_handTextSize>0)font.setPointSizeF(_handTextSize*(expression.sizeIsSpatiumDependent()?spatium()/SPATIUM20:1.));',1)
s=s.replace('p->setFont(handFont());p->drawText(handTextPosition(),handLeft() ? "l.h." : "r.h.");','QFont textFont=handFont();textFont.setPointSizeF(textFont.pointSizeF()*MScore::pixelRatio);TextBase::drawTextWorkaround(p,textFont,handTextPosition(),handLeft() ? "l.h." : "r.h.");',1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/performanceeditor/handsymbol_tests.inc';s=p.read_text(encoding='utf8')
s=s.replace('      auto savedStyle=HandBracket::defaults(mark->sym());','      const SymId allHands[]={SymId::keyboardPlayWithLH,SymId::keyboardPlayWithLHEnd,SymId::keyboardPlayWithRH,SymId::keyboardPlayWithRHEnd};QVector<HandBracket::Style> savedStyles;for(auto id:allHands)savedStyles.append(HandBracket::defaults(id));\n      auto savedStyle=HandBracket::defaults(mark->sym());',1)
s=s.replace('QVERIFY(HandBracket::setDefaults(mark->sym(),savedStyle));','QVERIFY(HandBracket::setDefaults(mark->sym(),savedStyle));for(int i=0;i<4;++i){handSettings.remove(QString("handBracket/%1").arg(Sym::id2name(allHands[i])));QVERIFY(HandBracket::setDefaults(allHands[i],savedStyles[i]));}handSettings.sync();',1)
p.write_bytes(s.encode())
