"""Fetch the pinned, BSD-licensed FFT sources used by the spectrum worker."""
from pathlib import Path
import hashlib, json, subprocess
ROOT=Path(__file__).resolve().parent
COMMIT='8f47a67f595a6641c566087bf5277034be64f24d'
FILES=('kiss_fft.c','kiss_fft.h','kiss_fftr.c','kiss_fftr.h','_kiss_fft_guts.h','kiss_fft_log.h','COPYING','LICENSES/BSD-3-Clause')
target=ROOT/'out/kissfft'
target.mkdir(parents=True,exist_ok=True)
checkout=ROOT/'out/kissfft-upstream'
if not (checkout/'.git').exists():
 subprocess.run(['git','clone','--depth','1','--branch','131.1.0','git@github.com:mborgerding/kissfft.git',str(checkout)],check=True)
actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
if actual!=COMMIT:raise RuntimeError('KISS FFT commit differs from the pinned source: '+actual)
manifest={'name':'KISS FFT','version':'131.1.0','commit':COMMIT,'license':'BSD-3-Clause','files':{}}
for name in FILES:
 path=target/name;url='https://raw.githubusercontent.com/mborgerding/kissfft/'+COMMIT+'/'+name
 data=subprocess.check_output(['git','show',COMMIT+':'+name],cwd=checkout)
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 manifest['files'][name]={'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(target/'SOURCES.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
print('KISS FFT',manifest['version'],COMMIT,len(FILES),'files')
