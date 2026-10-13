from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=HOST,**kwargs).decode('utf8').strip()
assert not git('diff','--cached','--name-only'),'已有其它任务的暂存内容，先保留它们。'
git('fetch','origin');assert git('rev-list','--left-right','--count','HEAD...origin/3.x')=='0\t0','远端有变化，先合并。'
paths=['libmscore/CMakeLists.txt','libmscore/freeslur.cpp','libmscore/freeslur.h','libmscore/freesluravoidance.cpp','libmscore/property.cpp','libmscore/property.h','libmscore/slur.cpp','libmscore/slur.h','mscore/inspector/freeslurinspector.h','mtest/mscore/performanceeditor/freeslur_tests.inc','mtest/mscore/performanceeditor/tst_performanceeditor.cpp','personal/CHANGELOG.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/FREE_SLUR_VALIDATION.md','personal/docs/images/slur-038.png']
git('add','--',*paths)
sha=git('hash-object','-w','--stdin',input=(ROOT/'out/guide-index.md').read_bytes());git('update-index','--cacheinfo','100644,'+sha+',personal/USER_GUIDE.md')
git('diff','--cached','--check');print(git('diff','--cached','--stat'));print(git('commit','-m','feat(slur): bounded automatic avoidance with protected manual nodes'))
git('tag','personal-v0.38.0');print(git('status','--short'))
