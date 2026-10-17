from pathlib import Path
R=Path(__file__).resolve().parent/'staged057/native/mscore/performanceeditor'
p=R/'performanceeditor.h';s=p.read_text(encoding='utf8').replace('bool _comparisonGuides=false;','bool _comparisonGuides=false, _comparisonTime=false;');p.write_bytes(s.encode())
p=R/'expressioncompare.cpp';s=p.read_text(encoding='utf8')
s=s.replace('_comparisonView->setToolTip(', '_comparisonTime=_comparisonView->currentIndex()==1;\n      _comparisonView->setToolTip(',1)
s=s.replace('cancelComparisonDrag();QSettings().setValue("performanceEditor/comparisonView",mode);surfaceResized(PerformanceSurface::Parameter);invalidateVisual();','''cancelComparisonDrag();const double center=_canvas->width()*.5;const int anchor=tickForX(center,false);_comparisonTime=mode==1;
            QSettings().setValue("performanceEditor/comparisonView",mode);surfaceResized(PerformanceSurface::Parameter);_scroll->setValue(qMax(0,leftTickForAnchor(anchor,center)));invalidateVisual();''')
s=s.replace('_comparisonView->currentIndex()==1&&comparisonActive()','_comparisonTime&&comparisonActive()')
s=s.replace('                  }\n            }\n      std::sort(_comparisonPositions.begin(),_comparisonPositions.end());','                  }\n            std::sort(_comparisonPositions.begin(),_comparisonPositions.end());\n            }')
p.write_bytes(s.encode())
p=R/'performanceux.cpp';s=p.read_text(encoding='utf8').replace('谱表 %1 · 力度参考线／谱中力度','谱表 %1 · 参考线／谱中力度');p.write_bytes(s.encode())
