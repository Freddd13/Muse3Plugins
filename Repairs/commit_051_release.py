from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo).decode('utf8').strip()
for name,count in [('performanceeditor',60),('p0native',23),('p1native',45)]:assert f'Totals: {count} passed, 0 failed' in (R/f'out/repair-051-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace')
for repo in [HOST,ROOT]:
 assert not git(repo,'diff','--cached','--name-only'),'已有暂存内容';git(repo,'fetch','origin');up=git(repo,'rev-parse','--abbrev-ref','@{upstream}');assert git(repo,'rev-list','--count','HEAD..'+up)=='0','远程有新提交'
paths=set(git(HOST,'diff','--name-only').splitlines()+git(HOST,'ls-files','--others','--exclude-standard').splitlines());paths.discard('AGENTS.md')
assert all((R/'native'/p).is_file() or p.startswith(('personal/','share/plugins/')) for p in paths),paths
git(HOST,'add','--',*sorted(paths));git(HOST,'diff','--cached','--check');print(git(HOST,'commit','-m','Refine slur routes hand brackets and assistant window lifetime'),flush=True);git(HOST,'tag','personal-v0.51.0');native=git(HOST,'rev-parse','--short=9','HEAD')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8');s+=f'\n第四批提交：{native}，personal-v0.51.0。安装：msvc.install_repair_0_51_x64。128项窗口检查、重复开关和大谱缩放通过；继续第五批。\n';p.write_text(s,encoding='utf8',newline='\n')
paths=set(git(ROOT,'diff','--name-only').splitlines()+git(ROOT,'ls-files','--others','--exclude-standard').splitlines());paths={p for p in paths if p!='p0-test-results.txt' and '052' not in p}
assert all(p.startswith(('Repairs/','Planning/','HarmonyAssistant/','ArrangementAssistant/')) for p in paths),paths
git(ROOT,'add','--',*sorted(paths));git(ROOT,'diff','--cached','--check');print(git(ROOT,'commit','-m','Finish notation controls and stabilize assistant surfaces'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.51.0');git(ROOT,'push','origin','main');print('Native '+native+'; plugins '+git(ROOT,'rev-parse','--short=9','HEAD'),flush=True)
