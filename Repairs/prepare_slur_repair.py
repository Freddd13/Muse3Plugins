from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
existing=ROOT/'native/libmscore/freeslur.h'
if existing.exists() and 'bool locked' in existing.read_text(encoding='utf8'):
    raise SystemExit('这是本批开发时的准备记录；当前模块已更新，请使用apply_native.py。')
def mirror(path):
    target=ROOT/'native'/path
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): target.write_bytes((HOST/path).read_bytes())
    return target
def change(path,old,new):
    p=mirror(path); s=p.read_text(encoding='utf8'); assert s.count(old)==1,(path,old[:80])
    p.write_bytes(s.replace(old,new).encode('utf8'))
change('libmscore/freeslur.h','#include <QString>','#include <QString>\n#include <QRectF>')
change('libmscore/freeslur.h','      QPointF offset, tangent; // spatium units; tangent is a derivative adjustment','      QPointF offset, tangent; // spatium units; tangent is a derivative adjustment\n      bool locked = true; // legacy/manual nodes retain their position and tangent')
change('libmscore/freeslur.h','QString encode(const QVector<FreeSlurNode>&);','''QString encode(const QVector<FreeSlurNode>&);
struct CurvePoint { double t; QPointF p,d; bool locked = false; };
struct AvoidanceResult {
      QVector<CurvePoint> points;
      int collisions = 0, candidates = 0;
      bool limited = false;
      };
// Pure bounded geometry; no score pointers, properties or undo commands.
AvoidanceResult avoid(const QVector<CurvePoint>&,const QVector<QRectF>&,bool up,double spatium);
QPointF curvePosition(const QVector<CurvePoint>&,double t);
''')
change('libmscore/freeslur.cpp','#include "xml.h"','#include "xml.h"\n#include "segment.h"\n#include "freesluravoidance.h"')
change('libmscore/freeslur.cpp','if(!item.isArray() || item.toArray().size()!=5) return false;','if(!item.isArray() || (item.toArray().size()!=5 && item.toArray().size()!=6)) return false;')
change('libmscore/freeslur.cpp','            nodes.append({values[0].toDouble(),{values[1].toDouble(),values[2].toDouble()},{values[3].toDouble(),values[4].toDouble()}});','''            if(values.size()==6 && !values[5].isBool()) return false;
            nodes.append({values[0].toDouble(),{values[1].toDouble(),values[2].toDouble()},{values[3].toDouble(),values[4].toDouble()},values.size()==5 || values[5].toBool()});''')
change('libmscore/freeslur.cpp','      for(const auto& n:nodes) values.append(QJsonArray{n.position,n.offset.x(),n.offset.y(),n.tangent.x(),n.tangent.y()});','''      for(const auto& n:nodes) {
            QJsonArray row{n.position,n.offset.x(),n.offset.y(),n.tangent.x(),n.tangent.y()};
            if(!n.locked) row.append(false); // unchanged five-value legacy form for locked nodes
            values.append(row);
            }''')
change('libmscore/freeslur.cpp','      if(id==Pid::FREE_SLUR_MODE) return _freeMode;','      if(id==Pid::FREE_SLUR_MODE) return _freeMode;\n      if(id==Pid::FREE_SLUR_AUTO) return _freeAuto;')
change('libmscore/freeslur.cpp','      if(id==Pid::FREE_SLUR_MODE) return false;','      if(id==Pid::FREE_SLUR_MODE || id==Pid::FREE_SLUR_AUTO) return false;')
change('libmscore/freeslur.cpp','      if(id==Pid::FREE_SLUR_MODE) _freeMode=value.toBool();','      if(id==Pid::FREE_SLUR_MODE) _freeMode=value.toBool();\n      else if(id==Pid::FREE_SLUR_AUTO) _freeAuto=value.toBool();')
change('libmscore/freeslur.cpp','struct CurvePoint { double t; QPointF p,d; };','using FreeSlur::CurvePoint;')
change('libmscore/freeslur.cpp','      if(!slur()->freeMode() || slur()->freeNodes().isEmpty() || !system()) return false;','''      _freeCollisions=0; _freeLimited=false;
      if(!slur()->freeMode() || (slur()->freeNodes().isEmpty() && !slur()->freeAuto()) || !system()) return false;''')
