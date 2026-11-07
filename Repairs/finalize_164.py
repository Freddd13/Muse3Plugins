"""Commit only N8 checked paths in both repositories."""
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';OUT=ROOT/'P2/out/repair-164'
files=list(json.loads((OUT/'files.json').read_text('utf8')))
for name in ['pluginhost-scoreVideoPictures164.txt','spectrum-checks.txt']:
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
subprocess.run(['git','commit','-m','Add 0.164 native score video preview and MP4 ProRes export'],cwd=HOST,check=True)
subprocess.run(['git','tag','personal-v0.164.0'],cwd=HOST,check=True)
for name in files:
    if subprocess.check_output(['git','show','HEAD:'+name],cwd=HOST)!=(ROOT/'P2/native'/name).read_bytes():raise ValueError('Mirror differs '+name)
helpers=['prepare_164.py','prepare_164_audio.py','prepare_164_document.py','wire_164.py','refine_164.py','polish_164.py','verify_164_ui.py','sync_164.py','format_164.py','build_164.py','run_164_checks.py','run_spectrum_164.py','check_video_164.py','prepare_164_docs.py','finish_164_docs.py','prepare_164_release.py','check_164_program.py','install_164.py','finalize_164.py']
paths=['P2/native/'+name for name in files]+['Repairs/'+name for name in helpers]+['Planning/SCORE_VIDEO_164_DESIGN.md','Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md']
subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','Deliver N8 native score video, bounded sound and checked instructions'],cwd=ROOT,check=True)
print('Committed',len(files),'native paths')
