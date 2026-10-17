"""Collect installed-program checks and distribute the completed 0.52 guide."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / 'Repairs'
HOST = ROOT.parent / 'muse3_dev/MuseScore'
INSTALL = HOST / 'msvc.install_repair_0_52_x64'
for name, count in [('p1native', 49), ('performanceeditor', 62), ('p0native', 23)]:
    log = (R / f'out/repair-052-final-{name}/gui.txt').read_text(encoding='utf8', errors='replace')
    assert f'Totals: {count} passed, 0 failed' in log, name
    assert not re.search(r'TypeError:|ReferenceError:|Unable to assign \[undefined\]', log), name
raw = (R / 'out/repair-052-benchmark/gui.txt').read_text(encoding='utf8', errors='replace')
assert 'Totals: 4 passed, 0 failed' in raw
measures = {(a, b): c for a, b, c in re.findall(r'Score Ctrl zoom (\d+) notes: band (\d+) P95 ([\d.]+)', raw)}
for folder in [R / 'docs/images', HOST / 'personal/docs/images']:
    for source, destination in [
        ('regional-comparison-panel-052.png', 'comparison-052-variants.png'),
        ('regional-comparison-score-052.png', 'comparison-052-score.png'),
        ('regional-rhythm-overlay-052.png', 'comparison-052-rhythm.png'),
        ('midi-length-comparison-052.png', 'comparison-052-midi.png'),
        ('midi-length-editor-052.png', 'comparison-052-midi-editor.png'),
    ]:
        shutil.copy2(R / 'out/repair-052-final-p1native' / source, folder / destination)
    shutil.copy2(R / 'out/repair-052-final-performanceeditor/kumo-about-012.png', folder / 'comparison-052-about.png')

path = R / 'docs/COMPARISON_052_VALIDATION.md'
text = path.read_text(encoding='utf8').replace('repair-052-candidate-*', 'repair-052-final-*')
text += '\n## 安装后复查\n\n安装版再次通过134项检查。关于窗口显示Kumo branch / Freddd13 · v0.52.0。另有8份JavaScript规则检查通过。\n\n'
text += '返回导出窗口后，新长度继续使用清楚的强调色；图像检查核对选中音与背景的对比。叠加开启后，停着不操作时保持空闲。\n\n'
text += '四分音符与八分音符的写法叠加、缺少起音处的插值位置、符杠、窗口大小变化和Ctrl缩放已用独立乐谱检查；源谱内容与撤销位置保持。对比绘制按可见谱行取变化，当前几何位置在绘制时读取。\n\n'
text += '![节奏写法叠加](images/comparison-052-rhythm.png)\n\n'
text += '| 谱中音符 | 关闭谱行带，Ctrl缩放95%耗时 | 开启谱行带，Ctrl缩放95%耗时 |\n|---|---:|---:|\n'
for count in ['10080', '50064']:
    text += f'| {count} | {measures[count, "0"]} ms | {measures[count, "1"]} ms |\n'
text += '\n这些数字包括原生谱面刷新，使用与前几批相同的乐谱和窗口大小。初次写法对比会建立排版副本，内容未变时继续复用；缩放读取当前可见谱行。\n'
path.write_text(text, encoding='utf8', newline='\n')
shutil.copy2(path, HOST / 'personal/docs' / path.name)

path = HOST / 'personal/docs/source-map.tsv'
rows = path.read_text(encoding='utf8').splitlines()
for i, row in enumerate(rows):
    fields = row.split('\t')
    if len(fields) == 6 and (HOST / fields[1]).is_file():
        hits = [n + 1 for n, line in enumerate((HOST / fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
        if hits:
            fields[3] = str(min(hits, key=lambda n: abs(n - int(fields[3]))))
            rows[i] = '\t'.join(fields)
path.write_text('\n'.join(rows) + '\n', encoding='utf8', newline='\n')

marker = '## Codex 钢琴编曲与 MCP 桥接'.encode()
old = subprocess.check_output(['git', 'show', 'HEAD:personal/USER_GUIDE.md'], cwd=HOST)
now = (HOST / 'personal/USER_GUIDE.md').read_bytes()
assert now[now.index(marker):] == old[old.index(marker):]
assert (HOST / 'personal/VERSION').read_text().strip() == '0.52.0'
(INSTALL / 'personal').mkdir(exist_ok=True)
for name in ['USER_GUIDE.md', 'CHANGELOG.md', 'VERSION']:
    shutil.copy2(HOST / 'personal' / name, INSTALL / 'personal' / name)
shutil.copytree(HOST / 'personal/docs', INSTALL / 'personal/docs', dirs_exist_ok=True)

path = ROOT / 'Planning/REPAIR_2026_10_SECOND_PASS.md'
text = path.read_text(encoding='utf8').replace('- [ ] 5：', '- [x] 5：')
text += '\n0.52.0：第五批完成，写法叠加、组合、快捷比较及MIDI音长编辑与试听已通过安装版检查。五批调整的操作说明和0–12项答复见Repairs/docs/REPAIR_048_052_DELIVERY.md。134项窗口与文件检查、4项大谱测量和8份JS规则检查通过。\n'
path.write_text(text, encoding='utf8', newline='\n')
print('0.52安装版检查、截图和完整说明已整理。')
