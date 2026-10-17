"""Independent slur endpoints, cross-staff geometry and exact rit. right edges."""
from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def edit(path,changes):
 p=H/path;s=p.read_text(encoding='utf8')
 for a,b in changes:
  expected=2 if path=='libmscore/freeslur.cpp' and a.startswith('      const auto p0=ups') else 1
  assert s.count(a)==expected,(path,a[:90],s.count(a));s=s.replace(a,b,1)
 q=R/'native'/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(s.encode())
edit('libmscore/property.h',[('      FREE_SLUR_AUTO,','      FREE_SLUR_AUTO,\n      FREE_SLUR_START_SIDE,\n      FREE_SLUR_END_SIDE,\n      HAND_TEXT_OFFSET,\n      HAND_TEXT_FONT,\n      HAND_TEXT_SIZE,\n      HAND_TEXT_AUTO,')])
edit('libmscore/property.cpp',[('      { Pid::FREE_SLUR_AUTO, P_TYPE::BOOL, true, "freeSlurAuto", "free slur automatic avoidance" },','''      { Pid::FREE_SLUR_AUTO, P_TYPE::BOOL, true, "freeSlurAuto", "free slur automatic avoidance" },
      { Pid::FREE_SLUR_START_SIDE, P_TYPE::INT, true, "freeSlurStartSide", "free slur start side" },
      { Pid::FREE_SLUR_END_SIDE, P_TYPE::INT, true, "freeSlurEndSide", "free slur end side" },
      { Pid::HAND_TEXT_OFFSET, P_TYPE::POINT, true, "handTextOffset", "hand text offset in staff spaces" },
      { Pid::HAND_TEXT_FONT, P_TYPE::STRING, true, "handTextFont", "hand text font" },
      { Pid::HAND_TEXT_SIZE, P_TYPE::REAL, true, "handTextSize", "hand text point size" },
      { Pid::HAND_TEXT_AUTO, P_TYPE::BOOL, true, "handTextAuto", "hand text automatic placement" },''')])
edit('libmscore/slur.h',[
 ('      bool _freeAuto = false;','      bool _freeAuto = false;\n      int _freeStartSide=0,_freeEndSide=0;'),
 ('      bool freeAuto() const { return _freeAuto; }','      bool freeAuto() const { return _freeAuto; }\n      int freeStartSide()const{return _freeStartSide;}\n      int freeEndSide()const{return _freeEndSide;}')])
edit('libmscore/slur.cpp',[
 ('      _freeMode=s._freeMode;','      _freeStartSide=s._freeStartSide;_freeEndSide=s._freeEndSide;\n      _freeMode=s._freeMode;'),
 ('      writeProperty(xml,Pid::FREE_SLUR_AUTO);','      writeProperty(xml,Pid::FREE_SLUR_AUTO);\n      writeProperty(xml,Pid::FREE_SLUR_START_SIDE);\n      writeProperty(xml,Pid::FREE_SLUR_END_SIDE);'),
 ('      if(e.name()==propertyName(Pid::FREE_SLUR_AUTO))','      for(auto id:{Pid::FREE_SLUR_START_SIDE,Pid::FREE_SLUR_END_SIDE})if(e.name()==propertyName(id)){readProperty(e,id);return true;}\n      if(e.name()==propertyName(Pid::FREE_SLUR_AUTO))')])
