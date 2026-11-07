"""Update the cumulative guide and source map for N5."""
from pathlib import Path
import csv
import hashlib
import io
import json
import shutil
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
names=['personal/USER_GUIDE.md','personal/CHANGELOG.md','personal/docs/source-map.tsv',
       'personal/docs/REWORK_PROGRESS.md','personal/docs/PERFORMANCE_TIMING_161_GUIDE.md','personal/docs/PERFORMANCE_TIMING_161_CHECKS.md']
for name in names:
    target=HOST/name
    if name not in files:files[name]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
guide=NATIVE/'personal/USER_GUIDE.md';text=guide.read_text('utf8').replace('当前版本：**0.160.0','当前版本：**0.161.0',1)
if 'docs/PERFORMANCE_TIMING_161_GUIDE.md' not in text:
    text=text.replace('| 想完成的事 | 从哪里开始 |','| 想完成的事 | 从哪里开始 |\n| 移动实际起音、调整松键，保留谱面时值 | [卷帘演奏起止](docs/PERFORMANCE_TIMING_161_GUIDE.md) |',1)
    text+='\n\n## 0.161：卷帘演奏起止\n\n打开“演奏编辑器 → 演奏编辑”，开启卷帘上方的“演奏调整”。拖主体移动实际起音，拖两端改按键时间；细轮廓保留谱面时值。选音、选段和全谱可分别恢复，保存后重开继续使用。完整例子见[实际起音与松键](docs/PERFORMANCE_TIMING_161_GUIDE.md)。\n\n发布定位：`personal-v0.161.0`。\n'
guide.write_bytes(text.encode('utf8'))
changelog=NATIVE/'personal/CHANGELOG.md';text=changelog.read_text('utf8')
if '## 0.161.0' not in text:text=text.replace('# 个人版本更新日志\n','# 个人版本更新日志\n\n## 0.161.0 — 2026-11-07\n\n- N5：谱面轨增加默认关闭的“演奏调整”，拖主体移动实际起音与松键，拖两端改按键时间；细轮廓保留记谱位置。\n- 逐次发声偏移接入原生播放、查询与MIDI导出；保留自动NoteEvent、延音链和发音符号。音符数据支持链接、复制、保存重开、恢复和原生撤销。\n- 显示分批读取真实演奏事件，建立音高区间索引，平移缩放复用；播放和跨窗口结束手势归还鼠标。\n- 修正从分谱选择外部MIDI音源时的总谱谱表对应。操作及检查见PERFORMANCE_TIMING_161_GUIDE.md、PERFORMANCE_TIMING_161_CHECKS.md，发布定位personal-v0.161.0。\n',1)
changelog.write_bytes(text.encode('utf8'))
source=NATIVE/'personal/docs/source-map.tsv';rows=list(csv.reader(io.StringIO(source.read_text('utf8')),delimiter='\t'))
new=[
 ['逐次演奏起止','libmscore/performancetiming.cpp','void apply(',0,'自动事件之后的起音与松键偏移、链接及保存','mtest/mscore/pluginhost/timing_161_tests.inc'],
 ['卷帘演奏拖动','mscore/performanceeditor/timingeditor.cpp','bool TimingEditor::handle(',0,'分批事件、固定拖动目标、实际起止及恢复','mtest/mscore/pluginhost/timing_161_tests.inc']]
for item in new:
    if not any(row and row[0]==item[0] for row in rows):rows.append(item)
for row in rows[1:]:
    if len(row)!=6:raise ValueError('Source map columns')
    path=NATIVE/row[1] if row[1] in files else HOST/row[1]
    if not path.is_file():path=NATIVE/row[1]
    lines=path.read_text('utf8').splitlines();matches=[i+1 for i,line in enumerate(lines) if row[2] in line]
    if not matches:raise ValueError('Source symbol missing: '+row[1]+' '+row[2])
    row[3]=str(min(matches,key=lambda line:abs(line-int(row[3]))))
buffer=io.StringIO(newline='');csv.writer(buffer,delimiter='\t',lineterminator='\n').writerows(rows);source.write_bytes(buffer.getvalue().encode('utf8'))
checks=NATIVE/'personal/docs/PERFORMANCE_TIMING_161_CHECKS.md'
if not checks.is_file():checks.write_bytes('# 0.161 实际起音与松键检查\n\n当前正在核对原生事件、鼠标拖动、撤销与保存；完成结果随后写入。\n'.encode('utf8'))
image=OUT/'performance-timing-controls-161.png'
if image.is_file():
    name='personal/docs/images/performance-timing-161.png';target=HOST/name
    if name not in files:files[name]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
    shutil.copy2(image,NATIVE/name)
record.write_text(json.dumps(files,indent=2),encoding='utf8')
print('Prepared N5 guide and source map')
