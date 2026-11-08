"""Record the complete review and native score-output repair."""
from pathlib import Path
import csv
import io
import json

R = Path(__file__).resolve().parents[1]
N = R / 'P2/native'
H = R.parent / 'muse3_dev/MuseScore'
O = R / 'P2/out/repair-166'

def write(name, text):
    for base in (N, H):
        (base / name).write_text(text, encoding='utf8', newline='\n')

def edit(name, change):
    for base in (N, H):
        path = base / name
        path.write_text(change(path.read_text('utf8')), encoding='utf8', newline='\n')

write('personal/VERSION', '0.166.0\n')
review = '''# 0.166：整轮审视与原生谱面输出修复

上次只修好了动态乐谱的入口。文字比例和实际画面继续存在问题，这次已回到原谱输出，并沿 N1—N9 的操作顺序审视本轮其它改动。

## 动态乐谱怎样保留原谱

画面使用 MuseScore 已排好的音符、文字、线条和各自的位置。先准备每行所选谱表，再按演奏时间换行；预览与导出读取同一组图片。字体、字号、人工移动和分行都来自原谱。

这次查到并修正了两处原因：

1. **文字和音符大小不协调。** 原生 PNG 导出同时设置图像分辨率和绘图缩放；视频遗漏了图像分辨率，文字被按另一套尺寸绘制。现在与原生 PNG 使用相同的换算。
2. **各行音符忽大忽小。** 准备图片时会按谱行尺寸选择图片分辨率，合成时却只比较像素。现在按原谱尺寸计算“各行使用相同缩放”，再换算到每张图片。

同样的分辨率遗漏也存在于 AI 的 MuseScore 原图接口，已一并修正。返回的拍位、音符引用和图片位置继续对应原谱。

使用只读的《如果有来生 release5》核对第一行、中间三谱表及末行：原生 PNG 与视频谱行的文字、音符、速度、力度、八度线、圆滑线及分手记号位置一致。另核对了准备副本与原谱，结果一致。最终 1080p 画面保留这些比例。原谱的内容、保存状态保持原样。本地对照画面与记录在插件仓库 `P2/out/repair-166`。

## 本轮其它改动逐项审视

| 编号 | 按实际用途核对的内容 | 当前结果 |
|---|---|---|
| N1 日常操作 | 长按力度、自动重复松键、编辑器 Home、P 键盘及前后倚音间距 | 按住与真实松开分开处理；Home 沿用普通播放、选段试听和循环各自起点。倚音额外间距保存到原生属性。继续保留现有按键、配色及间距。 |
| N2 混响 | 混音器发送、Fluid、独立 SF2 与原生 Zita1 的声音路径 | 沿用已核对的 Kawai 三档实际输出；发送量的重复缩小已在 0.159 修正。F11 中选择 Zita1，再在混音器调各乐器混响量。个人效果设置继续使用。 |
| N3 上游 | 批准的五项修复与 57 项提交报告 | 当前代码与报告对应，后续项目继续按报告安排。 |
| N4 多轨 MIDI | 导入落入所属乐谱、选轨、编辑、录制结果、写谱草稿、删除恢复、偏移与关联保存 | 从轨道列表到卷帘、力度和草稿使用同一当前轨。异步读取保留发起任务的乐谱；保存包含原始 MIDI、编辑和对应。重走了现有控件中的编辑、撤销和采用过程。 |
| N5 实际演奏起止 | 谱面轨与外部轨的编辑目标、拖动两端、取消、恢复及实际播放 | “演奏调整”保持初次关闭。拖动固定发声目标；记谱轮廓继续保留，实际偏移用于播放和 MIDI 导出。重新检查了拖动及恢复操作。 |
| N6 频谱 | 所选录音、固定时间块、缩放复用、外部 MIDI 叠加、共同时间尺 | 分析结果按音轨与文件身份管理；显示换算读取共同的原曲对应。重新检查浮动时间尺定位、空格、音符显隐及谱位对照，原有区域高度保留。 |
| N7 谱面原曲控制 | 分体播放按钮、同起点多个关联、停止、真实范围与手动移位 | 主按钮与箭头分别负责播放和选择。范围坐标独立于按钮位置。重新检查多片段播放、停止及再次播放。 |
| N8 动态乐谱 | 发布入口、原生画面、统一大小、谱表组合、声音时间、预览与编码 | 0.165 的入口修复继续保留，本次修正画面比例和统一缩放；完整画面及实际 MP4／透明 MOV 输出按同一渲染路径核对。 |
| N9 AI | 当前谱身份、44 项工具说明、原生图与简化图用途 | 保留现有数据流程，修正 MuseScore 原图的文字比例。工具清单与完整操作见 [AI 连接报告](AI_CONNECTION_IMPLEMENTATION_159.md)。 |

这次集中使用源码、保存资料、演奏事件和程序生成的画面；复用已有的 Kawai 输出、文件重开与兼容结果。实体 MIDI 键盘录制及演奏者听感仍按之前安排补查。

## 现在怎样使用

- **动态乐谱：**工具 → 动态乐谱视频… → 选择谱表和声音 → 准备画面 → 播放预览 → 导出视频…。升级后重新准备一次画面，便会采用新的尺寸计算。[完整步骤](SCORE_VIDEO_164_GUIDE.md)
- **外部 MIDI：**视图 → MIDI轨道，导入后选择轨名，可编辑、试听，再从“写谱草稿…”采用。[完整步骤](MIDI_TRACKS_160_GUIDE.md)
- **实际音长：**演奏编辑 → 开启“演奏调整”，拖主体或两端。[完整步骤](PERFORMANCE_TIMING_161_GUIDE.md)
- **频谱与参考录音：**从原曲参考选择录音，再到扒谱查看；两边使用同一条音轨和播放位置。[完整步骤](SPECTRUM_162_GUIDE.md)

## 后续顺序

1. 连接实体 MIDI 键盘后检查录制、停止、对应和采用，结合 Mi Monitor 听连续片段。
2. 依据现有 AI 报告讨论数据组织、资料范围与候选操作，补齐外部 MIDI、原曲和视频的专用接口。
3. 自动音符候选、音频和弦、自由演奏转谱及完整雕版／后处理继续按后续计划推进。淡化非旋律音量保持待讨论。

发布定位：`personal-v0.166.0`。编译、安装与提交信息完成后记入本页和更新日志。
'''
write('personal/docs/ROUND_166_REVIEW.md', review)
write('personal/docs/REWORK_PROGRESS.md', '''# 当前进度与后续完整计划

## 2026-11-08：0.166整轮审视与谱面输出修复

本次继续审视 N1—N9。动态乐谱修正文字与音符的分辨率换算，以及各谱行统一缩放；AI 原生谱图一并修正。用真实钢琴谱的第一行、中间三谱表及末行与原生输出比较，位置和比例一致。其它功能按编辑、试听、采用与保存的顺序核对，具体记录见 [0.166整轮审视](ROUND_166_REVIEW.md)。

当前正在编译与准备发布。接下来依次为实体 MIDI 键盘及连续音乐听感、AI 数据与交互扩展、后续自动扒谱和雕版／后处理。现有布局与个人设置继续保留。

以下保留各版原始记录。

''' + (N / 'personal/docs/REWORK_PROGRESS.md').read_text('utf8').split('\n', 1)[1].lstrip())
edit('personal/USER_GUIDE.md', lambda t: t.replace('当前版本：**0.165.0', '当前版本：**0.166.0', 1)
     .replace('本次动态乐谱入口修复与整轮审视见[0.165更新](docs/ROUND_165_REVIEW.md)（`personal-v0.165.0`）。',
              '本次修正动态乐谱与AI谱图的文字比例，统一各行音符大小；完整进度见[0.166整轮审视](docs/ROUND_166_REVIEW.md)（`personal-v0.166.0`）。', 1))
