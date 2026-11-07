from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
for label in ['reference','settings']:
    name='personal/docs/images/spectrum-'+label+'-162.png';file=HOST/name
    files.setdefault(name,hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else None)
    shutil.copy2(OUT/('spectrum-'+label+'-162.png'),NATIVE/name)
progress=NATIVE/'personal/docs/REWORK_PROGRESS.md';text=progress.read_text('utf8')
if '## 2026-11-07：0.162' not in text:
    text=text.replace('# 当前进度与后续完整计划\n','# 当前进度与后续完整计划\n\n## 2026-11-07：0.162 频谱与MIDI对照\n\nN6已完成固定块分析、后台整轨准备、调律与视口复用、琴键／倍频参考、设置高度、MIDI叠加与共同时间尺。新操作与原有取音、循环、写谱、演奏编辑均已核对。正在更新程序目录。见[操作](SPECTRUM_162_GUIDE.md)与[检查](SPECTRUM_162_CHECKS.md)。\n\n| 编号 | 当前结果与下一项 |\n|---|---|\n| N1—N3 | 0.159操作、Kawai混响及上游报告已交付 |\n| N4 | 0.160外部／临时MIDI轨道已交付 |\n| N5 | 0.161谱面轨实际起止与恢复已交付 |\n| N6 | 0.162频谱和MIDI对照已检查 |\n| N7 | 下一项：原曲范围、分体播放、移位与显隐 |\n| N8 | 动态乐谱、谱表组合、时间调整、MP4与透明MOV |\n| N9 | AI44项工具及数据流程报告已交付 |\n\n接着完成N7、N8；实体键盘和真实音乐听感继续保留。以下为前面各批记录。\n',1)
progress.write_bytes(text.encode('utf8'))
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('| N6 | 频谱键盘高亮、谐波、设置及固定块缓存 | 待实施 |','| N6 | 频谱键盘高亮、谐波、设置及固定块缓存 | 0.162已检查整轨准备、三格式长音频、琴键／倍频、设置与MIDI对照，正在更新程序目录 |');plan.write_bytes(text.encode('utf8'))
record.write_text(json.dumps(files,indent=2),encoding='utf8')
