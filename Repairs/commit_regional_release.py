# coding: utf-8
"""Commit only the completed repair batch, keeping other work unstaged."""
from pathlib import Path
import subprocess,json,sys
ROOT=Path(__file__).resolve().parents[1]
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(repo,*args,input=None):return subprocess.check_output(['git',*args],cwd=repo,input=input)
results=json.loads((ROOT/'P1/out/final-regression/summary.json').read_text(encoding='utf8'))
assert len(results)==7 and all(v['exit']==0 and v['counts'][1]=='0' for v in results.values())
assert (HOST/'personal/VERSION').read_text().strip()=='0.42.1'
assert (ROOT/'Repairs/out/region-042-install.log').exists()
for repo in (HOST,ROOT):
 staged=git(repo,'diff','--cached','--name-only').decode().splitlines()
 allowed={'ArrangementVariants/ArrangementVariants_MS3.qml','Planning/README.md','Planning/REPAIR_IMPLEMENTATION.md','Planning/TODO.md','Repairs/USER_GUIDE.md','Repairs/apply_native.py','Repairs/commit_regional_release.py','Repairs/document_regional_release.py','Repairs/prepare_regional_release.py','Repairs/finish_regional_core.py','Repairs/native/libmscore/regionalvariants.cpp','Repairs/native/libmscore/regionalvariants.h','Repairs/native/libmscore/scorefile.cpp','Repairs/native/libmscore/undo.cpp','Repairs/native/libmscore/undo.h','Repairs/native/mscore/workflow/regionalpanel.cpp','Repairs/native/mscore/workflow/regionalpanel.h','Repairs/native/mtest/mscore/p1native/regional_tests.inc','Repairs/native/mtest/mscore/p1native/tst_p1native.cpp'}
 if staged and not(repo==ROOT and '--resume-staging' in sys.argv and set(staged)<=allowed):raise RuntimeError('已有暂存修改，请先核对。')
 git(repo,'fetch','origin')
 upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}').decode().strip()
 if int(git(repo,'rev-list','--count','HEAD..'+upstream)):raise RuntimeError('远端有新修改，先合并。')
 git(repo,'diff','--check')
native=['libmscore/CMakeLists.txt','libmscore/regionalvariants.cpp','libmscore/regionalvariants.h','libmscore/scorefile.cpp','libmscore/undo.cpp','libmscore/undo.h','mscore/musescore.cpp','mscore/plugin/plugin.cmake','mscore/shortcut.cpp','mscore/workflow/regionalpanel.cpp','mscore/workflow/regionalpanel.h','mtest/mscore/p1native/tst_p1native.cpp','mtest/mscore/p1native/regional_tests.inc','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/REGIONAL_VARIANTS_VALIDATION.md','personal/docs/images/regional-042.png','share/plugins/ArrangementVariants/ArrangementVariants_MS3.qml']
git(HOST,'add','--',*native)
blob=git(HOST,'hash-object','-w','--stdin',input=(ROOT/'Repairs/out/guide-index.md').read_bytes()).decode().strip()
git(HOST,'update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md')
git(HOST,'diff','--cached','--check')
print(git(HOST,'commit','-m','Add regional staff and voice variants in one MSCZ with safe switching and compatibility export').decode('utf8'),flush=True)
git(HOST,'tag','personal-v0.42.1')
plugin=['ArrangementVariants/ArrangementVariants_MS3.qml','Planning/README.md','Planning/REPAIR_IMPLEMENTATION.md','Planning/TODO.md','Repairs/USER_GUIDE.md','Repairs/apply_native.py','Repairs/prepare_regional_release.py','Repairs/document_regional_release.py','Repairs/finish_regional_core.py','Repairs/commit_regional_release.py']
plugin+=['Repairs/native/'+path for path in native if (ROOT/'Repairs/native'/path).is_file()]
git(ROOT,'add','--',*plugin);git(ROOT,'diff','--cached','--check')
print(git(ROOT,'commit','-m','Complete regional variants and document the approved repair workflow').decode('utf8'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.42.1');git(ROOT,'push','origin','main')
print('0.42两仓库修改已提交并推送；其它任务修改未纳入。')
