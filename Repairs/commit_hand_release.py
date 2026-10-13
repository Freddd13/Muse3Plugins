# coding: utf-8
"""Commit only this release; preserve the other task's guide and AGENTS edits."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(cwd,*args,input=None):return subprocess.check_output(['git',*args],cwd=cwd,input=input)
for repo in [HOST,ROOT]:
 if git(repo,'diff','--cached','--name-only').strip():raise RuntimeError('There are already staged changes in '+str(repo))
 git(repo,'fetch','origin')
 upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}').decode().strip()
 behind=int(git(repo,'rev-list','--count','HEAD..'+upstream))
 if behind:raise RuntimeError('Remote changes need merging in '+str(repo))
 git(repo,'diff','--check')
native=['libmscore/CMakeLists.txt','libmscore/handbracket.cpp','libmscore/handbracket.h','libmscore/symbol.cpp','libmscore/symbol.h','libmscore/tempotext.cpp','mscore/CMakeLists.txt','mscore/handbracketsettings.cpp','mscore/handbracketsettings.h','mscore/inspector/inspector.cpp','mscore/menus.cpp','mscore/palette/palettetree.cpp','mscore/plugin/api/arrangementsnapshot.cpp','mtest/mscore/performanceeditor/handsymbol_tests.inc','mtest/mscore/performanceeditor/tst_performanceeditor.cpp','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/HAND_MARKER_VALIDATION.md','personal/docs/images/hand-039.png','share/plugins/ArrangementAssistant/Rules.js']
git(HOST,'add','--',*native)
blob=git(HOST,'hash-object','-w','--stdin',input=(ROOT/'Repairs/out/guide-index.md').read_bytes()).decode().strip()
git(HOST,'update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md')
git(HOST,'diff','--cached','--check')
print(git(HOST,'commit','-m','Improve hand bracket placement and defaults; align restored tempo').decode('utf8'),flush=True)
git(HOST,'tag','personal-v0.39.0')
plugin=['ArrangementAssistant/Rules.js','ArrangementAssistant/tests/test-rules.cjs','Repairs/apply_native.py','Repairs/prepare_hand_release.py','Repairs/commit_hand_release.py','Repairs/USER_GUIDE.md','Repairs/native/libmscore/handbracket.cpp','Repairs/native/libmscore/handbracket.h','Repairs/native/libmscore/symbol.cpp','Repairs/native/libmscore/tempotext.cpp','Repairs/native/mscore/handbracketsettings.cpp','Repairs/native/mscore/handbracketsettings.h','Repairs/native/mscore/plugin/api/arrangementsnapshot.cpp','Repairs/native/mtest/mscore/performanceeditor/handsymbol_tests.inc','Repairs/native/mtest/mscore/performanceeditor/tst_performanceeditor.cpp']
git(ROOT,'add','--',*plugin);git(ROOT,'diff','--cached','--check')
print(git(ROOT,'commit','-m','Improve hand marker semantics, placement and saved shapes').decode('utf8'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.39.0');git(ROOT,'push','origin','main')
print('两仓库0.39修改已提交和推送；其它任务与后续和弦计算仍保留在工作区。')
