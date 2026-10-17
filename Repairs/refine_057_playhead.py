from pathlib import Path
R=Path(__file__).resolve().parent
for prefix in ['native','staged057/native']:
 p=R/prefix/'mscore/performanceeditor/performanceinteraction.cpp';s=p.read_text(encoding='utf8')
 s=s.replace('if (tick < _scroll->value() || tick > _scroll->value() + span * 0.85) {\n                  _automaticScroll = true; _scroll->setValue(qMax(0, tick - int(span * 0.12)));','const int shown=comparisonPlayTick(tick);\n            if (shown < _scroll->value() || shown > _scroll->value() + span * 0.85) {\n                  _automaticScroll = true; _scroll->setValue(qMax(0, shown - int(span * 0.12)));')
 s=s.replace('xForTick(previous, false)), newX = qRound(xForTick(tick, false))','xForTick(comparisonPlayTick(previous), false)), newX = qRound(xForTick(comparisonPlayTick(tick), false))')
 s=s.replace('tick-qRound((_canvas->width()-PerformanceViewport::gutter)*.35*DIVISION/_viewport.pixelsPerQuarter)','leftTickForAnchor(tick,PerformanceViewport::gutter+(_canvas->width()-PerformanceViewport::gutter)*.35)')
 p.write_bytes(s.encode())
 p=R/prefix/'mscore/performanceeditor/expressioncompare.cpp';s=p.read_text(encoding='utf8')
 s=s.replace('connect(workflowContext(),&WorkflowContext::changed,this,&PerformanceEditor::syncExpressionComparison);','''connect(workflowContext(),&WorkflowContext::changed,this,&PerformanceEditor::syncExpressionComparison);
      connect(workflowContext(),&WorkflowContext::auditionChanged,this,[this]{const auto mode=workflowContext()->audition().value("mode").toString();if(_comparisonButton->property("auditionMode").toString()!=mode){_comparisonButton->setProperty("auditionMode",mode);updateSurfaces();}});''')
 p.write_bytes(s.encode())
