from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore';D=R/'staged057/native'
def read(k):
 p=R/'native'/k
 return (p if p.exists() else H/k).read_text(encoding='utf8')
def stage(k,s):
 p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
k='mscore/performanceeditor/performancepainting.cpp';p=D/k;s=p.read_text(encoding='utf8')
at=s.index('      double lastLabel = -1000;')
s=s[:at]+'''      if(comparisonTimeActive()){
            const double origin=_score->tempomap()->tick2time(_scroll->value());
            const double left=_score->tempomap()->tick2time(from),right=_score->tempomap()->tick2time(until);
            const double desired=80/(2*_viewport.pixelsPerQuarter);
            double step=.1;while(step<desired)step*=2;
            for(double seconds=std::ceil(left/step)*step;seconds<=right;seconds+=step){
                  const double x=PerformanceViewport::gutter+(seconds-origin)*2*_viewport.pixelsPerQuarter;
                  painter.setPen(QPen(c[PerformanceAppearance::Grid],.7));painter.drawLine(QPointF(x,surface==PerformanceSurface::Parameter?laneRect().top():0),QPointF(x,surface==PerformanceSurface::Parameter?laneRect().bottom():widget->height()));
                  if(surface==PerformanceSurface::Ruler){const int minutes=int(seconds)/60;const QString label=QString("%1:%2").arg(minutes).arg(seconds-minutes*60,4,'f',1,QChar('0'));painter.setPen(c[PerformanceAppearance::Text]);painter.drawText(QPointF(x+3,19),label);}
                  }
            painter.restore();return;
            }
'''+s[at:];p.write_bytes(s.encode())
k='mscore/performanceeditor/performancewheel.cpp';s=read(k).replace('记号力度 %4','力度参考线 %4').replace('QString::number(n.base));','QString::number(n.markBase>=0?n.markBase:n.base));');stage(k,s)
k='mscore/workflow/scoreworkflow.cpp';s=read(k).replace('{"repeats",repeats}};','{"repeats",repeats},{"velocityWriteModes",true}};',1);stage(k,s)
p=D/'mscore/performanceeditor/expressioncompare.cpp';s=p.read_text(encoding='utf8').replace('谱中 %6 → 拟采用 %7','谱中 %6 → 拟采用 %7\\n重音等演奏处理后的基础力度：%8').replace('.arg(qRound(_comparisonValues.value(nearest).value("target").toDouble())),_canvas);','.arg(qRound(_comparisonValues.value(nearest).value("target").toDouble())).arg(n.base),_canvas);');p.write_bytes(s.encode())
