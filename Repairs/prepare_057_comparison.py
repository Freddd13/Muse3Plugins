from pathlib import Path
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
D=R/'staged057/native'
def read(k):
    p=R/'native'/k
    return (p if p.exists() else H/k).read_text(encoding='utf8')
def stage(k,s):
    p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
k='mscore/performanceeditor/performanceeditor.h';s=read(k)
s=s.replace('#include "libmscore/score.h"','#include "libmscore/score.h"\n#include "libmscore/tempo.h"')
s=s.replace('QString dynamicText;','QString dynamicText;\n            int markBase = -1;')
s=s.replace('QToolButton* _comparisonButton=nullptr;','''QToolButton* _comparisonButton=nullptr;
      QComboBox* _comparisonView=nullptr;
      TempoMap _comparisonClock;
      QVector<QPair<int,int>> _comparisonPositions;
      int _comparisonEnd=0;
      bool _comparisonGuides=false;
      bool comparisonTimeActive()const;
      int comparisonDisplayTick(int)const;
      QVector<int> comparisonVisible(int,int)const;
      int comparisonPlayTick(int)const;
      int leftTickForAnchor(int,double)const;''')
stage(k,s)
k='mscore/performanceeditor/performanceeditor.cpp';s=read(k)
s=s.replace('cached.dynamicText=markVelocityAt(markNames,note->track(),tick);','cached.dynamicText=markVelocityAt(markNames,note->track(),tick);cached.markBase=stablePlayback?note->staff()->velocities().val(Fraction::fromTicks(tick)):-1;')
s=s.replace('int from = 0, until = _endTick;','int from = 0, until = comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick;')
s=s.replace('_viewport.pixelsPerQuarter = qBound(0.01, double(qMax(100, _canvas->width() - PerformanceViewport::gutter - PerformanceViewport::rightMargin)) * DIVISION / qMax(1, until - from), 1000.0);','''const double width=qMax(100,_canvas->width()-PerformanceViewport::gutter-PerformanceViewport::rightMargin);
      const double units=comparisonTimeActive()?qMax(.001,2*(_score->tempomap()->tick2time(until)-_score->tempomap()->tick2time(from))):double(qMax(1,until-from))/DIVISION;
      _viewport.pixelsPerQuarter=qBound(.01,width/units,1000.);''')
s=s.replace('if (!onScore) return PerformanceViewport::gutter + (tick - _scroll->value()) * _viewport.pixelsPerQuarter / DIVISION;','''if (!onScore) {
            const double units=comparisonTimeActive()?2*(_score->tempomap()->tick2time(tick)-_score->tempomap()->tick2time(_scroll->value())):double(tick-_scroll->value())/DIVISION;
            return PerformanceViewport::gutter+units*_viewport.pixelsPerQuarter;
            }''')
s=s.replace('if (!onScore) return qBound(0, qRound((x - PerformanceViewport::gutter) * DIVISION / _viewport.pixelsPerQuarter) + _scroll->value(), _endTick);','''if (!onScore) {
            const double units=(x-PerformanceViewport::gutter)/_viewport.pixelsPerQuarter;
            const int tick=comparisonTimeActive()?_score->tempomap()->time2tick(_score->tempomap()->tick2time(_scroll->value())+units*.5):qRound(units*DIVISION)+_scroll->value();
            return qBound(0,tick,comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick);
            }''')
stage(k,s)
k='mscore/performanceeditor/performancepainting.cpp';s=read(k)
s=s.replace('const int span = qMax(1, qRound(qMax(10, _canvas->width() - PerformanceViewport::gutter - PerformanceViewport::rightMargin) * DIVISION / _viewport.pixelsPerQuarter));','''const double units=qMax(10,_canvas->width()-PerformanceViewport::gutter-PerformanceViewport::rightMargin)/_viewport.pixelsPerQuarter;
      const int span=qMax(1,comparisonTimeActive()?_score->tempomap()->time2tick(_score->tempomap()->tick2time(_scroll->value())+units*.5)-_scroll->value():qRound(units*DIVISION));''')
