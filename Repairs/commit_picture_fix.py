from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def git(*args,**kwargs):return subprocess.check_output(['git',*args],cwd=HOST,**kwargs).decode('utf8').strip()
git('add','--','mtest/mscore/p0native/tst_p0native.cpp','personal/docs/images/input-332-036.png','personal/CHANGELOG.md','personal/VERSION')
sha=git('hash-object','-w','--stdin',input=(ROOT/'out/guide-index.md').read_bytes());git('update-index','--cacheinfo','100644,'+sha+',personal/USER_GUIDE.md')
git('diff','--cached','--check');print(git('commit','-m','docs(notation): capture visible score examples and check screenshot content'))
git('tag','personal-v0.36.1');print(git('status','--short'))
