from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent.parent;HOST=ROOT.parent/'muse3_dev/MuseScore'
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo).decode('utf8').strip()
assert git(HOST,'rev-parse','--short=9','HEAD')=='dd656520a'
for path in [ROOT/'Repairs/docs/EXPRESSION_049_GUIDE.md',ROOT/'Repairs/native/mscore/seq.h',HOST/'mscore/seq.h']:
 path.write_bytes(path.read_bytes().rstrip()+b'\n')
git(HOST,'add','--','mscore/seq.h');git(HOST,'diff','--cached','--check');print(git(HOST,'commit','--amend','--no-edit'),flush=True)
native=git(HOST,'rev-parse','--short=9','HEAD');git(HOST,'tag','-f','personal-v0.49.0')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';p.write_text(p.read_text(encoding='utf8').replace('dd656520a',native),encoding='utf8',newline='\n')
git(ROOT,'add','--','Repairs/docs/EXPRESSION_049_GUIDE.md','Repairs/native/mscore/seq.h','Repairs/finish_049_commit.py','Planning/REPAIR_2026_10_SECOND_PASS.md');git(ROOT,'diff','--cached','--check');print(git(ROOT,'commit','-m','Make expression comparison application and recovery continuous'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.49.0');git(ROOT,'push','origin','main')
print('Native '+native+'; plugins '+git(ROOT,'rev-parse','--short=9','HEAD'),flush=True)
