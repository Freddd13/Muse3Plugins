from pathlib import Path
import csv,hashlib,io,json,shutil
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';N=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-163'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
for name in ['personal/VERSION','personal/USER_GUIDE.md','personal/CHANGELOG.md','personal/docs/source-map.tsv','personal/docs/REWORK_PROGRESS.md','personal/docs/REFERENCE_CONTROLS_163_GUIDE.md','personal/docs/REFERENCE_CONTROLS_163_CHECKS.md','personal/docs/images/reference-cross-line-163.png']:
    if name not in files:files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest() if (HOST/name).is_file() else None
(N/'personal/VERSION').write_bytes(b'0.163.0\n')
guide=N/'personal/USER_GUIDE.md';text=guide.read_text('utf8').replace('当前版本：**0.162.0','当前版本：**0.163.0',1)
if 'docs/REFERENCE_CONTROLS_163_GUIDE.md' not in text:
    text=text.replace('|---|---|','|---|---|\n| 从谱面播放原曲片段，查看范围并移动按钮 | [谱面原曲控件](docs/REFERENCE_CONTROLS_163_GUIDE.md) |',1)
    text+='\n\n## 0.163：谱面原曲范围和分体播放\n\n打开原曲参考中的“谱面播放按钮”。左边直接播放／停止，右边选择片段；范围可随悬停、播放或始终显示。按钮可以拖动、隐藏、恢复和撤销，保存乐谱后继续保留。完整步骤见[谱面原曲控件](docs/REFERENCE_CONTROLS_163_GUIDE.md)。发布定位：`personal-v0.163.0`。\n'
guide.write_bytes(text.encode('utf8'))
change=N/'personal/CHANGELOG.md';text=change.read_text('utf8')
if '## 0.163.0' not in text:text=text.replace('# 个人版本更新日志\n','# 个人版本更新日志\n\n## 0.163.0 — 2026-11-07\n\n- N7：谱面原曲控件使用原生分体按钮，直接播放／停止和选择片段分别操作，保留共用播放会话。\n- 关联范围按实际谱行、谱表及音符拍位显示，提供悬停、播放时、始终显示；按钮移位与真实范围分别处理。\n- 按钮位置和隐藏进入原生撤销，独立谱内资料随MSCZ保存；原曲面板提供恢复入口。分段写法移位与撤销一同回查。\n- 操作及检查见REFERENCE_CONTROLS_163_GUIDE.md、REFERENCE_CONTROLS_163_CHECKS.md，发布定位personal-v0.163.0。\n',1)
change.write_bytes(text.encode('utf8'))
progress=N/'personal/docs/REWORK_PROGRESS.md';text=progress.read_text('utf8')
if '## 2026-11-07：0.163' not in text:text=text.replace('# 当前进度与后续完整计划\n','# 当前进度与后续完整计划\n\n## 2026-11-07：0.163 谱面原曲关联\n\nN7已检查原曲分体播放、选择、停止、范围显示、跨行、移位、隐藏、恢复和保存撤销。正在更新程序目录。见[操作](REFERENCE_CONTROLS_163_GUIDE.md)与[检查](REFERENCE_CONTROLS_163_CHECKS.md)。\n\n| 编号 | 当前结果与下一项 |\n|---|---|\n| N1—N3 | 操作、Kawai混响、上游适配已交付 |\n| N4／N5 | 外部MIDI与谱面演奏起止已交付 |\n| N6 | 频谱与MIDI对照0.162已交付 |\n| N7 | 谱面原曲控件0.163已检查 |\n| N8 | 下一项：动态乐谱、谱表组合、换行时间、MP4及透明MOV |\n| N9 | AI44项工具与数据流程报告已交付 |\n\n继续N8动态乐谱；实体键盘和真实音乐听感按原安排保留。以下为前面记录。\n',1)
progress.write_bytes(text.encode('utf8'))
source=N/'personal/docs/source-map.tsv';rows=list(csv.reader(io.StringIO(source.read_text('utf8')),delimiter='\t'))
new=['谱面原曲控件','mscore/workflow/referencecontrols.cpp','void installReferenceScoreControls(',0,'分体播放、实际范围、摆放及撤销保存','mtest/mscore/pluginhost/reference_163_tests.inc']
if not any(row and row[0]==new[0] for row in rows):rows.append(new)
# The extracted controller replaces its former factory-local class.
for row in rows[1:]:
    if row[1]=='mscore/workflow/referencefactory.cpp' and 'ReferenceScoreControls' in row[2]:row[1]='mscore/workflow/referencecontrols.cpp';row[2]='void installReferenceScoreControls('
    file=N/row[1] if row[1] in files else HOST/row[1]
    if not file.is_file():file=N/row[1]
    lines=file.read_text('utf8').splitlines();matches=[i+1 for i,line in enumerate(lines) if row[2] in line]
    if not matches:raise ValueError('Missing '+row[1]+' '+row[2])
    row[3]=str(min(matches,key=lambda i:abs(i-int(row[3]))))
buffer=io.StringIO(newline='');csv.writer(buffer,delimiter='\t',lineterminator='\n').writerows(rows);source.write_bytes(buffer.getvalue().encode('utf8'))
shutil.copy2(OUT/'reference-cross-line-163.png',N/'personal/docs/images/reference-cross-line-163.png')
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('| N7 | 原曲范围、分体播放按钮及可移动谱面控件 | 待实施 |','| N7 | 原曲范围、分体播放按钮及可移动谱面控件 | 0.163分体播放、实际范围、移位显隐及撤销保存已检查，正在更新程序目录 |');plan.write_bytes(text.encode('utf8'))
record.write_text(json.dumps(files,indent=2),encoding='utf8')