edit('personal/docs/SCORE_VIDEO_164_GUIDE.md', lambda t: t.replace(
    '## 从哪里打开', '''## 画面与原谱的关系

视频直接使用 MuseScore 已排好的谱面。音符、文字、字号、线条、人工位置和分行都沿用原谱，整行一起放大或缩小。0.166 修复了文字比例及各行大小不一致的问题。升级后点一次“准备画面”更新预览。

要改变一行的音乐内容或净谱，先回到乐谱修改，再准备画面；视频里的边距、位置、背景及换行时间在本面板调整。

## 从哪里打开''', 1))
edit('personal/docs/ROUND_165_REVIEW.md', lambda t: t.replace('\n\n',
     '\n\n后续在实际谱图中查到文字比例与统一缩放问题，修复及完整审视见[0.166记录](ROUND_166_REVIEW.md)。\n\n', 1))
edit('personal/CHANGELOG.md', lambda t: t.replace('\n\n', '''

## 0.166.0 — 2026-11-08

- 修正动态乐谱的图像分辨率，使文字、音乐符号与音符保持原谱比例、位置和字体。
- 各谱行按原谱尺寸统一缩放，正确处理不同分辨率的准备图片。
- AI 原生谱图采用相同的分辨率修正；音符引用与位置继续对应当前原谱。
- 用真实钢琴谱核对原生输出与视频画面，继续审视 N1—N9 的编辑、试听、采用和保存；保留已有操作和布局。
- 两仓库 AGENTS 增加原谱输出及完整范围返工要求。用户操作与本轮结果见 ROUND_166_REVIEW.md。
- 发布定位 personal-v0.166.0；安装与提交信息随后补入。

''', 1))
path = N / 'personal/docs/source-map.tsv'
rows = list(csv.reader(io.StringIO(path.read_text('utf8')), delimiter='\t'))
rows.extend([
    ['谱面输出尺寸', 'mscore/scorevideo/scorevideo.cpp', 'const int dotsPerMeter', '474', '原生文字与音乐符号共同缩放', 'mtest/mscore/pluginhost/scorevideo_166_review.inc'],
    ['视频统一比例', 'mscore/scorevideo/scorevideoframe.cpp', 'const double raster =', '61', '按原谱单位对齐各行', 'mtest/mscore/pluginhost/scorevideo_166_review.inc'],
    ['AI原图尺寸', 'mscore/workflow/arrangementimages.cpp', 'const int dotsPerMeter', '100', '原生谱图设备分辨率', 'mtest/mscore/pluginhost/scorevideo_166_review.inc']])
for row in rows[1:]:
    source = H / row[1]
    if source.is_file() and row[3].isdigit():
        matches = [i for i, line in enumerate(source.read_text('utf8').splitlines(), 1) if row[2] in line]
        if matches:
            row[3] = str(min(matches, key=lambda i: abs(i-int(row[3]))))
buf = io.StringIO()
csv.writer(buf, delimiter='\t', lineterminator='\n').writerows(rows)
write('personal/docs/source-map.tsv', buf.getvalue())
files = json.loads((O / 'sync-files.json').read_text('utf8'))
files += ['personal/VERSION', 'personal/USER_GUIDE.md', 'personal/CHANGELOG.md',
          'personal/docs/ROUND_166_REVIEW.md', 'personal/docs/REWORK_PROGRESS.md',
          'personal/docs/SCORE_VIDEO_164_GUIDE.md', 'personal/docs/ROUND_165_REVIEW.md',
          'personal/docs/source-map.tsv']
(O / 'release-files.json').write_text(json.dumps(files, indent=2), encoding='utf8')
print('Updated the native guide, complete review, source map and release version.')
