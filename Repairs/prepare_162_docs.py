"""Cumulative N6 instructions and implementation index."""
from pathlib import Path
import csv,hashlib,io,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
for name in ['personal/VERSION','personal/USER_GUIDE.md','personal/CHANGELOG.md','personal/docs/source-map.tsv','personal/docs/REWORK_PROGRESS.md','personal/docs/SPECTRUM_162_GUIDE.md','personal/docs/SPECTRUM_162_CHECKS.md']:
    if name not in files:files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest() if (HOST/name).is_file() else None
(NATIVE/'personal/VERSION').write_bytes(b'0.162.0\n')
guide=NATIVE/'personal/USER_GUIDE.md';text=guide.read_text('utf8').replace('当前版本：**0.161.0','当前版本：**0.162.0',1)
# Keep the task table valid: its separator follows the header.
text=text.replace('| 想完成的事 | 从哪里开始 |\n| 移动实际起音、调整松键，保留谱面时值 | [卷帘演奏起止](docs/PERFORMANCE_TIMING_161_GUIDE.md) |\n|---|---|','| 想完成的事 | 从哪里开始 |\n|---|---|\n| 移动实际起音、调整松键，保留谱面时值 | [卷帘演奏起止](docs/PERFORMANCE_TIMING_161_GUIDE.md) |')
if 'docs/SPECTRUM_162_GUIDE.md' not in text:
    text=text.replace('|---|---|','|---|---|\n| 听辨频谱、看基音和倍频，对照外部MIDI | [频谱完整操作](docs/SPECTRUM_162_GUIDE.md) |',1)
    text+='\n\n## 0.162：频谱准备与MIDI对照\n\n在扒谱页选录音，先显示当前部分，再后台准备整轨。琴键跟随鼠标，倍频线可调编号和强度；设置区可拖高、收起，卷帘时间尺及空格控制原曲。已有分析供缩放、调律和配色复用。完整步骤见[频谱与MIDI对照](docs/SPECTRUM_162_GUIDE.md)。发布定位：`personal-v0.162.0`。\n'
guide.write_bytes(text.encode('utf8'))
change=NATIVE/'personal/CHANGELOG.md';text=change.read_text('utf8')
if '## 0.162.0' not in text:text=text.replace('# 个人版本更新日志\n','# 个人版本更新日志\n\n## 0.162.0 — 2026-11-07\n\n- N6：固定4秒、全音域1024行分析块，调律、音域和视口通过投影复用；可见部分优先，继而相邻与整轨准备，支持取消及原缓存容量。\n- 频谱鼠标强调琴键，基音与倍频编号增加颜色、数量和强度；设置页自然宽度，可独立调整高度。\n- 外部MIDI按原曲绑定、偏移及内部对齐点叠加；上下与叠加显示各自支持显隐，卷帘共用时间、缩放、播放位置和空格。\n- 操作与检查见SPECTRUM_162_GUIDE.md、SPECTRUM_162_CHECKS.md，发布定位personal-v0.162.0。\n',1)
change.write_bytes(text.encode('utf8'))
source=NATIVE/'personal/docs/source-map.tsv';rows=list(csv.reader(io.StringIO(source.read_text('utf8')),delimiter='\t'))
for row in [['频谱投影复用','mscore/referenceaudio/spectrumprojection.cpp','void projectSpectrumBlock(',0,'全音域固定块、调律与视口映射','mtest/mscore/spectrum/tst_spectrum.cpp'],['频谱琴键与参考线','mscore/performanceeditor/spectrumguides.cpp','void SpectrumPane::paintReferences(',0,'编号倍频、键盘强调、MIDI与共同时间尺','mtest/mscore/pluginhost/spectrum_162_tests.inc']]:
    if not any(r and r[0]==row[0] for r in rows):rows.append(row)
for row in rows[1:]:
    file=NATIVE/row[1] if row[1] in files else HOST/row[1]
    if not file.is_file():file=NATIVE/row[1]
    lines=file.read_text('utf8').splitlines();matches=[i+1 for i,line in enumerate(lines) if row[2] in line]
    if not matches:raise ValueError('Missing symbol '+row[1]+' '+row[2])
    row[3]=str(min(matches,key=lambda i:abs(i-int(row[3]))))
buffer=io.StringIO(newline='');csv.writer(buffer,delimiter='\t',lineterminator='\n').writerows(rows);source.write_bytes(buffer.getvalue().encode('utf8'))
record.write_text(json.dumps(files,indent=2),encoding='utf8')
