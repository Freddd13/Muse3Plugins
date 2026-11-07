"""Sync the explicit N5 batch, retaining separate native edits."""
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/'muse3_dev/MuseScore'
OUT=ROOT/'P2/out/repair-161'
base=json.loads((OUT/'files.json').read_text('utf8'))
record=OUT/'applied.json'
applied=json.loads(record.read_text('utf8')) if record.is_file() else {}
pending=[]
for name,original in base.items():
    source=ROOT/'P2/native'/name;target=HOST/name
    data=source.read_bytes()
    if source.suffix in ('.cpp','.h','.cmake','.md','.tsv','.inc') or name=='personal/VERSION':
        data=data.replace(b'\r\n',b'\n')
    if source.read_bytes()!=data:source.write_bytes(data)
    actual=target.read_bytes() if target.is_file() else None
    if name=='personal/USER_GUIDE.md' and actual!=data:
        prior=OUT/'guide-last-native.md'
        ancestor=prior.read_bytes() if prior.is_file() else subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)
        paths=[OUT/('guide-'+label+'.md') for label in ('current','base','incoming')]
        for path,content in zip(paths,(actual,ancestor,data)):path.write_bytes(content)
        merge=subprocess.run(['git','merge-file','-p',*[str(p) for p in paths]],capture_output=True)
        if merge.returncode:raise ValueError('Guide merge requires review')
        prior.write_bytes(data);data=merge.stdout
        pending.append((name,target,data));continue
    digest=hashlib.sha256(actual).hexdigest() if actual is not None else None
    if actual!=data and digest not in (original,applied.get(name)):raise ValueError('Separate edits: '+name)
    pending.append((name,target,data))
for name,target,data in pending:
    if not target.is_file() or target.read_bytes()!=data:target.write_bytes(data)
    applied[name]=hashlib.sha256(data).hexdigest()
record.write_text(json.dumps(applied,indent=2),encoding='utf8')
print('Synced',len(pending),'N5 files')
