"""Stage only the current batch's appended guide section; leave concurrent edits intact."""
from pathlib import Path
import subprocess,sys
host=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
section=Path(__file__).parent/'out'/('guide-'+sys.argv[1]+'.txt')
previous=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=host)
new=previous+section.read_bytes()
blob=subprocess.check_output(['git','hash-object','-w','--stdin'],cwd=host,input=new).decode().strip()
subprocess.run(['git','update-index','--cacheinfo','100644',blob,'personal/USER_GUIDE.md'],cwd=host,check=True)
