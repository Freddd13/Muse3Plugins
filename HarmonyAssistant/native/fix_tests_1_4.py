from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8').replace('#include "libmscore/measure.h"','#include "libmscore/measure.h"\n#include "libmscore/system.h"\n#include "libmscore/page.h"')
s=s.replace('score->selectRange(segment,score->lastSegment(),0,1);','score->selection().setRange(segment,score->lastSegment(),0,1);score->selection().update();')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
