from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent.parent;HOST=ROOT.parent/'muse3_dev/MuseScore'
def output(repo,*args):return subprocess.check_output(['git',*args],cwd=repo).decode('utf8').strip()
assert output(HOST,'rev-parse','--short=9','HEAD')=='3937d68c1'
assert 'AGENTS.md' not in output(HOST,'diff','--cached','--name-only').splitlines()
# New source files use LF; retain the existing style in edited files.
for repo,names in [(HOST,output(HOST,'diff','--cached','--diff-filter=A','--name-only').splitlines()),(ROOT,output(ROOT,'ls-files','--others','--exclude-standard').splitlines())]:
 for name in names:
  if name=='p0-test-results.txt':continue
  path=repo/name
  if not path.is_file():continue
  data=path.read_bytes()
  if b'\0' in data:continue
  clean=data.replace(b'\r\n',b'\n')
  if clean!=data:path.write_bytes(clean)
source=(ROOT/'Repairs/commit_050_release.py').read_text(encoding='utf8')
prefix=source[:source.index('for repo in [HOST,ROOT]:')]
suffix=source[source.index('metadata='):]
suffix=suffix.replace("paths=set(git(HOST,'diff','--name-only').splitlines()+", "paths=set(git(HOST,'diff','--name-only').splitlines()+git(HOST,'diff','--cached','--name-only').splitlines()+",1)
exec(prefix,globals())
for repo in [HOST,ROOT]:
 git(repo,'fetch','origin');upstream=git(repo,'rev-parse','--abbrev-ref','@{upstream}');assert int(git(repo,'rev-list','--count','HEAD..'+upstream))==0
exec(suffix,globals())