change('libmscore/freeslur.cpp','            points.append({t,p,d}); _freeGrips.append({i,p,{}, {},0,0});','            points.append({t,p,d,node.locked}); _freeGrips.append({i,p,{}, {},0,0});')
change('libmscore/freeslur.cpp','      for(int i=0;i<_freeGrips.size();++i) {\n            const auto& p=points[i+1]; auto& grips=_freeGrips[i];','''      if(slur()->freeAuto() && autoplace()) {
            QVector<QRectF> obstacles;
            const double padding=qMax(.2*sp,score()->styleP(Sid::slurMinDistance));
            auto ss=slur()->startSegment();auto es=slur()->endSegment();
            // Shapes use the same local staff coordinates as native slur placement.
            for(auto segment=system()->firstMeasure()->first();segment;segment=segment->next1()) {
                  if(segment->measure()->system()!=system()) break;
                  if(!segment->enabled() || segment==ss || segment==es || (segment->segmentType()&SegmentType::BarLineType)) continue;
                  const double x=segment->x()+segment->measure()->x();
                  if(x+segment->width()<qMin(p0.x(),p3.x()))continue;
                  if(x>qMax(p0.x(),p3.x()))break;
                  const auto shape=segment->staffShape(staffIdx()).translated(segment->pos()+segment->measure()->pos()-pos());
                  for(const auto& r:shape) {
                        if(r.width()<=0 || r.height()<=0)continue;
                        obstacles.append(QRectF(r).adjusted(-padding,-padding,padding,padding));
                        if(obstacles.size()>2048)break;
                        }
                  if(obstacles.size()>2048)break;
                  }
            // Native endpoint/control edits also constrain the automatic end tangents.
            points.front().locked=!ups(Grip::START).off.isNull() || !ups(Grip::BEZIER1).off.isNull();
            points.back().locked=!ups(Grip::END).off.isNull() || !ups(Grip::BEZIER2).off.isNull();
            const auto result=FreeSlur::avoid(points,obstacles,slur()->up(),sp);
            points=result.points;_freeCollisions=result.collisions;_freeLimited=result.limited;
            }
      for(int i=0;i<_freeGrips.size();++i) {
            auto& grips=_freeGrips[i];const auto& node=nodes[grips.index];
            const double tick=slur()->tick().ticks()+node.position*slur()->ticks().ticks();
            const double t=qBound(.00000001,(tick-first)/(last-first),.99999999);
            int j=1;while(j<points.size()-1 && std::abs(points[j].t-t)>.00000001)++j;
            const auto& p=points[j];grips.point=p.p;''')
change('libmscore/freeslur.cpp','grips.leftScale=(p.t-points[i].t)/3; grips.rightScale=(points[i+2].t-p.t)/3;','grips.leftScale=(p.t-points[j-1].t)/3; grips.rightScale=(points[j+1].t-p.t)/3;')
change('libmscore/freeslur.cpp','      if (_freeMode) undoResetProperty(Pid::FREE_SLUR_MODE);','      if (_freeMode) undoResetProperty(Pid::FREE_SLUR_MODE);\n      if (_freeAuto) undoResetProperty(Pid::FREE_SLUR_AUTO);')
p=mirror('libmscore/freeslur.cpp');s=p.read_text(encoding='utf8').replace('id==Pid::FREE_SLUR_MODE || id==Pid::FREE_SLUR_NODES','id==Pid::FREE_SLUR_MODE || id==Pid::FREE_SLUR_AUTO || id==Pid::FREE_SLUR_NODES');s=s.replace('      if(index%3==0) node.offset+=ed.delta/spatium();','      node.locked=true;\n      if(index%3==0) node.offset+=ed.delta/spatium();');p.write_bytes(s.encode('utf8'))
change('mscore/inspector/freeslurinspector.h','      QWidget* _details;','      QWidget* _details;\n      QCheckBox* _automatic;\n      QCheckBox* _locked;\n      QLabel* _result;')
change('mscore/inspector/freeslurinspector.h','            const int i=_choice->currentIndex();','''            const int i=_choice->currentIndex();
            QSignalBlocker lockBlock(_locked);_locked->setEnabled(i>=0);_locked->setChecked(i>=0 && _nodes[i].locked);''')
