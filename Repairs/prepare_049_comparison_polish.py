from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def save(name,s):
 p=root/'native'/name;p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mscore/performanceeditor/performanceux.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8');start=s.index('void PerformanceEditor::paintOriginalVelocity(');end=s.index('void PerformanceEditor::rebuildScoreNoteRows()',start)
s=s[:start]+'''void PerformanceEditor::paintOriginalVelocity(QPainter& painter,const QRectF& rect,bool onScore)
      {
      if(rangeKind()!=0)return;
      QHash<int,QPointF> previous;
      QSet<QString> labelled;
      QVector<QRectF> labels;
      const int from=tickForX(rect.left(),onScore),until=tickForX(rect.right(),onScore);
      auto candidates=onScore?_systemIndices:_intervals.query(from,until);
      std::sort(candidates.begin(),candidates.end());
      for(int i:candidates){
            const auto& n=_notes[i];
            if(!n.inScope||(!n.enabled&&!_ghostVoices)||n.base<0)continue;
            const double x=xForNote(i,onScore);
            if(x<rect.left()||x>rect.right())continue;
            const auto lane=velocityLane(i,rect,onScore);if(lane.isEmpty())continue;
            const QPointF point(x,yForValue(n.base,lane,onScore));
            const int staff=n.track/VOICES,line=n.track;
            QColor color=_appearance.staves[staff%8];if(!n.enabled)color.setAlpha(45);
            painter.setPen(QPen(color,1,Qt::DashLine));
            if(previous.contains(line)){auto old=previous.value(line);painter.drawLine(old,QPointF(point.x(),old.y()));painter.drawLine(QPointF(point.x(),old.y()),point);}
            else painter.drawLine(QPointF(point.x()-4,point.y()),QPointF(point.x()+4,point.y()));
            previous[line]=point;
            const QString key=QString("%1:%2:%3").arg(staff).arg(n.base).arg(n.dynamicText);
            if(labelled.contains(key))continue;
            const QString text=tr("谱表 %1 · %2 %3").arg(staff+1).arg(n.dynamicText.isEmpty()?tr("记号力度"):n.dynamicText).arg(n.base);
            const double width=painter.fontMetrics().horizontalAdvance(text)+8,height=painter.fontMetrics().height()+2;
            const double offsets[4]={-height-3,3,-2*height-5,height+5};
            for(int attempt=0;attempt<12;++attempt){
                  const double left=qBound(lane.left(),point.x()+4+(attempt/4)*(width+6),qMax(lane.left(),lane.right()-width));
                  QRectF box(left,point.y()+offsets[attempt%4],width,height);
                  if(!lane.contains(box))continue;
                  bool overlaps=false;for(const auto& used:labels)if(box.intersects(used)){overlaps=true;break;}
                  if(overlaps)continue;
                  painter.setPen(QPen(color,1));painter.fillRect(box,_appearance.colors[PerformanceAppearance::Background]);painter.drawText(box.adjusted(4,0,-4,0),Qt::AlignVCenter,text);
                  labels.append(box);labelled.insert(key);break;
                  }
            }
      for(auto it=previous.cbegin();it!=previous.cend();++it){painter.setPen(QPen(_appearance.staves[(it.key()/VOICES)%8],1,Qt::DashLine));painter.drawLine(it.value(),QPointF(rect.right(),it.value().y()));}
      }
''' +s[end:];save(name,s)
name='mscore/performanceeditor/workflowlanes.cpp';s=(root/'native'/name).read_text(encoding='utf8')
s=s.replace('bool hasExpression=!expression.isEmpty();','const auto result=expression.value("result").toMap(),candidate=expression.value("candidate").toMap();bool hasExpression=!result.value("matches").toList().isEmpty()||!result.value("missing").toList().isEmpty()||!result.value("extra").toList().isEmpty()||!candidate.value("velocity").toList().isEmpty()||!candidate.value("tempos").toList().isEmpty();',1)
s=s.replace('candidate.value(mode->currentIndex() ? "tempos" : "velocity").toList().size();','workflowContext()->expression().value("applyCounts").toMap().value(mode->currentIndex()?"tempos":"velocity",candidate.value(mode->currentIndex() ? "tempos" : "velocity").toList().size()).toInt();',1)
save(name,s)
name='mscore/performanceeditor/expressioncompare.cpp';s=(root/'native'/name).read_text(encoding='utf8')
old='''                  for(int index:_intervals.query(tickForX(point.x()-8,false),tickForX(point.x()+8,false))){const auto& n=_notes[index];if(!n.enabled||!_comparisonValues.contains(index))continue;const auto row=velocityLane(index,lane,false);if(row.isEmpty()||!row.contains(point))continue;const double distance=qAbs(xForNote(index,false)-point.x())+qAbs(yForValue(comparisonValue(index),row)-point.y())*.05-(n.selected?2.:0.);if(distance<nearest){nearest=distance;_comparisonAnchor=index;}}'''
new='''                  const auto nearby=_intervals.query(tickForX(point.x()-8,false),tickForX(point.x()+8,false));int closestTick=-1;double closestX=9.;
                  for(int index:nearby){if(!noteEditable(_notes[index])||!_comparisonValues.contains(index))continue;const double d=qAbs(xForNote(index,false)-point.x());if(d<closestX){closestX=d;closestTick=_notes[index].tick;}}
                  for(int index:nearby){const auto& n=_notes[index];if(n.tick!=closestTick||!noteEditable(n)||!_comparisonValues.contains(index))continue;const auto row=velocityLane(index,lane,false);if(row.isEmpty()||!row.contains(point))continue;const double distance=qAbs(yForValue(comparisonValue(index),row)-point.y())-(n.selected?100000.:0.);if(distance<nearest){nearest=distance;_comparisonAnchor=index;}}'''
assert s.count(old)==1;s=s.replace(old,new)
at='      if(event->type()!=QEvent::MouseButtonPress'
index=s.index(at)
tooltip='''      if(event->type()==QEvent::ToolTip&&_parameter->currentIndex()==0){auto help=static_cast<QHelpEvent*>(event);int nearest=-1;double distance=1e20;for(int index:_intervals.query(tickForX(help->pos().x()-8,false),tickForX(help->pos().x()+8,false))){if(!_notes[index].enabled||!_comparisonValues.contains(index)||qAbs(xForNote(index,false)-help->pos().x())>8)continue;auto row=velocityLane(index,laneRect(),false);if(row.isEmpty())continue;double d=qAbs(yForValue(comparisonValue(index),row)-help->pos().y());if(d<distance){distance=d;nearest=index;}}if(nearest>=0){const auto& n=_notes[nearest];QToolTip::showText(help->globalPos(),tr("%1 · 谱表 %2 · 声部 %3\\n记号力度 %4 %5\\n谱中 %6 → 拟采用 %7").arg(n.name).arg(n.track/VOICES+1).arg(n.track%VOICES+1).arg(n.dynamicText).arg(n.base).arg(NoteVelocity::effective(n.base,n.type,n.raw)).arg(qRound(_comparisonValues.value(nearest).value("target").toDouble())),_canvas);return true;}}
'''
s=s[:index]+tooltip+s[index:];save(name,s)
print('Comparison keeps the selected note at the same onset; labels and applied counts follow the displayed scope')
