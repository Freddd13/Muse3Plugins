"""Commit only N7 checked paths in both repositories."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-163'
files=list(json.loads((OUT/'files.json').read_text('utf8')))
for name in ['pluginhost-referenceControls163.txt']:
    if not re.search(r'Totals: \d+ passed, 0 failed, 0 skipped',(OUT/name).read_text('utf8',errors='replace')):raise ValueError(name)
program=HOST/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
if hashlib.sha256(program.read_bytes()).hexdigest()!=json.loads((OUT/'program-checks.json').read_text('utf8'))['sha256']:raise ValueError('Unchecked program')
subprocess.run([__import__('sys').executable,str(HOST/'personal/tools/check_guides.py')],check=True)
existing=set(subprocess.check_output(['git','diff','--cached','--name-only'],cwd=HOST,text=True).splitlines())
if existing-set(files):raise ValueError('Other staged changes '+str(existing-set(files)))
subprocess.run(['git','add','--',*[name for name in files if name!='personal/USER_GUIDE.md']],cwd=HOST,check=True)
blob=subprocess.check_output(['git','hash-object','-w','--stdin'],input=(ROOT/'P2/native/personal/USER_GUIDE.md').read_bytes(),cwd=HOST).decode().strip()
subprocess.run(['git','update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md'],cwd=HOST,check=True)
staged=set(subprocess.check_output(['git','diff','--cached','--name-only'],cwd=HOST,text=True).splitlines())
if staged-set(files):raise ValueError('Staged paths differ')
for name in set(files)-staged:
    if subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)!=(ROOT/'P2/native'/name).read_bytes():raise ValueError('Unstaged change '+name)
subprocess.run(['git','diff','--cached','--check'],cwd=HOST,check=True)
subprocess.run(['git','commit','-m','Add 0.163 reference range controls with split playback and undo'],cwd=HOST,check=True)
subprocess.run(['git','tag','personal-v0.163.0'],cwd=HOST,check=True)
for name in files:
    if subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)!=(ROOT/'P2/native'/name).read_bytes():raise ValueError('Mirror differs '+name)
helpers=['prepare_163.py','prepare_163_wiring.py','sync_163.py','build_163.py','format_163.py','run_163_checks.py','prepare_163_docs.py','finish_163_docs.py','prepare_163_release.py','check_163_program.py','install_163.py','finalize_163.py']
paths=['P2/native/'+name for name in files]+['Repairs/'+name for name in helpers]+['Planning/REFERENCE_CONTROLS_163_DESIGN.md','Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','Deliver N7 reference ranges, split controls and verified instructions'],cwd=ROOT,check=True)
print('Committed',len(files),'native paths')
