"""Keep each edited text file in the line-ending style already stored in Git."""
from pathlib import Path
import subprocess,os
ROOT=Path(__file__).resolve().parent.parent
roots=[ROOT]
if '--host' in __import__('sys').argv: roots.append(ROOT.parent/'muse3_dev/MuseScore')
for repo in roots:
 names=subprocess.check_output(['git','diff','--name-only'],cwd=repo).decode('utf8').splitlines()
 count=0
 for name in names:
  if name in ['AGENTS.md','personal/USER_GUIDE.md']:continue
  path=repo/name
  if not path.is_file():continue
  before=subprocess.check_output(['git','show','HEAD:'+name],cwd=repo)
  after=path.read_bytes()
  if b'\0' in before or b'\0' in after:continue
  crlf=before.count(b'\r\n')
  lf=before.count(b'\n')
  target=after.replace(b'\r\n',b'\n')
  if crlf>lf/2:target=target.replace(b'\n',b'\r\n')
  if target!=after:
   stamp=path.stat();path.write_bytes(target);os.utime(path,ns=(stamp.st_atime_ns,stamp.st_mtime_ns));count+=1
 print(str(repo),count,'text files kept in their stored line-ending style',flush=True)
