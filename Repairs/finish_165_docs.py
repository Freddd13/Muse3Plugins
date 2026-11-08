"""Refresh source locations and the current release link."""
from pathlib import Path
import csv
import io

R = Path(__file__).resolve().parents[1]
N = R / 'P2/native'
H = R.parent / 'muse3_dev/MuseScore'
p = N / 'personal/USER_GUIDE.md'
t = p.read_text('utf8')
anchor = '当前版本：**0.165.0 · Kumo branch / Freddd13**。'
assert anchor in t
if '本次动态乐谱入口修复与整轮审视' not in t:
    t = t.replace(anchor, anchor + '\n\n本次动态乐谱入口修复与整轮审视见[0.165更新](docs/ROUND_165_REVIEW.md)（`personal-v0.165.0`）。', 1)
p.write_text(t, encoding='utf8', newline='\n')
p = N / 'personal/docs/source-map.tsv'
rows = list(csv.reader(io.StringIO(p.read_text('utf8')), delimiter='\t'))
for row in rows[1:]:
    source = H / row[1]
    if not source.is_file() or not row[3].isdigit():
        continue
    candidates = [i for i, line in enumerate(source.read_text('utf8').splitlines(), 1) if row[2] in line]
    if candidates:
        row[3] = str(min(candidates, key=lambda at: abs(at - int(row[3]))))
buffer = io.StringIO()
csv.writer(buffer, delimiter='\t', lineterminator='\n').writerows(rows)
p.write_text(buffer.getvalue(), encoding='utf8', newline='\n')
print('Updated current release links and source locations.')
