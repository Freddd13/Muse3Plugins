"""Sync only the guarded N6 files."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-162'
files=json.loads((OUT/'files.json').read_text('utf8'));record=OUT/'applied.json';previous=json.loads(record.read_text('utf8')) if record.is_file() else {}
pending=[]
for name,original in files.items():
    source=ROOT/'P2/native'/name;target=HOST/name;data=source.read_bytes()
    if source.suffix in ('.cpp','.h','.cmake','.md','.tsv','.inc') or name=='personal/VERSION':data=data.replace(b'\r\n',b'\n')
    actual=target.read_bytes() if target.is_file() else None
    if name=='personal/USER_GUIDE.md' and actual!=data:
        prior=OUT/'guide-last-native.md'
        ancestor=prior.read_bytes() if prior.is_file() else subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)
        paths=[OUT/('guide-'+label+'.md') for label in ('current','base','incoming')]
        for path,content in zip(paths,(actual,ancestor,data)):path.write_bytes(content)
        merged=subprocess.run(['git','merge-file','-p',*[str(p) for p in paths]],capture_output=True)
        if merged.returncode:raise ValueError('Guide needs review')
        prior.write_bytes(data);data=merged.stdout
        pending.append((name,source,target,data));continue
    digest=hashlib.sha256(actual).hexdigest() if actual is not None else None
    if actual!=data and digest not in (original,previous.get(name)):raise ValueError('Separate edit '+name)
    pending.append((name,source,target,data))
for name,source,target,data in pending:
    if name!='personal/USER_GUIDE.md' and source.read_bytes()!=data:source.write_bytes(data)
    if not target.is_file() or target.read_bytes()!=data:target.write_bytes(data)
    previous[name]=hashlib.sha256(data).hexdigest()
record.write_text(json.dumps(previous,indent=2),encoding='utf8');print('Synced',len(files),'N6 files')