s=s.replace('_scroll->setRange(0, qMax(0, _endTick - span));','_scroll->setRange(0, qMax(0, (comparisonTimeActive()?qMax(_endTick,_comparisonEnd):_endTick) - span));')
s=s.replace('const double x = xForTick(tick, false); painter.drawLine','const double x = xForTick(comparisonPlayTick(tick), false); painter.drawLine')
stage(k,s)
k='mscore/performanceeditor/performanceinteraction.cpp';s=read(k)
s=s.replace('tick - qRound((wheel->position().x() - PerformanceViewport::gutter) * DIVISION / _viewport.pixelsPerQuarter)','leftTickForAnchor(tick,wheel->position().x())')
stage(k,s)
k='mscore/performanceeditor/performanceux.cpp';s=read(k)
s=s.replace('记号力度','力度参考线')
s=s.replace('connect(actual,&QCheckBox::toggled,this,[](bool on){QSettings().setValue("performanceEditor/markVelocityLines",on);});','connect(actual,&QCheckBox::toggled,this,[this](bool on){QSettings().setValue(_comparisonGuides?"performanceEditor/comparisonVelocityLines":"performanceEditor/markVelocityLines",on);});')
s=s.replace('显示力度参考线线','显示力度参考线')
# Guide values describe dynamics; playback base also contains articulation and instrument processing.
s=s.replace('const QPointF point(x,yForValue(n.base,lane,onScore));','const int reference=n.markBase>=0?n.markBase:n.base;\n            const QPointF point(x,yForValue(reference,lane,onScore));')
s=s.replace('.arg(n.base).arg(n.dynamicText)','.arg(reference).arg(n.dynamicText)')
s=s.replace('.arg(n.dynamicText.isEmpty()?tr("力度参考线"):n.dynamicText).arg(n.base)','.arg(n.dynamicText.isEmpty()?tr("力度参考线"):n.dynamicText).arg(reference)')
stage(k,s)
k='mscore/performanceeditor/expressioncompare.cpp';s=read(k)
s=s.replace('#include <QPushButton>','#include <QPushButton>\n#include <QCheckBox>\n#include <QScrollBar>\n#include <QSettings>')
s=s.replace('空心显示谱中效果，实心显示拟采用效果；拖动实心条调整预览。使用力度后写入乐谱。','左侧中性色柱为谱中力度，右侧强调色柱为拟采用力度。拖动强调色柱调整；点击使用力度保存到乐谱。')
s=s.replace('_actionsRow->addWidget(_comparisonButton,_actionsRow->rowCount(),0);','''const int row=_actionsRow->rowCount();_actionsRow->addWidget(_comparisonButton,row,0);
      _comparisonView=new QComboBox(this);_comparisonView->setObjectName("performanceComparisonView");
      _comparisonView->addItems({tr("同音对比"),tr("真实播放时间对比")});_comparisonView->hide();
      _comparisonView->setCurrentIndex(qBound(0,QSettings().value("performanceEditor/comparisonView",0).toInt(),1));
      _comparisonView->setToolTip(tr("同音对比把原、新力度放在同一个谱位。真实播放时间按两种效果各自的秒数排列，用来查看速度变化。"));
      _actionsRow->addWidget(_comparisonView,row,1);
      connect(_comparisonView,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[this](int mode){cancelComparisonDrag();QSettings().setValue("performanceEditor/comparisonView",mode);surfaceResized(PerformanceSurface::Parameter);invalidateVisual();});''')
