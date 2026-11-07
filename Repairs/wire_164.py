from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];N=R/'P2/native';H=R.parent/'muse3_dev/MuseScore';O=R/'P2/out/repair-164'
manifest=O/'files.json';files=json.loads(manifest.read_text('utf8'))
name='mscore/workflow/toolicons.cpp'
if name not in files:
    data=(H/name).read_bytes();files[name]=hashlib.sha256(data).hexdigest();(N/name).write_bytes(data)
p=N/name;t=p.read_text('utf8')
if 'key == "video"' not in t:
    t=t.replace('"range", "hand"}.contains','"range", "hand", "video"}.contains')
    t=t.replace('      } else if (key == "settings") {','      } else if (key == "video") {\n            p.drawRoundedRect(QRectF(1.5,2,13,12),1,1);\n            for(int x:{4,8,12}){p.drawLine(x,2,x,4);p.drawLine(x,12,x,14);}\n            p.drawLine(4,6,12,6);p.drawLine(4,8.5,9,8.5);\n            p.drawLine(10,8,10,11);p.drawLine(10,11,12,10);\n      } else if (key == "settings") {',1)
    p.write_text(t,encoding='utf8',newline='\n')
p=N/'mscore/CMakeLists.txt';t=p.read_text('utf8')
if 'scorevideo/scorevideopanel.cpp' not in t:t=t.replace('      scorevideo/scorevideo.cpp','      scorevideo/scorevideopanel.cpp scorevideo/scorevideopanel.h scorevideo/scorevideoexport.cpp scorevideo/scorevideoexport.h\n      scorevideo/scorevideo.cpp',1)
p.write_text(t,encoding='utf8',newline='\n')
p=N/'mscore/musescore.cpp';t=p.read_text('utf8')
if '#include "scorevideo/scorevideopanel.h"' not in t:t='#include "scorevideo/scorevideopanel.h"\n'+t
t=t.replace('"kumo-vst"}) {','"kumo-vst", "kumo-score-video"}) {',1)
t=t.replace('action->setIcon(personalToolIcon(name));','action->setIcon(QString(name)=="kumo-score-video"?componentToolIcon("video"):personalToolIcon(name));',1)
if 'addScoreVideoAction(menuTools);' not in t:t=t.replace('      addReferenceActions(menuTools);','      addReferenceActions(menuTools);\n      addScoreVideoAction(menuTools);',1)
p.write_text(t,encoding='utf8',newline='\n');manifest.write_text(json.dumps(files,indent=2),encoding='utf8')
