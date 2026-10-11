"""Fetch pinned upstream source, never executables or repo metadata."""
from pathlib import Path
import urllib.request, json, base64, hashlib, tarfile, io

ROOT=Path(__file__).resolve().parent/'native/mscore/referenceaudio/vendor'
ROOT.mkdir(parents=True,exist_ok=True)
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Kumo-P1-source'}),timeout=40).read()
def save(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()

if __name__=='__main__':
    info=json.loads(get('https://api.github.com/repos/mackron/dr_libs/git/blobs/a631ae40f066076e41f2f655ffd2891b41ca3772'))
    info['html_url']='https://api.github.com/repos/mackron/dr_libs/git/blobs/a631ae40f066076e41f2f655ffd2891b41ca3772'
    payload=base64.b64decode(info['content'])
    assert hashlib.sha256(payload).hexdigest()=="997b7ee18de6e6b81e2a83f1ea9fc62aef25c62b28d48db95635f49e65de0a2f"
    mp3hash=save(ROOT/'dr_mp3.h',payload)
    errors=[]
    for url in ['https://codeberg.org/soundtouch/soundtouch/archive/2.3.3.tar.gz','https://www.surina.net/soundtouch/soundtouch-2.3.3.tar.gz']:
        try:
            archive=get(url)
            assert hashlib.sha256(archive).hexdigest()=="43b23dfac2f64a3aff55d64be096ffc7b73842c3f5665caff44975633a975a99"
            with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
                count=0
                for member in tar.getmembers():
                    pieces=Path(member.name).parts[1:]
                    if not member.isfile() or '..' in pieces:continue
                    p=Path(*pieces)
                    if (str(p).replace('\\','/').startswith(('include/','source/SoundTouch/')) and p.suffix in ('.h','.cpp')) or p.name in ('COPYING.TXT','README.html','AUTHORS'):
                        save(ROOT/'soundtouch'/p,tar.extractfile(member).read());count+=1
                if count<15:raise RuntimeError('Incomplete SoundTouch archive')
            save(ROOT/'SOURCES.json',json.dumps({'SoundTouch':{'version':'2.3.3','url':url,'sha256':hashlib.sha256(archive).hexdigest(),'license':'LGPL-2.1-or-later'},'dr_mp3':{'gitBlob':info['sha'],'sha256':mp3hash,'license':'MIT-0','url':info['html_url']}},indent=2).encode())
            print('Pinned source dependencies fetched:',count,'SoundTouch files');break
        except Exception as e:errors.append(str(e))
    else:raise RuntimeError(errors)