s=s.replace('cancelComparisonDrag();updateSelection();status(comparisonActive()?tr("调整拟采用效果 · 空心为谱中值，实心为预览值")','cancelComparisonDrag();syncExpressionComparison();updateSelection();status(comparisonActive()?tr("调整拟采用效果 · 中性色为谱中值，强调色为预览值")')
at=s.index('bool PerformanceEditor::comparisonActive()')
s=s[:at]+'''bool PerformanceEditor::comparisonTimeActive()const
      {return _score&&_comparisonView&&_comparisonView->currentIndex()==1&&comparisonActive();}
int PerformanceEditor::comparisonDisplayTick(int index)const
      {return comparisonTimeActive()?_comparisonValues.value(index).value("displayTick",_notes[index].tick).toInt():_notes[index].tick;}
int PerformanceEditor::leftTickForAnchor(int tick,double x)const
      {
      const double units=(x-PerformanceViewport::gutter)/_viewport.pixelsPerQuarter;
      return comparisonTimeActive()?_score->tempomap()->time2tick(_score->tempomap()->tick2time(tick)-units*.5):tick-qRound(units*DIVISION);
      }
int PerformanceEditor::comparisonPlayTick(int tick)const
      {
      if(!comparisonTimeActive()||workflowContext()->audition().value("mode").toString()!="candidate")return tick;
      return _score->tempomap()->time2tick(_comparisonClock.tick2time(tick));
      }
QVector<int> PerformanceEditor::comparisonVisible(int from,int until)const
      {
      auto indices=_intervals.query(from,until);
      if(comparisonTimeActive()){
            auto first=std::lower_bound(_comparisonPositions.cbegin(),_comparisonPositions.cend(),from,[](const QPair<int,int>& a,int t){return a.first<t;});
            for(auto it=first;it!=_comparisonPositions.cend()&&it->first<=until;++it)indices.append(it->second);
            std::sort(indices.begin(),indices.end());indices.erase(std::unique(indices.begin(),indices.end()),indices.end());
            }
      return indices;
      }
'''+s[at:]
s=s.replace('_comparisonValues.clear();_comparisonTempos=', '_comparisonValues.clear();_comparisonPositions.clear();_comparisonEnd=_endTick;_comparisonTempos=')
needle='if(available)for(auto value:candidate.value("velocity").toList())'
s=s.replace(needle,'''if(_score){_comparisonClock=*_score->tempomap();for(auto point:_comparisonTempos){auto t=point.toMap();_comparisonClock.setTempo(t.value("tick").toInt(),t.value("bpm").toDouble()/60.);}}
            if(available)for(auto value:candidate.value("velocity").toList())''')
s=s.replace('const auto target=value.toMap();const int tick=target.value("tick").toInt();','''auto target=value.toMap();const int tick=target.value("tick").toInt();
                  const int display=_score->tempomap()->time2tick(_comparisonClock.tick2time(tick));target["displayTick"]=display;
                  _comparisonEnd=qMax(_comparisonEnd,display+DIVISION);''')
