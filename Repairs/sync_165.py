"""Copy this repair only, keeping the existing native guide edits."""
from pathlib import Path
import hashlib, json, subprocess
R=Path(__file__).resolve().parents[1]; H=R.parent/'muse3_dev/MuseScore'; O=R/'P2/out/repair-165'
files=json.loads((O/'files.json').read_text('utf8'))
prior=json.loads((O/'applied.json').read_text('utf8')) if (O/'applied.json').exists() else {}
for name,original in files.items():
    source=R/'P2/native'/name; target=H/name; data=source.read_bytes(); actual=target.read_bytes() if target.exists() else b''
    if source.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        data=data.replace(b'\r\n',b'\n')
    if name=='personal/USER_GUIDE.md':
        ancestor=(O/'guide-last.md').read_bytes() if (O/'guide-last.md').exists() else subprocess.check_output(['git','show','HEAD:'+name],cwd=H)
        paths=[O/('guide-'+n+'.md') for n in ('actual','base','ours')]
        for p,b in zip(paths,(actual,ancestor,data)):p.write_bytes(b)
        merged=subprocess.run(['git','merge-file','-p',*[str(p) for p in paths]],capture_output=True)
        if merged.returncode:raise ValueError('Guide needs review')
        (O/'guide-last.md').write_bytes(data);data=merged.stdout
    elif actual!=data and not (original is None and not target.exists()) and hashlib.sha256(actual).hexdigest() not in (original,prior.get(name)):
        raise ValueError('Other edit '+name)
    if actual!=data:target.write_bytes(data)
    prior[name]=hashlib.sha256(data).hexdigest()
(O/'applied.json').write_text(json.dumps(prior,indent=2),encoding='utf8')
print('Synced',len(files),'repair files.')
