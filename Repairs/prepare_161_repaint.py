from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
name='mscore/performanceeditor/performancewheel.cpp';path=NATIVE/name
text=path.read_text('utf8')
if '#include "timingeditor.h"' not in text:text=text.replace('#include "performanceeditor.h"','#include "performanceeditor.h"\n#ifdef SCRIPT_INTERFACE\n#include "timingeditor.h"\n#endif',1)
old='      if(_noteCanvas->isVisible())buildGeometry();'
new='''#ifdef SCRIPT_INTERFACE
      if(_timingEditor)_timingEditor->repaintNote(index);
#endif
'''+old
if new not in text:
    if old not in text:raise ValueError('Wheel repaint section')
    text=text.replace(old,new,1)
path.write_bytes(text.encode('utf8'))
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
if name not in files:files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest()
record.write_text(json.dumps(files,indent=2),encoding='utf8')
