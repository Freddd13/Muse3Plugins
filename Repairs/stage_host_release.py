"""Stage exact native release copies, while keeping later work in the working tree."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore'
def git(args,**kwargs):return subprocess.run(['git']+args,cwd=P,check=True,capture_output=True,**kwargs).stdout
paths=subprocess.run(['git','diff-tree','--no-commit-id','--name-only','-r','HEAD'],cwd=H,check=True,capture_output=True,text=True).stdout.splitlines()
for path in paths:
 target=P/path.removeprefix('share/plugins/') if path.startswith('share/plugins/') else R/'native'/path
 if not target.is_file():continue
 blob=git(['hash-object','-w','--stdin'],input=(H/path).read_bytes()).decode().strip()
 git(['update-index','--add','--cacheinfo','100644,'+blob+','+target.relative_to(P).as_posix()])
print('Staged exact release copies:',len(paths))
