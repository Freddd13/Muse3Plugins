from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/libmscore/freeslur.cpp';s=p.read_text(encoding='utf8')
s=s.replace('id==Pid::FREE_SLUR_MODE || id==Pid::FREE_SLUR_AUTO || id==Pid::FREE_SLUR_NODES','id==Pid::FREE_SLUR_MODE || id==Pid::FREE_SLUR_AUTO || id==Pid::FREE_SLUR_NODES || id==Pid::FREE_SLUR_START_SIDE || id==Pid::FREE_SLUR_END_SIDE')
s=s.replace('      SlurTie::reset();','      undoResetProperty(Pid::FREE_SLUR_START_SIDE);undoResetProperty(Pid::FREE_SLUR_END_SIDE);\n      SlurTie::reset();',1)
s=s.replace('      for(const auto& n:_freeGrips) {result.push_back(n.point+origin);', '''      if(_freeCurvePoints.size()>=2){
            const auto& a=_freeCurvePoints.front();const auto& b=_freeCurvePoints[1];
            const auto& z=_freeCurvePoints.back();const auto& y=_freeCurvePoints[_freeCurvePoints.size()-2];
            result[int(Grip::START)]=origin+a.p;result[int(Grip::END)]=origin+z.p;
            result[int(Grip::BEZIER1)]=origin+a.p+a.d*(b.t-a.t)/3;
            result[int(Grip::BEZIER2)]=origin+z.p-z.d*(z.t-y.t)/3;
            }
      for(const auto& n:_freeGrips) {result.push_back(n.point+origin);''',1)
p.write_bytes(s.encode())
p=R/'native/libmscore/symbol.h';s=p.read_text(encoding='utf8').replace('bool _handTextAuto=true;','bool _handTextAuto=true,_handTextDragAuto=true;');p.write_bytes(s.encode())
p=R/'native/libmscore/symbol.cpp';s=p.read_text(encoding='utf8').replace('_handTextDragOriginal=_handTextOffset;','_handTextDragOriginal=_handTextOffset;_handTextDragAuto=_handTextAuto;').replace('setProperty(Pid::HAND_TEXT_OFFSET,_handTextDragOriginal);_handDragging=false;','setProperty(Pid::HAND_TEXT_OFFSET,_handTextDragOriginal);setProperty(Pid::HAND_TEXT_AUTO,_handTextDragAuto);_handDragging=false;');p.write_bytes(s.encode())
