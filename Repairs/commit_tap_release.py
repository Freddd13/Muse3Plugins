# coding: utf-8
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=HOST,**kwargs).decode('utf8').strip()
paths=['mscore/CMakeLists.txt','mscore/inspector/inspector.cpp','mscore/inspector/inspectorTextLine.cpp','mscore/performanceeditor/parameteredit.cpp','mscore/scoreview.cpp','mscore/shortcut.cpp','mscore/taptempo/taptempo.cpp','mscore/taptempo/taptempo.h','mscore/taptempo/tapmark.cpp','mscore/taptempo/tapmark.h','mscore/workflow/workflowvariants.cpp','mtest/mscore/p1native/tst_p1native.cpp','mtest/mscore/p1native/tap_mark_tests.inc','personal/CHANGELOG.md','personal/docs/source-map.tsv','personal/docs/images/tap-035.png','personal/VERSION']
git('add','--',*paths)
sha=git('hash-object','-w','--stdin',input=(ROOT/'out/guide-index.md').read_bytes())
git('update-index','--cacheinfo','100644,'+sha+',personal/USER_GUIDE.md')
git('diff','--cached','--check')
print(git('diff','--cached','--stat'))
print(git('commit','-m','fix(tempo): preview Tap changes and compare equivalent workflow routing'))
git('tag','personal-v0.35.0')
print(git('status','--short'))
