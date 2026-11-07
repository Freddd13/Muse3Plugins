"""Snapshot the explicit N7 scope before editing."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-163';OUT.mkdir(exist_ok=True)
record=OUT/'files.json';files=json.loads(record.read_text('utf8')) if record.is_file() else {}
for name in ['mscore/workflow/referencefactory.cpp','mscore/workflow/workflowdocument.cpp','mscore/plugin/plugin.cmake','mscore/referenceaudio/mediaproject.h','mscore/referenceaudio/mediaproject.cpp','share/workflow/panels/ReferencePlayer/ReferencePlayer.view.qml','mtest/mscore/pluginhost/tst_pluginhost.cpp']:
    if name in files:continue
    source=HOST/name;data=source.read_bytes();files[name]=hashlib.sha256(data).hexdigest();target=ROOT/'P2/native'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
for name in ['mscore/workflow/referencecontrols.cpp','mscore/workflow/referencecontrols.h','mtest/mscore/pluginhost/reference_163_tests.inc']:files.setdefault(name,None)
record.write_text(json.dumps(files,indent=2),encoding='utf8')
script=(ROOT/'Repairs/sync_162.py').read_text('utf8').replace('repair-162','repair-163').replace('N6','N7')
(ROOT/'Repairs/sync_163.py').write_text(script,encoding='utf8',newline='\n')
script=(ROOT/'Repairs/build_162.py').read_text('utf8').replace('162','163').replace('N6','N7')
(ROOT/'Repairs/build_163.py').write_text(script,encoding='utf8',newline='\n')
script=(ROOT/'Repairs/run_162_checks.py').read_text('utf8').replace('repair-162','repair-163').replace('N6','N7')
script=script.replace("str(OUT/'long-audio')","str(ROOT/'P2/out/repair-162/long-audio')")
(ROOT/'Repairs/run_163_checks.py').write_text(script,encoding='utf8',newline='\n')
