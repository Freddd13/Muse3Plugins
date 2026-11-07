"""Record the native score-video scope before implementation."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-164';OUT.mkdir(exist_ok=True)
file=OUT/'files.json';files=json.loads(file.read_text('utf8')) if file.is_file() else {}
for name in ['mscore/CMakeLists.txt','mscore/musescore.cpp','mscore/workflow/referencefactory.cpp','mscore/workflow/referencefactory.h','mscore/referenceaudio/CMakeLists.txt','mscore/referenceaudio/mediaplugin.cpp','mscore/workflow/workspaceviews.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp','mtest/mscore/spectrum/tst_spectrum.cpp']:
    if name in files:continue
    data=(HOST/name).read_bytes();files[name]=hashlib.sha256(data).hexdigest();path=ROOT/'P2/native'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
for name in ['mscore/scorevideo/scorevideo.h','mscore/scorevideo/scorevideo.cpp','mscore/scorevideo/scorevideoframe.cpp','mscore/scorevideo/scorevideotimeline.cpp','mscore/scorevideo/scorevideoexport.h','mscore/scorevideo/scorevideoexport.cpp','mscore/scorevideo/scorevideopanel.h','mscore/scorevideo/scorevideopanel.cpp','mscore/referenceaudio/mediaexportfactory.h','mscore/referenceaudio/mediaexport.h','mscore/referenceaudio/mediaexport.cpp','mtest/mscore/pluginhost/scorevideo_164_tests.inc']:
    files.setdefault(name,None);(ROOT/'P2/native'/name).parent.mkdir(parents=True,exist_ok=True)
file.write_text(json.dumps(files,indent=2),encoding='utf8')
for old,new in [('sync_163.py','sync_164.py'),('build_163.py','build_164.py'),('run_163_checks.py','run_164_checks.py')]:
    text=(ROOT/'Repairs'/old).read_text('utf8').replace('repair-163','repair-164').replace('N7','N8')
    if old.startswith('build'):text=text.replace('163','164')
    target=ROOT/'Repairs'/new
    if not target.is_file():target.write_text(text,encoding='utf8',newline='\n')