change('mscore/inspector/freeslurinspector.h','            _choice=new QComboBox(_details);','''            _automatic=new QCheckBox(tr("自动避让音符"),this);_automatic->setObjectName("freeSlurAuto");layout->addWidget(_automatic,3,0,1,3);
            _result=new QLabel(this);_result->setWordWrap(true);layout->addWidget(_result,4,0,1,3);
            connect(_automatic,&QCheckBox::clicked,this,[this](bool value) {
                  if(_owner)mscore->performanceEditor()->queueProperty(_owner,Pid::FREE_SLUR_AUTO,value);
                  });
            _locked=new QCheckBox(tr("锁定这个点和切线"),_details);_locked->setObjectName("freeSlurLock");grid->addWidget(_locked,7,0,1,3);
            connect(_locked,&QCheckBox::clicked,this,[this](bool value) {int i=_choice->currentIndex();if(i<0)return;_nodes[i].locked=value;commit(i);});
            auto restore=buttonForRestore(_details,grid);
            connect(restore,&QToolButton::clicked,this,[this] {
                  if(!_owner)return;_nodes.clear();auto editor=mscore->performanceEditor();
                  editor->queueProperty(_owner,Pid::FREE_SLUR_NODES,QString("[]"));
                  editor->queueProperty(_owner,Pid::FREE_SLUR_AUTO,true);refresh(-1);
                  });
            _choice=new QComboBox(_details);''')
change('mscore/inspector/freeslurinspector.h','   public:\n      QCheckBox* mode;','''      QToolButton* buttonForRestore(QWidget* host,QGridLayout* grid)
            {
            auto button=new QToolButton(host);button->setText(tr("恢复自动形状"));button->setObjectName("freeSlurRestoreAuto");grid->addWidget(button,8,0,1,3);
            button->setToolTip(tr("清除这条线的中间点并重新自动避让；可撤销。起点、终点和原有手柄偏移保留。"));return button;
            }
   public:
      QCheckBox* mode;''')
change('mscore/inspector/freeslurinspector.h','if(k<2) {if(k==0)_nodes[i].offset.setX(value);','_nodes[i].locked=true;if(k<2) {if(k==0)_nodes[i].offset.setX(value);')
change('mscore/inspector/freeslurinspector.h','多选时只共同设置模式。','手动调整会锁定该点；取消锁定后自动避让才会移动它。多选时只共同设置模式。')
change('mscore/inspector/freeslurinspector.h','            _details->setEnabled(single && owner->freeMode()); refresh(_choice->currentIndex()<0 ? 0:_choice->currentIndex());','''            _details->setEnabled(single && owner->freeMode());_automatic->setEnabled(single && owner->freeMode());
            if(!mscore->performanceEditor()->hasPending()) {QSignalBlocker block(_automatic);_automatic->setChecked(owner->freeAuto());}
            int collisions=0;bool limited=false;for(auto s:owner->spannerSegments()) {auto segment=toSlurSegment(s);collisions+=segment->freeCollisions();limited|=segment->freeLimited();}
            _result->setText(!owner->freeAuto() ? tr("手动形状：不会自动移动中间点。") : !owner->autoplace() ? tr("请先开启圆滑线的自动放置。") : limited ? tr("内容过密，保留形状；请手动调整。") : collisions ? tr("仍有拥挤位置：锁定点或高度限制可能使避让无法完成。") : tr("已自动避让；手动点和两端位置保留。"));
            refresh(_choice->currentIndex()<0 ? 0:_choice->currentIndex());''')
print('自由圆滑线模块和检视器修改已准备。')
