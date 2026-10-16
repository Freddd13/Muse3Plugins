from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo).decode('utf8').strip()
for name,count in [('performanceeditor',56),('p0native',23),('p1native',44)]:
 text=(R/f'out/repair-050-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
 assert not re.search(r'TypeError:|ReferenceError:|Unable to assign \[undefined\]',text),name+' has a UI error'
assert 'Totals: 4 passed, 0 failed' in (R/'out/repair-050-benchmark/gui.txt').read_text(encoding='utf8',errors='replace')
assert 'Totals: 12 passed, 0 failed, 0 skipped' in (R/'out/repair-050-media-device.txt').read_text(encoding='utf8',errors='replace')
assert (HOST/'personal/VERSION').read_text().strip()=='0.50.0'
for repo in [HOST,ROOT]:
 assert not git(repo,'diff','--cached','--name-only'),'Existing staged files'
 git(repo,'fetch','origin');upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}')
 assert int(git(repo,'rev-list','--count','HEAD..'+upstream))==0,'Remote has new commits'
metadata={'personal/CHANGELOG.md','personal/USER_GUIDE.md','personal/VERSION','personal/docs/source-map.tsv','personal/docs/ASSISTANTS_050_VALIDATION.md'}
paths=set(git(HOST,'diff','--name-only').splitlines()+git(HOST,'ls-files','--others','--exclude-standard').splitlines());paths.discard('AGENTS.md')
assert all((R/'native'/path).is_file() or path in metadata or path in {'mscore/musescore.cpp','mscore/scoreview.h'} or path.startswith(('share/plugins/','personal/docs/images/assistants-050-')) for path in paths),paths
assert paths,'No native changes'
git(HOST,'add','--',*sorted(paths));git(HOST,'diff','--cached','--check');print(git(HOST,'commit','-m','Refine harmony arrangement panels and reference playback'),flush=True)
native=git(HOST,'rev-parse','--short=9','HEAD');git(HOST,'tag','personal-v0.50.0')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8');s+='\n软件第三批提交：'+native+'，personal-v0.50.0。安装为msvc.install_repair_0_50_x64；说明与截图见ASSISTANTS_050_VALIDATION.md。继续第四、五批。\n';p.write_text(s,encoding='utf8',newline='\n')
paths=set(git(ROOT,'diff','--name-only').splitlines()+git(ROOT,'ls-files','--others','--exclude-standard').splitlines());paths.discard('p0-test-results.txt')
assert all(path.startswith(('Repairs/','HarmonyAssistant/','ArrangementAssistant/','ArrangementVariants/','PerformanceExpression/','ReferencePlayer/','WorkflowCommon/','Planning/')) for path in paths),paths
git(ROOT,'add','--',*sorted(paths));git(ROOT,'diff','--cached','--check');print(git(ROOT,'commit','-m','Unify assistant surfaces and make reference fragments editable'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.50.0');git(ROOT,'push','origin','main')
print('Native '+native+'; plugins '+git(ROOT,'rev-parse','--short=9','HEAD'),flush=True)
