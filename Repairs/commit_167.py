"""Commit the inspected repair without including unrelated local work."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R=Path(__file__).resolve().parents[1]
H=R.parent/'muse3_dev/MuseScore'
N=R/'P2/native'
O=R/'P2/out/usability-167'
sys.stdout.reconfigure(encoding='utf8',errors='replace')

def git(repo,*args,data=None):
    result=subprocess.run(['git',*args],cwd=repo,input=data,capture_output=True)
    if result.returncode:raise RuntimeError((result.stdout+result.stderr).decode('utf8',errors='replace'))
    return result.stdout

files=json.loads((O/'release-files.json').read_text('utf8'))
binary=(H/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe').read_bytes()
assert all(name in binary for name in (b'0.167.0',b'Kumo branch',b'Freddd13'))
for name in ('final-combined','hold-final','midi-export-final','slur-endpoints-final',
             'saved-tempo-palette','notation-input-and-playback','extensions-before',
             'extensions-disabled','extensions-restored','real-bach'):
    log=(O/(name+'.txt')).read_text('utf8',errors='replace')
    assert '0 failed' in log and '0 skipped' in log,name

assert not git(R,'diff','--cached','--name-only').strip()
staged=set(git(H,'diff','--cached','--name-only').decode().splitlines())
assert not staged or staged==set(files)
for name in files:
    source=N/name
    if source.suffix!='.png':source.write_bytes(source.read_bytes().replace(b'\r\n',b'\n'))
    if name!='personal/USER_GUIDE.md':
        native=(H/name).read_bytes()
        if source.suffix!='.png':native=native.replace(b'\r\n',b'\n')
        assert native==source.read_bytes(),name
    if name=='personal/VERSION':(H/name).write_bytes(source.read_bytes())
git(H,'add','--',*[name for name in files if name!='personal/USER_GUIDE.md'])
guide=git(H,'hash-object','-w','--stdin',data=(N/'personal/USER_GUIDE.md').read_bytes()).decode().strip()
git(H,'update-index','--cacheinfo','100644,'+guide+',personal/USER_GUIDE.md')
assert set(git(H,'diff','--cached','--name-only').decode().splitlines())==set(files)
git(H,'diff','--cached','--check')
print(git(H,'commit','-m','Keep explicit work view during startup and verify cumulative workflows').decode('utf8'))
git(H,'tag','personal-v0.167.0')
native=git(H,'rev-parse','HEAD').decode().strip()
paths=['P2/native/'+name for name in files]+['Planning/CURRENT_FEATURE_CHECK_167.md']
paths+=['Repairs/'+name for name in ('check_current_features.py','finish_current_checks.py',
    'prepare_167.py','build_167.py','commit_167.py','install_167.py','finish_167.py')]
git(R,'add','--',*paths)
git(R,'diff','--cached','--check')
print(git(R,'commit','-m','Inspect all current tools and preserve explicit startup view').decode('utf8'))
(O/'commits.json').write_text(json.dumps({'native':native,
    'plugins':git(R,'rev-parse','HEAD').decode().strip()},indent=2),encoding='utf8')
(O/'program-checks.json').write_text(json.dumps({'version':'0.167.0',
    'sha256':hashlib.sha256(binary).hexdigest(),'nativeCommit':native},indent=2),encoding='utf8')
