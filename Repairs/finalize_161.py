"""Commit the checked N5 batch in both repositories, preserving separate edits."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-161'
files=list(json.loads((OUT/'files.json').read_text('utf8')))
for name in ('pluginhost-performanceTimingPersistence161.txt','pluginhost-existingEditorProfileFirstOpen.txt','performanceeditor-wheelSelectionCommit158.txt'):
    if not re.search(r'Totals: \d+ passed, 0 failed, 0 skipped',(OUT/name).read_text('utf8',errors='replace')):raise ValueError(name)
program=HOST/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
if hashlib.sha256(program.read_bytes()).hexdigest()!=json.loads((OUT/'program-checks.json').read_text('utf8'))['sha256']:raise ValueError('Unchecked executable')
subprocess.run([__import__('sys').executable,str(HOST/'personal/tools/check_guides.py')],check=True)
if subprocess.check_output(['git','diff','--cached','--name-only'],cwd=HOST).strip():raise ValueError('Other native staged changes')
subprocess.run(['git','add','--',*[name for name in files if name!='personal/USER_GUIDE.md']],cwd=HOST,check=True)
guide=(ROOT/'P2/native/personal/USER_GUIDE.md').read_bytes()
blob=subprocess.check_output(['git','hash-object','-w','--stdin'],input=guide,cwd=HOST).decode().strip()
subprocess.run(['git','update-index','--cacheinfo','100644,'+blob+',personal/USER_GUIDE.md'],cwd=HOST,check=True)
actual=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=HOST,text=True).splitlines()
if set(actual)!=set(files):raise ValueError('Unexpected native paths '+str(set(actual)^set(files)))
subprocess.run(['git','diff','--cached','--check'],cwd=HOST,check=True)
subprocess.run(['git','commit','-m','Add 0.161 native roll onset and release editing with persistence'],cwd=HOST,check=True)
subprocess.run(['git','tag','personal-v0.161.0'],cwd=HOST,check=True)
for name in files:
    data=subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)
    if data!=(ROOT/'P2/native'/name).read_bytes():raise ValueError('Mirror mismatch '+name)
helpers=['prepare_161.py','prepare_161_checks.py','prepare_161_docs.py','prepare_161_lookahead.py','prepare_161_repaint.py','format_161.py','sync_161.py','build_161.py','run_161_checks.py','check_161_program.py','finish_161_docs.py','finalize_161.py','install_161.py']
paths=['P2/native/'+name for name in files]+['Repairs/'+name for name in helpers]+['Planning/ACTUAL_TIMING_DESIGN.md','Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md','P2/check_stock.py']
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','Deliver N5 roll performance timing and checked 0.161 guides'],cwd=ROOT,check=True)
print('Committed',len(files),'native files')
