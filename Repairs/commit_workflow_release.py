# coding: utf-8
"""Commit only this release; keep the user's AGENTS and additional guide text."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(repo,*args,input=None):return subprocess.check_output(['git',*args],cwd=repo,input=input)
for repo in (HOST,ROOT):
 if git(repo,'diff','--cached','--name-only').strip():raise RuntimeError('已有暂存修改，请先核对。')
 git(repo,'fetch','origin');upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}').decode().strip()
 if int(git(repo,'rev-list','--count','HEAD..'+upstream)):raise RuntimeError('远端有新修改，需要合并。')
 git(repo,'diff','--check')
native=['mscore/CMakeLists.txt','mscore/musescore.cpp','mscore/seq.cpp','mscore/shortcut.cpp','mscore/performanceeditor/performanceeditor.cmake','mscore/performanceeditor/performanceeditor.cpp','mscore/performanceeditor/performanceeditor.h','mscore/performanceeditor/performancepainting.cpp','mscore/performanceeditor/workflowlanes.cpp','mscore/performanceeditor/workflowlanes.h','mscore/plugin/api/qmlpluginapi.cpp','mscore/plugin/api/qmlpluginapi.h','mscore/plugin/api/scoreobserver.h','mscore/plugin/plugin.cmake','mscore/referenceaudio/CMakeLists.txt','mscore/referenceaudio/audioreader.cpp','mscore/referenceaudio/audioreader.h','mscore/referenceaudio/mediaplugin.cpp','mscore/referenceaudio/mediaproject.cpp','mscore/referenceaudio/mediaproject.h','mscore/referenceaudio/pcmring.h','mscore/referenceaudio/projectfactory.h','mscore/referenceaudio/referencehost.h','mscore/workflow/referencebus.cpp','mscore/workflow/referencebus.h','mscore/workflow/referencefactory.cpp','mscore/workflow/referencefactory.h','mscore/workflow/referenceworkflow.cpp','mscore/workflow/workflowcontext.cpp','mscore/workflow/workflowcontext.h','mscore/workflow/workflowexpression.cpp','mtest/mscore/p1native/tst_p1native.cpp','mtest/mscore/p1native/reference_tests.inc','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/REFERENCE_WORKFLOW_VALIDATION.md','personal/docs/images/reference-041.png','personal/docs/images/expression-041.png','share/plugins/PerformanceExpression/Alignment.js','share/plugins/PerformanceExpression/PerformanceExpression_MS3.qml','share/plugins/ReferencePlayer/ReferencePlayer_MS3.qml']
git(HOST,'add','--',*native)
blob=git(HOST,'hash-object','-w','--stdin',input=(ROOT/'Repairs/out/guide-index.md').read_bytes()).decode().strip();git(HOST,'update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md');git(HOST,'diff','--cached','--check')
print(git(HOST,'commit','-m','Add shared reference audio playback and interactive expression comparison').decode('utf8'),flush=True);git(HOST,'tag','personal-v0.41.0')
plugin=['P1/tests/CMakeLists.txt','PerformanceExpression/Alignment.js','PerformanceExpression/PerformanceExpression_MS3.qml','ReferencePlayer/ReferencePlayer_MS3.qml','Repairs/USER_GUIDE.md','Repairs/apply_native.py','Repairs/prepare_workflow_release.py','Repairs/document_workflow_release.py','Repairs/extend_reference_ui.py','Repairs/commit_workflow_release.py','Repairs/tests/tst_referenceproject.cpp','Planning/REPAIR_IMPLEMENTATION.md']
plugin += ['Repairs/native/'+name for name in native if (ROOT/'Repairs/native'/name).is_file()]
git(ROOT,'add','--',*plugin);git(ROOT,'diff','--cached','--check')
print(git(ROOT,'commit','-m','Add multi-track reference controls and editor expression comparison').decode('utf8'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.41.0');git(ROOT,'push','origin','main')
print('0.41两仓库修改已提交并推送。')