s=s.replace('_comparisonValues.insert(int(it-_notes.cbegin()),target);break;','const int index=int(it-_notes.cbegin());_comparisonValues.insert(index,target);_comparisonPositions.append({display,index});break;')
s=s.replace('      const bool comparing=comparisonActive(),waiting=comparisonWaiting();','''      std::sort(_comparisonPositions.begin(),_comparisonPositions.end());
      const bool comparing=comparisonActive(),waiting=comparisonWaiting();
      _comparisonView->setVisible(available&&_comparisonButton->isChecked());
      const bool guides=comparing&&_parameter->currentIndex()==0;
      if(guides!=_comparisonGuides){_comparisonGuides=guides;if(auto check=findChild<QCheckBox*>("performanceActualVelocity")){
            QSignalBlocker block(check);_relativeActual=QSettings().value(guides?"performanceEditor/comparisonVelocityLines":"performanceEditor/markVelocityLines",!guides).toBool();check->setChecked(_relativeActual);}}
''')
start=s.index('            for(int i:_intervals.query(from,until))')
end=s.index('            }\n      else {',start)
s=s[:start]+'''            for(int i:comparisonVisible(from,until)){
                  const auto& note=_notes[i];if(!note.inScope||(!note.enabled&&!_ghostVoices))continue;
                  const auto lane=velocityLane(i,rect,false);if(lane.isEmpty())continue;
                  double old=NoteVelocity::effective(note.base,note.type,note.raw);if(rangeKind()==1)old=note.type==Note::ValueType::OFFSET_VAL?note.raw:NoteVelocity::offsetFor(note.base,note.raw);
                  const double x=xForNote(i,false),y=yForValue(old,lane),base=qBound(lane.top(),yForValue(rangeKind()==1?0:1,lane),lane.bottom());
                  QColor neutral=original;neutral.setAlpha(note.enabled?(_comparisonValues.contains(i)?160:45):25);
                  auto voice=_appearance.noteColor(qRound(old),note.track);voice.setAlpha(note.enabled?180:40);
                  painter.setPen(QPen(voice,note.selected?2:1));painter.setBrush(neutral);
                  painter.drawRect(QRectF(x-7,qMin(base,y),5,qMax(2.,qAbs(base-y))));
                  if(!_comparisonValues.contains(i))continue;
                  const double nextX=xForTick(comparisonDisplayTick(i),false)+2,target=yForValue(comparisonValue(i),lane);
                  QColor color=proposed;if(!note.enabled)color.setAlpha(40);
                  painter.setPen(QPen(note.selected?_appearance.colors[PerformanceAppearance::Selection]:voice,note.selected?2:1));painter.setBrush(color);
                  painter.drawRect(QRectF(nextX,qMin(base,target),5,qMax(2.,qAbs(base-target))));
                  if(i==_comparisonAnchor||(!_selectedIndices.isEmpty()&&i==_selectedIndices.front())){
                        const QString text=QString("%1 → %2").arg(NoteVelocity::effective(note.base,note.type,note.raw)).arg(qRound(_comparisonDraft.value(_comparisonValues.value(i).value("id").toString(),_comparisonValues.value(i).value("target").toDouble())));
                        const double w=painter.fontMetrics().horizontalAdvance(text)+10;QRectF badge(qBound(lane.left(),nextX+8,qMax(lane.left(),lane.right()-w)),lane.bottom()-19,w,18);
                        painter.fillRect(badge,_appearance.colors[PerformanceAppearance::Background]);painter.setPen(QPen(color,1));painter.drawRect(badge);painter.setPen(original);painter.drawText(badge,Qt::AlignCenter,text);
                        }
                  }
'''+s[end:]
s=s.replace('谱中：空心　拟采用：实心','谱中：中性色　拟采用：强调色')
s=s.replace('_intervals.query(tickForX(help->pos().x()-8,false),tickForX(help->pos().x()+8,false))','comparisonVisible(tickForX(help->pos().x()-12,false),tickForX(help->pos().x()+12,false))')
s=s.replace('qAbs(xForNote(index,false)-help->pos().x())>8','qAbs(xForTick(comparisonDisplayTick(index),false)+4-help->pos().x())>9')
s=s.replace('记号力度 %4 %5','力度参考线 %4：%5')
s=s.replace('.arg(n.dynamicText).arg(n.base)','.arg(n.dynamicText).arg(n.markBase)')
s=s.replace('有实心预览条','有强调色预览条')
s=s.replace('_intervals.query(tickForX(lane.left(),false),tickForX(lane.right(),false))','comparisonVisible(tickForX(lane.left(),false),tickForX(lane.right(),false))')
start=s.index('                  const auto nearby=_intervals.query')
end=s.index('                  if(_comparisonAnchor<0)return true;',start)
s=s[:start]+'''                  const auto nearby=comparisonVisible(tickForX(point.x()-12,false),tickForX(point.x()+12,false));
                  int originalIndex=-1;double originalDistance=1e20;
                  for(int index:nearby){const auto& n=_notes[index];if(!noteEditable(n))continue;const auto row=velocityLane(index,lane,false);if(!row.contains(point))continue;
                        const double sourceX=xForNote(index,false)-4.5;
                        double old=NoteVelocity::effective(n.base,n.type,n.raw);if(rangeKind()==1)old=n.type==Note::ValueType::OFFSET_VAL?n.raw:NoteVelocity::offsetFor(n.base,n.raw);
                        const double sourceDistance=qAbs(yForValue(old,row)-point.y());
                        if(qAbs(sourceX-point.x())<=4&&sourceDistance<originalDistance){originalDistance=sourceDistance;originalIndex=index;}
                        if(!_comparisonValues.contains(index))continue;
                        if(qAbs(xForTick(comparisonDisplayTick(index),false)+4.5-point.x())>5)continue;
                        const double distance=qAbs(yForValue(comparisonValue(index),row)-point.y())-(n.selected?100000.:0.);
                        if(distance<nearest){nearest=distance;_comparisonAnchor=index;}
                        }
                  if(originalIndex>=0&&_comparisonAnchor<0){selectIndices({originalIndex},mouse->modifiers(),true);status(tr("已选中谱中音符；拖动旁边的强调色柱调整拟采用力度。"));return true;}
'''+s[end:]
s=s.replace('const double x=xForNote(index,false);if(x<left','const double x=xForTick(comparisonDisplayTick(index),false)+4.5;if(x<left')
stage(k,s)
print('0.57 comparison staged')
