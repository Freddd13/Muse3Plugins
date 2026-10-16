from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
name='mscore/performanceeditor/performanceux.cpp';p=root/'native'/name;s=p.read_text(encoding='utf8')
s=s.replace('      QHash<int,QPointF> previous;\n      QSet<QString> labelled;','      QHash<int,QPointF> previous;QHash<int,QColor> lineColors;\n      QSet<QString> labelled;',1)
old='''            if(previous.contains(line)){auto old=previous.value(line);painter.drawLine(old,QPointF(point.x(),old.y()));painter.drawLine(QPointF(point.x(),old.y()),point);}
            else painter.drawLine(QPointF(point.x()-4,point.y()),QPointF(point.x()+4,point.y()));
            previous[line]=point;'''
new='''            lineColors[line]=color;
            if(previous.contains(line)){auto old=previous.value(line);if(qAbs(old.y()-point.y())>.001){painter.drawLine(old,QPointF(point.x(),old.y()));painter.drawLine(QPointF(point.x(),old.y()),point);previous[line]=point;}}
            else previous[line]=point;'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('QPen(_appearance.staves[(it.key()/VOICES)%8],1,Qt::DashLine));painter.drawLine(it.value(),QPointF(rect.right(),it.value().y()));','QPen(lineColors.value(it.key()),1,Qt::DashLine));painter.drawLine(it.value(),QPointF(rect.right(),it.value().y()));',1)
p.write_text(s,encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
print('Repeated mark-velocity values paint as one horizontal segment')
