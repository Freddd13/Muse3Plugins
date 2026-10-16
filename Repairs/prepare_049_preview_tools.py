from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def save(name,text):
 p=root/'native'/name;p.write_text(text,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
name='mscore/performanceeditor/performanceeditor.h';s=(root/'native'/name).read_text(encoding='utf8').replace('bool _comparisonDragging=false;','bool _comparisonDragging=false,_comparisonDrawing=false;',1).replace('QPointF _comparisonPress;','QPointF _comparisonPress,_comparisonLast;',1);save(name,s)
name='mscore/performanceeditor/expressioncompare.cpp';s=(root/'native'/name).read_text(encoding='utf8')
s=s.replace('const bool tempo=_comparisonTempoTick>=0;','const bool tempo=_parameter->currentIndex()==1;',1)
s=s.replace('_comparisonPress=point;_comparisonAnchor=-1;','_comparisonPress=_comparisonLast=point;_comparisonDrawing=_tool->currentIndex()>0;_comparisonAnchor=-1;',1)
old='            if(_parameter->currentIndex()==0){double nearest=1e20;'
new='''            if(_comparisonDrawing){
                  if(_parameter->currentIndex()==0){const bool selected=!_selectedIndices.isEmpty();for(int index:_intervals.query(tickForX(lane.left(),false),tickForX(lane.right(),false)))if(noteEditable(_notes[index])&&_comparisonValues.contains(index)&&(!selected||_notes[index].selected))_comparisonStarts.insert(index,comparisonValue(index));if(_comparisonStarts.isEmpty()){status(tr("选中有实心预览条的音后，可以画一段新的力度。"));return true;}}
                  }
            else if(_parameter->currentIndex()==0){double nearest=1e20;'''
assert s.count(old)==1;s=s.replace(old,new)
old='            if(_comparisonTempoTick>=0){const double delta='
new='''            if(_comparisonDrawing){
                  const bool line=_tool->currentIndex()==2;const QPointF from=line?_comparisonPress:_comparisonLast;if(line)_comparisonDraft.clear();
                  const double left=qMin(from.x(),point.x())-.5,right=qMax(from.x(),point.x())+.5;
                  auto yAt=[&](double x){return qFuzzyCompare(from.x()+1,point.x()+1)?point.y():from.y()+(point.y()-from.y())*(x-from.x())/(point.x()-from.x());};
                  if(_parameter->currentIndex()==0)for(auto it=_comparisonStarts.cbegin();it!=_comparisonStarts.cend();++it){const int index=it.key();const double x=xForNote(index,false);if(x<left||x>right)continue;const auto row=velocityLane(index,lane,false);if(row.isEmpty())continue;double target=valueForY(yAt(x),row);if(rangeKind()==1)target=NoteVelocity::effective(_notes[index].base,Note::ValueType::OFFSET_VAL,qRound(target));_comparisonDraft.insert(_comparisonValues.value(index).value("id").toString(),qBound(1.,target,127.));}
                  else for(auto value:_comparisonTempos){const auto t=value.toMap();const int tick=t.value("tick").toInt();const double x=xForTick(tick,false);if(x>=left&&x<=right)_comparisonDraft.insert(QString::number(tick),qBound(5.,valueForY(yAt(x),lane),999.));}
                  _comparisonLast=point;
                  }
            else if(_comparisonTempoTick>=0){const double delta='''
assert s.count(old)==1;s=s.replace(old,new)
at='      if(!comparisonActive()){'
s=s.replace(at,'      if(_comparisonDragging&&(event->type()==QEvent::UngrabMouse||event->type()==QEvent::ApplicationDeactivate)){cancelComparisonDrag();updateSurfaces();return false;}\n'+at,1)
save(name,s)
# Repeated identical bases form one horizontal segment, including ghost styling.
name='mscore/performanceeditor/performanceux.cpp';s=(root/'native'/name).read_text(encoding='utf8')
s=s.replace('      QHash<int,QPointF> previous;\n      QSet<QString> labelled;','      QHash<int,QPointF> previous;QHash<int,QColor> lineColors;\n      QSet<QString> labelled;',1)
old='''            if(previous.contains(line)){auto old=previous.value(line);painter.drawLine(old,QPointF(point.x(),old.y()));painter.drawLine(QPointF(point.x(),old.y()),point);}
            else painter.drawLine(QPointF(point.x()-4,point.y()),QPointF(point.x()+4,point.y()));
            previous[line]=point;'''
new='''            lineColors[line]=color;
            if(previous.contains(line)){auto old=previous.value(line);if(qAbs(old.y()-point.y())>.001){painter.drawLine(old,QPointF(point.x(),old.y()));painter.drawLine(QPointF(point.x(),old.y()),point);previous[line]=point;}}
            else previous[line]=point;'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('QPen(_appearance.staves[(it.key()/VOICES)%8],1,Qt::DashLine));painter.drawLine(it.value(),QPointF(rect.right(),it.value().y()));','QPen(lineColors.value(it.key()),1,Qt::DashLine));painter.drawLine(it.value(),QPointF(rect.right(),it.value().y()));',1)
save(name,s)
print('Pencil/line preview gestures and compact mark-line painting prepared')
