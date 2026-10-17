from pathlib import Path
R=Path(__file__).resolve().parent
for prefix in ['native','staged057/native']:
 p=R/prefix/'mscore/performanceeditor/expressioncompare.cpp';s=p.read_text(encoding='utf8')
 s=s.replace('(_comparisonValues.contains(i)?160:45)','(_comparisonValues.contains(i)?210:45)')
 s=s.replace('auto voice=_appearance.noteColor(qRound(old),note.track);voice.setAlpha(note.enabled?180:40);','QColor voice=MScore::selectColor[note.track%VOICES];voice.setAlpha(note.enabled?(_comparisonValues.contains(i)?180:45):25);')
 s=s.replace('QRectF(x-7,qMin(base,y),5,','QRectF(x-9,qMin(base,y),7,').replace('QRectF(nextX,qMin(base,target),5,','QRectF(nextX,qMin(base,target),7,')
 needle='''                  }
            }
      else {
            QPolygonF old,now;'''
 replacement='''                  }
            // End caps keep each simultaneous note visible when filled bars overlap.
            for(int i:comparisonVisible(from,until)){
                  const auto& note=_notes[i];if(!note.inScope||(!note.enabled&&!_ghostVoices)||!_comparisonValues.contains(i))continue;
                  const auto lane=velocityLane(i,rect,false);if(lane.isEmpty())continue;
                  const double x=xForTick(comparisonDisplayTick(i),false)+2,y=yForValue(comparisonValue(i),lane);
                  QColor edge=original;edge.setAlpha(note.enabled?220:40);painter.setPen(QPen(edge,note.selected?2:1));painter.drawLine(QPointF(x-1,y),QPointF(x+8,y));
                  if(note.selected){painter.setBrush(proposed);painter.drawEllipse(QPointF(x+3.5,y),3,3);}
                  }
            }
      else {
            QPolygonF old,now;'''
 assert needle in s;s=s.replace(needle,replacement,1)
 s=s.replace('painter.setPen(original);painter.drawText(rect.adjusted(6,3,-6,-3),Qt::AlignTop|Qt::AlignRight,tr("谱中：中性色　拟采用：强调色"));painter.restore();','''const QString oldLabel=tr("谱中"),newLabel=tr("拟采用");const double a=painter.fontMetrics().horizontalAdvance(oldLabel),b=painter.fontMetrics().horizontalAdvance(newLabel),x=rect.right()-a-b-54,y=rect.top()+6;
      painter.fillRect(QRectF(x,y+2,8,8),original);painter.setPen(original);painter.drawText(QPointF(x+12,y+painter.fontMetrics().ascent()),oldLabel);
      painter.fillRect(QRectF(x+a+28,y+2,8,8),proposed);painter.drawText(QPointF(x+a+40,y+painter.fontMetrics().ascent()),newLabel);painter.restore();''')
 p.write_bytes(s.encode())
 p=R/prefix/'mscore/performanceeditor/performancepainting.cpp';s=p.read_text(encoding='utf8').replace('double step=.1;while(step<desired)step*=2;','const double magnitude=std::pow(10.,std::floor(std::log10(desired)));const double ratio=desired/magnitude;const double step=magnitude*(ratio<=1?1:ratio<=2?2:ratio<=5?5:10);');p.write_bytes(s.encode())
 p=R/prefix/'mtest/mscore/performanceeditor/expression_compare_tests.inc';s=p.read_text(encoding='utf8').replace('score->undoRedo(true,&edit);revision=observer.analysisRevision();candidate["revision"]=revision;','score->undoRedo(true,&edit);revision=observer.analysisRevision();candidate["revision"]=revision;for(auto& value:values){auto v=value.toMap();v["target"]=60+v["index"].toInt()*25;value=v;}candidate["velocity"]=values;');p.write_bytes(s.encode())
