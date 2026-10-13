# coding: utf-8
"""Commit the verified algorithm release without other tasks' guide or AGENTS changes."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(repo,*args,input=None):return subprocess.check_output(['git',*args],cwd=repo,input=input)
for repo in [HOST,ROOT]:
 if git(repo,'diff','--cached','--name-only').strip():raise RuntimeError('There are already staged changes in '+str(repo))
 git(repo,'fetch','origin');upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}').decode().strip()
 if int(git(repo,'rev-list','--count','HEAD..'+upstream)):raise RuntimeError('Remote changes need merging in '+str(repo))
 git(repo,'diff','--check')
native=['audio/exports/exportmidi.cpp','audio/exports/midigate.h','audio/exports/midigatefile.cpp','audio/exports/midigatefile.h','libmscore/CMakeLists.txt','libmscore/handbracket.h','libmscore/handbracketanalysis.cpp','libmscore/pianohands.h','libmscore/symbol.cpp','mscore/midicrop/midicroppanel.cpp','mscore/plugin/api/arrangementsnapshot.cpp','mscore/plugin/api/pianohandanalysis.cpp','mscore/plugin/api/pianohandanalysis.h','mscore/plugin/api/readonlyanalysisjob.cpp','mscore/plugin/plugin.cmake','mtest/mscore/p0native/tst_p0native.cpp','mtest/mscore/p0native/longroot.mscx','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/ALGORITHM_REPAIR_VALIDATION.md','personal/docs/images/midi-040.png']
for folder,files in [('ArrangementAssistant',['ArrangementAssistant_MS3.qml','README.md','Rules.js']),('HarmonyAssistant',['Harmony.js','HarmonyAssistant_MS3.qml','Preferences.js','README.md','Timeline.js'])]:native += ['share/plugins/'+folder+'/'+name for name in files]
git(HOST,'add','--',*native)
blob=git(HOST,'hash-object','-w','--stdin',input=(ROOT/'Repairs/out/guide-index.md').read_bytes()).decode().strip();git(HOST,'update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md');git(HOST,'diff','--cached','--check')
print(git(HOST,'commit','-m','Improve contextual harmony, hand-use checks and protected MIDI releases').decode('utf8'),flush=True);git(HOST,'tag','personal-v0.40.0')
plugin=['ArrangementAssistant/ArrangementAssistant_MS3.qml','ArrangementAssistant/README.md','ArrangementAssistant/Rules.js','ArrangementAssistant/tests/test-rules.cjs','HarmonyAssistant/Harmony.js','HarmonyAssistant/HarmonyAssistant_MS3.qml','HarmonyAssistant/Preferences.js','HarmonyAssistant/README.md','HarmonyAssistant/Timeline.js','HarmonyAssistant/tests/test-context.cjs','Planning/REPAIR_IMPLEMENTATION.md','Repairs/USER_GUIDE.md','Repairs/apply_native.py','Repairs/prepare_algorithm_release.py','Repairs/commit_algorithm_release.py']
plugin += ['Repairs/native/'+name for name in native if (ROOT/'Repairs/native'/name).is_file()]
git(ROOT,'add','--',*plugin);git(ROOT,'diff','--cached','--check')
print(git(ROOT,'commit','-m','Improve harmony context and hand-aware checks; document protected MIDI release').decode('utf8'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.40.0');git(ROOT,'push','origin','main')
print('0.40两仓库修改已提交并推送。')
