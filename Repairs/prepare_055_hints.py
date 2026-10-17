from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
s=(H/'mscore/workflow/positionhint.cpp').read_text(encoding='utf8')
a='''            const QPoint top(qBound(3, qRound(first.left()), qMax(3,width()-size.width()-3)),
                             qBound(3, qRound(first.top())-size.height()-4, qMax(3,height()-size.height()-3)));
            const QRect label(top,size);'''
b='''            const QVector<QPointF> candidates{{first.left(),first.top()-size.height()-8},{first.right()+8,first.top()},{first.left(),first.bottom()+8},{first.left()-size.width()-8,first.top()},{3.,3.},{qreal(width()-size.width()-3),3.}};
            QRect label;double best=1e30;
            for(auto at:candidates){QRect candidate(QPoint(qBound(3,qRound(at.x()),qMax(3,width()-size.width()-3)),qBound(3,qRound(at.y()),qMax(3,height()-size.height()-3))),size);double cost=QLineF(candidate.center(),first.center()).length();for(const auto& box:_boxes){const auto overlap=QRectF(candidate).intersected(_view->matrix().mapRect(box).adjusted(-4,-6,4,6));cost+=overlap.width()*overlap.height()*1000;}if(cost<best){best=cost;label=candidate;}}'''
assert a in s;s=s.replace(a,b,1)
s=s.replace('      return {{"x",global.x()}', '''      const auto localMeasure=view->matrix().mapRect(element->findMeasure()->canvasBoundingRect()).toAlignedRect();
      const QRect measureBox(view->mapToGlobal(localMeasure.topLeft()),localMeasure.size());
      const QRect viewport(view->mapToGlobal(QPoint()),view->size());
      return {{"measureX",measureBox.x()},{"measureY",measureBox.y()},{"measureWidth",measureBox.width()},{"measureHeight",measureBox.height()},
              {"viewX",viewport.x()},{"viewY",viewport.y()},{"viewWidth",viewport.width()},{"viewHeight",viewport.height()},{"x",global.x()}''',1)
p=R/'native/mscore/workflow/positionhint.cpp';p.write_bytes(s.encode())