edit('libmscore/freeslur.cpp',[
 ('#include "chord.h"','#include "chord.h"\n#include "note.h"'),
 ('      if(id==Pid::FREE_SLUR_MODE) return _freeMode;','      if(id==Pid::FREE_SLUR_START_SIDE)return _freeStartSide;\n      if(id==Pid::FREE_SLUR_END_SIDE)return _freeEndSide;\n      if(id==Pid::FREE_SLUR_MODE) return _freeMode;'),
 ('      if(id==Pid::FREE_SLUR_NODES) return QString("[]");','      if(id==Pid::FREE_SLUR_START_SIDE||id==Pid::FREE_SLUR_END_SIDE)return 0;\n      if(id==Pid::FREE_SLUR_NODES) return QString("[]");'),
 ('      if(id==Pid::FREE_SLUR_MODE) _freeMode=value.toBool();','      if(id==Pid::FREE_SLUR_START_SIDE||id==Pid::FREE_SLUR_END_SIDE){int side=value.toInt();if(side<-1||side>1)return false;if(id==Pid::FREE_SLUR_START_SIDE)_freeStartSide=side;else _freeEndSide=side;}\n      else if(id==Pid::FREE_SLUR_MODE) _freeMode=value.toBool();'),
 ('      const auto p0=ups(Grip::START).pos(),p1=ups(Grip::BEZIER1).pos(),p2=ups(Grip::BEZIER2).pos(),p3=ups(Grip::END).pos();','''      auto p0=ups(Grip::START).pos(),p1=ups(Grip::BEZIER1).pos(),p2=ups(Grip::BEZIER2).pos(),p3=ups(Grip::END).pos();
      const auto& savedNodes=slur()->freeNodes();
      auto chordFor=[](Element* e)->Chord*{return !e?nullptr:e->isChord()?toChord(e):e->isNote()?toNote(e)->chord():nullptr;};
      auto startChord=chordFor(slur()->startElement()),endChord=chordFor(slur()->endElement());
      auto endpoint=[&](bool start,int side,QPointF old){
            const auto grip=start?Grip::START:Grip::END;
            if(!side){if(!ups(grip).off.isNull())return old;side=savedNodes.isEmpty()?0:start?savedNodes.front().before:savedNodes.back().after;}
            if(!side)return old;
            auto chord=start?startChord:endChord;if(!chord||chord->measure()->system()!=system())return old;
            auto e=start?slur()->startElement():slur()->endElement();
            auto note=e->isNote()?toNote(e):side<0?chord->upNote():chord->downNote();
            const auto box=note->bbox().translated(note->pagePos()-pagePos());
            return QPointF(box.center().x(),side<0?box.top()-.3*spatium():box.bottom()+.3*spatium())+ups(grip).off;
            };
      const auto newStart=endpoint(true,slur()->freeStartSide(),p0),newEnd=endpoint(false,slur()->freeEndSide(),p3);
      p1+=newStart-p0;p2+=newEnd-p3;p0=newStart;p3=newEnd;'''),
 ('            auto ss=slur()->startSegment();auto es=slur()->endSegment();','''            auto ss=slur()->startSegment();auto es=slur()->endSegment();
            const int firstStaff=qMax(0,qMin(staffIdx(),qMin(startChord?startChord->vStaffIdx():staffIdx(),endChord?endChord->vStaffIdx():staffIdx())));
            const int lastStaff=qMin(score()->nstaves()-1,qMax(staffIdx(),qMax(startChord?startChord->vStaffIdx():staffIdx(),endChord?endChord->vStaffIdx():staffIdx())));'''),
 ('if(segment->segmentType()==SegmentType::ChordRest)for(int track=staffIdx()*VOICES;track<(staffIdx()+1)*VOICES;++track)', 'if(segment->segmentType()==SegmentType::ChordRest)for(int track=firstStaff*VOICES;track<(lastStaff+1)*VOICES;++track)'),
 ('                  const auto shape=segment->staffShape(staffIdx()).translated(segment->pos()+segment->measure()->pos()-pos());\n                  for(const auto& r:shape) {','''                  for(int targetStaff=firstStaff;targetStaff<=lastStaff;++targetStaff){
                  const auto shape=segment->staffShape(targetStaff).translated(segment->pos()+segment->measure()->pos()-pos()+QPointF(0,system()->staffYpage(targetStaff)-system()->staffYpage(staffIdx())));
                  for(const auto& r:shape) {'''),
 ('                  if(obstacles.size()>2048)break;\n                  }\n            // Native endpoint', '                  if(obstacles.size()>2048)break;\n                  }\n                  }\n            // Native endpoint')])
edit('mscore/inspector/freeslurinspector.h',[
 ('      QComboBox* _span=nullptr;','      QComboBox* _span=nullptr;\n      QComboBox* _startSide=nullptr;QComboBox* _endSide=nullptr;'),
 ('            _result=new QLabel(this);','''            auto endpoints=new QWidget(this);auto endpointGrid=new QGridLayout(endpoints);endpointGrid->setContentsMargins(0,0,0,0);layout->addWidget(endpoints,5,0,1,3);
            for(int i=0;i<2;++i){auto box=new QComboBox(endpoints);box->addItems({tr("自动"),tr("音符上方"),tr("音符下方")});box->setObjectName(i?"freeSlurEndSide":"freeSlurStartSide");endpointGrid->addWidget(new QLabel(i?tr("终点位置"):tr("起点位置"),endpoints),i,0);endpointGrid->addWidget(box,i,1);if(i)_endSide=box;else _startSide=box;connect(box,QOverload<int>::of(&QComboBox::activated),this,[this,i](int value){if(_owner)mscore->performanceEditor()->queueProperty(_owner,i?Pid::FREE_SLUR_END_SIDE:Pid::FREE_SLUR_START_SIDE,value==1?-1:value==2?1:0);});}
            _result=new QLabel(this);'''),
 ('            _details->setEnabled(single && owner->freeMode());','            for(int i=0;i<2;++i){auto box=i?_endSide:_startSide;QSignalBlocker block(box);const int side=i?owner->freeEndSide():owner->freeStartSide();box->setCurrentIndex(side<0?1:side>0?2:0);box->setEnabled(single&&owner->freeMode());}\n            _details->setEnabled(single && owner->freeMode());')])
edit('libmscore/textline.cpp',[
 ('      Measure* measure = score()->tick2measureMM(point);','      const Fraction lookup=grip==Grip::END&&point>Fraction(0,1)?point-Fraction::eps():point;\n      Measure* measure = score()->tick2measureMM(lookup);')])
edit('mscore/temposymbols.cpp',[
 ('            const bool oldRit=cell->tag=="kumo-rit",oldRestore=cell->tag=="kumo-a-tempo";','''            const QString plain=e->isTextBase()?toTextBase(e)->plainText().simplified().toLower():e->isTextLine()?toTextLine(e)->beginText().simplified().toLower():QString();
            const bool factory=!cell->custom;
            const bool oldRit=cell->tag=="kumo-rit"||(factory&&(plain=="rit."||plain=="ritardando")),oldRestore=cell->tag=="kumo-a-tempo"||(factory&&plain=="a tempo");''')])
print('0.54 curve sources staged')
