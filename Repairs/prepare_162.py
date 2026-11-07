"""Start the fixed-spectrum batch from the actual native files."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162'
OUT.mkdir(exist_ok=True)
record=OUT/'files.json';files=json.loads(record.read_text('utf8')) if record.is_file() else {}
names=['mscore/referenceaudio/spectrum.cpp','mscore/referenceaudio/spectrum.h','mscore/referenceaudio/spectrumsession.cpp','mscore/referenceaudio/spectrumsession.h','mscore/referenceaudio/CMakeLists.txt']
for name in names:
    if name in files:continue
    source=HOST/name;target=NATIVE/name
    if subprocess.check_output(['git','diff','--',str(target)],cwd=ROOT).strip():raise ValueError('Separate mirror edits: '+name)
    target.write_bytes(source.read_bytes());files[name]=hashlib.sha256(source.read_bytes()).hexdigest()
for name in ('mscore/referenceaudio/spectrumprojection.cpp','mscore/referenceaudio/spectrumprojection.h'):
    files.setdefault(name,None)
def edit(name,old,new):
    path=NATIVE/name;text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError('Missing section '+name+' '+old[:50])
    path.write_bytes(text.replace(old,new,1).encode('utf8'))
edit('mscore/referenceaudio/spectrum.cpp','stream << quint32(3)','stream << quint32(4)')
edit('mscore/referenceaudio/CMakeLists.txt','spectrum.cpp spectrumsession.cpp','spectrum.cpp spectrumprojection.cpp spectrumprojection.h spectrumsession.cpp')
edit('mscore/referenceaudio/spectrumsession.h','    Q_PROPERTY(bool busy READ busy NOTIFY changed)','    Q_PROPERTY(bool busy READ busy NOTIFY changed)\n    Q_PROPERTY(bool backgroundBusy READ backgroundBusy NOTIFY changed)')
edit('mscore/referenceaudio/spectrumsession.h','    bool _busy = false;','    bool _busy = false, _backgroundBusy = false;\n    int _preparedBlocks=0, _totalBlocks=0, _backgroundComputed=0;')
edit('mscore/referenceaudio/spectrumsession.h','    bool busy() const { return _busy; }','    bool busy() const { return _busy; }\n    bool backgroundBusy() const { return _backgroundBusy; }')
edit('mscore/referenceaudio/spectrumsession.cpp','#include "spectrum.h"','#include "spectrum.h"\n#include "spectrumprojection.h"') if '#include "spectrum.h"' in (NATIVE/'mscore/referenceaudio/spectrumsession.cpp').read_text('utf8') else edit('mscore/referenceaudio/spectrumsession.cpp','#include "spectrumsession.h"','#include "spectrumsession.h"\n#include "spectrumprojection.h"')
edit('mscore/referenceaudio/spectrumsession.cpp','    _pending.clear();','    _pending.clear();_backgroundBusy=false;')
edit('mscore/referenceaudio/spectrumsession.cpp','{"blockMs",4000}};','{"blockMs",4000},{"canonicalRows",1024},{"preparedBlocks",_preparedBlocks},{"totalBlocks",_totalBlocks},{"backgroundComputed",_backgroundComputed},{"backgroundBusy",_backgroundBusy}};')
edit('mscore/referenceaudio/spectrumsession.cpp','    ++_generation;\n    if (_busy)', '    ++_generation;\n    if(_cancel)*_cancel=true;\n    if (_busy)')
path=NATIVE/'mscore/referenceaudio/spectrumsession.cpp';text=path.read_text('utf8');start=text.index('void ReferenceSpectrumSession::begin(');end=text.index('void ReferenceSpectrumSession::estimateTempo(',start)
text=text[:start]+(ROOT/'Repairs/session_162.inc').read_text('utf8')+'\n\n'+text[end:];path.write_bytes(text.encode('utf8'))
record.write_text(json.dumps(files,indent=2),encoding='utf8');print('Prepared',len(files),'spectrum files')
