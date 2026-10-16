from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parent.parent;HOST=ROOT.parent/'muse3_dev/MuseScore';R=ROOT/'Repairs'
def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo).decode('utf8').strip()
for name,count in [('performanceeditor',56),('p0native',23),('p1native',40)]:
 text=(R/f'out/repair-049-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
assert 'Totals: 4 passed, 0 failed' in (R/'out/repair-049-benchmark/gui.txt').read_text(encoding='utf8',errors='replace')
assert (HOST/'personal/VERSION').read_text().strip()=='0.49.0'
for repo in [HOST,ROOT]:
 assert not git(repo,'diff','--cached','--name-only'),'Existing staged files'
 git(repo,'fetch','origin');upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}')
 assert int(git(repo,'rev-list','--count','HEAD..'+upstream))==0,'Remote has new commits'
metadata={'personal/CHANGELOG.md','personal/USER_GUIDE.md','personal/VERSION','personal/docs/USER_GUIDE_HISTORY_20261014.md','personal/docs/source-map.tsv','personal/docs/EXPRESSION_049_VALIDATION.md','personal/docs/images/expression-049-editor.png','personal/docs/images/expression-049-panel.png'}
paths=set(git(HOST,'diff','--name-only').splitlines()+git(HOST,'ls-files','--others','--exclude-standard').splitlines());paths.discard('AGENTS.md')
assert all((R/'native'/path).is_file() or path in metadata or path.startswith('share/plugins/PerformanceExpression/') for path in paths),paths
git(HOST,'add','--',*sorted(paths));git(HOST,'diff','--cached','--check');print(git(HOST,'commit','-m','Restore expression audition and scoped velocity workflow'),flush=True)
native=git(HOST,'rev-parse','--short=9','HEAD');git(HOST,'tag','personal-v0.49.0')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8');s+='\n软件演奏表达提交：'+native+'，personal-v0.49.0。正式安装为msvc.install_repair_0_49_x64；日常编辑与表达检查已完成，继续第三批辅助面板和联合播放。\n';p.write_text(s,encoding='utf8',newline='\n')
paths=set(git(ROOT,'diff','--name-only').splitlines()+git(ROOT,'ls-files','--others','--exclude-standard').splitlines());paths.discard('p0-test-results.txt')
assert all(path.startswith(('Repairs/','PerformanceExpression/')) or path in {'P1/tests/test_expression_progress.js','Planning/REPAIR_2026_10_SECOND_PASS.md'} for path in paths),paths
git(ROOT,'add','--',*sorted(paths));git(ROOT,'diff','--cached','--check');print(git(ROOT,'commit','-m','Make expression comparison application and recovery continuous'),flush=True)
git(HOST,'push','origin','3.x');git(HOST,'push','origin','personal-v0.49.0');git(ROOT,'push','origin','main')
print('Native '+native+'; plugins '+git(ROOT,'rev-parse','--short=9','HEAD'),flush=True)
