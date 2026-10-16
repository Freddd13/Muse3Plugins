from pathlib import Path
from urllib.parse import urlsplit
import re
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
for path in [R/'USER_GUIDE_CURRENT.md',R/'USER_GUIDE.md',HOST/'personal/USER_GUIDE.md']:
 s=path.read_text(encoding='utf8');marker='## Codex 钢琴编曲与 MCP 桥接';tail=''
 if marker in s:s,tail=s.split(marker,1);tail=marker+tail
 s=s.replace('**0.49.0 · Kumo branch / Freddd13**','**0.49.0** · Kumo branch / Freddd13')
 s=s.replace('版本修改和提交记录见','本版提交定位：`personal-v0.49.0`。版本修改和提交记录见')
 if tail:
  raw=path.read_bytes();saved=raw[raw.index(marker.encode()):];path.write_bytes(s.encode()+saved)
 else:path.write_text(s,encoding='utf8',newline='\n')
# This archive moved one directory down when the guide was rewritten.
p=HOST/'personal/docs/USER_GUIDE_HISTORY_20261014.md';s=p.read_text(encoding='utf8')
def relocated(match):
 label,target=match.group(1),match.group(2);parsed=urlsplit(target)
 if parsed.scheme or parsed.netloc or not parsed.path:return match.group(0)
 original=(HOST/'personal'/parsed.path).resolve()
 if not (p.parent/parsed.path).resolve().exists() and original.exists():target='../'+target
 return '['+label+']('+target+')'
s=re.sub(r'\[([^\]\n]+)\]\(([^)\n]+)\)',relocated,s);p.write_text(s,encoding='utf8',newline='\n')
shutil_path=R/'docs/USER_GUIDE_HISTORY_20261014.md'
# Keep only the host archive's paths relative to its host directory; plugin archive is unchanged.
p=HOST/'personal/docs/source-map.tsv';rows=[]
for line in p.read_text(encoding='utf8').splitlines():
 fields=line.split('\t')
 if len(fields)==6:
  paths=[]
  for item in fields[5].split(';'):
   item=item.strip()
   if item.startswith('Muse3Plugins/'):item=item[len('Muse3Plugins/'):]
   if item!='-' and not (HOST/item).exists() and (ROOT/item).exists():item='../../muse3_plugins/'+item
   paths.append(item)
  fields[5]=';'.join(paths)
 rows.append('\t'.join(fields))
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
p=HOST/'personal/tools/check_guides.py';s=p.read_text(encoding='utf8')
old='''            except ValueError:
                errors.append(f"{document.name}: link leaves repository: {target}")
                continue'''
new='''            except ValueError:
                # The preserved MCP appendix links to the sibling project's documentation.
                sibling = REPO.parents[1] / "mcp-musescore"
                try:
                    destination.relative_to(sibling)
                except ValueError:
                    errors.append(f"{document.name}: link leaves project folders: {target}")
                    continue'''
assert old in s;s=s.replace(old,new)
old='''        for test_path in (path for path in row["tests"].split(";") if path and path != "-"):
            destination = (REPO / test_path).resolve()'''
new='''        for test_path in (path.strip() for path in row["tests"].split(";") if path.strip() and path.strip() != "-"):
            destination = (REPO / test_path).resolve()'''
assert old in s;s=s.replace(old,new)
old='''            except ValueError:
                inside_repo = False
            if not inside_repo or not destination.exists():'''
new='''            except ValueError:
                try:
                    destination.relative_to(REPO.parents[1] / "muse3_plugins")
                    inside_repo = True
                except ValueError:
                    inside_repo = False
            if not inside_repo or not destination.exists():'''
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8',newline='\n')
mirror=R/'native/personal/tools/check_guides.py';mirror.parent.mkdir(parents=True,exist_ok=True);mirror.write_bytes(p.read_bytes())
