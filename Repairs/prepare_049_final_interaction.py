from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
N=ROOT/'Repairs/native'
def edit(path,old,new):
 p=path;s=p.read_text(encoding='utf8');assert old in s,str(p)+' missing '+old[:70];p.write_text(s.replace(old,new),encoding='utf8',newline='\n')
edit(N/'mscore/performanceeditor/performanceeditor.h','QGridLayout *_topRow = nullptr, *_actionsRow = nullptr;','QGridLayout *_topRow = nullptr, *_actionsRow = nullptr;\n      bool _toolbarReady = false;')
edit(N/'mscore/performanceeditor/performanceeditor.cpp','setupUsabilityControls();setupExpressionComparison(); applyAppearance(); status();','setupUsabilityControls();setupExpressionComparison();\n      _toolbarReady = true; resizeEvent(nullptr); applyAppearance(); status();')
edit(N/'mscore/performanceeditor/performanceeditor.cpp','void PerformanceEditor::resizeEvent(QResizeEvent*)\n      {','void PerformanceEditor::resizeEvent(QResizeEvent*)\n      {\n      if (!_toolbarReady) return;')
edit(N/'mscore/performanceeditor/expressioncompare.cpp','_actionsRow->addWidget(_comparisonButton,_actionsRow->rowCount(),0);if(!_toolbarWidgets[1].isEmpty())_toolbarWidgets[1].append(_comparisonButton);','_actionsRow->addWidget(_comparisonButton,_actionsRow->rowCount(),0);')
edit(N/'mtest/mscore/performanceeditor/expression_compare_tests.inc','auto canvas=editor.findChild<QWidget*>("performanceParameterCanvas");','auto parameter=editor.findChild<QComboBox*>("performanceParameter");QVERIFY(parameter&&parameter->isVisible());\n            QVERIFY(!QRect(parameter->mapTo(&editor,QPoint()),parameter->size()).intersects(QRect(toggle->mapTo(&editor,QPoint()),toggle->size())));\n            auto canvas=editor.findChild<QWidget*>("performanceParameterCanvas");')
edit(N/'mscore/workflow/scoreworkflow.cpp','auto master=_score->masterScore();master->updateVelo();','auto master=_score->masterScore();master->updateVelo();if(_score!=master)_score->updateVelo();')
# Keep repeated sync runs from touching seq.cpp and recompiling it needlessly.
p=ROOT/'Repairs/apply_native.py'
edit(p," p.write_bytes(s.replace(anchor,anchor+period).encode('utf8'))"," updated=s.replace(anchor,anchor+period).encode('utf8')\n if p.read_bytes()!=updated:p.write_bytes(updated)")
edit(N/'mscore/performanceeditor/performanceeditor.h','      void fit(bool selection = false);','      void fit(bool selection = false);\n      void revealTick(int tick);')
p=N/'mscore/performanceeditor/performanceinteraction.cpp'
edit(p,'void PerformanceEditor::locateSelection()', '''void PerformanceEditor::revealTick(int tick)
      {
      if (!_score || !isVisible()) return;
      const double position=xForTick(tick,false);
      if(position<PerformanceViewport::gutter+24 || position>_canvas->width()-24){
            pauseFollow();_scroll->setValue(qMax(0,tick-qRound((_canvas->width()-PerformanceViewport::gutter)*.35*DIVISION/_viewport.pixelsPerQuarter)));
            }
      updateSurfaces();
      }
void PerformanceEditor::locateSelection()''')
p=N/'mscore/workflow/scoreworkflow.cpp'
edit(p,' view->moveCursor(Fraction::fromTicks(tick));',' view->moveCursor(Fraction::fromTicks(tick));\n if(auto editor=mscore->findChild<PerformanceEditor*>())editor->revealTick(tick);')
if '#include "mscore/performanceeditor/performanceeditor.h"' not in p.read_text(encoding='utf8'):
 edit(p,'#include "mscore/scoreview.h"','#include "mscore/scoreview.h"\n#include "mscore/performanceeditor/performanceeditor.h"')
