# -*- coding: utf-8 -*-
"""Stage only this task, including a HEAD-based user-guide increment."""
from pathlib import Path
import subprocess
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore');base=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo)]+list(args)).decode('utf-8').strip()
assert git('rev-parse','HEAD')=='3dc1d38c837875befe292c7a73f4eecd82dd03cb','Native HEAD changed concurrently'
prior=set(git('diff','--cached','--name-only').splitlines())
marker='## 和声助手 1.5：'
work=(repo/'personal/USER_GUIDE.md').read_text(encoding='utf-8')
baseline=(base/'native/baseline-1.5/personal/USER_GUIDE.md').read_text(encoding='utf-8')
assert work.split(marker)[0].rstrip()==baseline.replace('当前个人版本 **0.21.0**','当前个人版本 **0.22.0**',1).rstrip(),'Concurrent user guide changed'
candidate=base/'native/user-guide-index-1.5.md'
assert work.split(marker)[1]==candidate.read_text(encoding='utf-8').split(marker)[1]
paths=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp',
 'mtest/mscore/scoreobserver/tst_scoreobserver.cpp','mtest/mscore/scoreobserver/high-treble.mscx',
 'personal/VERSION','personal/CHANGELOG.md','personal/docs/04-feature-map.md','personal/docs/10-score-observer.md',
 'personal/docs/README.md','personal/docs/source-map.tsv']
paths += ['share/plugins/HarmonyAssistant/'+p.name for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md']
assert prior<=set(paths+['personal/USER_GUIDE.md']),'Unexpected existing staged work'
git('add','--',*paths)
blob=git('hash-object','-w',str(candidate));git('update-index','--cacheinfo','100644',blob,'personal/USER_GUIDE.md')
staged=set(git('diff','--cached','--name-only').splitlines())
assert staged<=set(paths+['personal/USER_GUIDE.md']) and set(paths[:11]+['personal/USER_GUIDE.md'])<=staged
git('diff','--cached','--check')
print(git('diff','--cached','--stat'))
print(git('commit','-m','fix(harmony): redesign inspector and adapt chord marker placement'))
print('Native commit:',git('rev-parse','HEAD'))
print('Remaining unrelated work:',git('status','--short'))
