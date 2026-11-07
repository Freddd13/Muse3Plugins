"""Record checked N5 operations and the next fixed task."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
for name in ('pluginhost-performanceTimingPersistence161.txt','pluginhost-existingEditorProfileFirstOpen.txt','performanceeditor-wheelSelectionCommit158.txt'):
    if not re.search(r'Totals: \d+ passed, 0 failed, 0 skipped',(OUT/name).read_text('utf8',errors='replace')):raise ValueError('Incomplete '+name)
program=json.loads((OUT/'program-checks.json').read_text('utf8'))
if hashlib.sha256((HOST/'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe').read_bytes()).hexdigest()!=program['sha256']:raise ValueError('Program differs')
text='''# 0.161 实际起音与松键检查

本批完成N5谱面轨的演奏起止；N4临时MIDI和写谱草稿继续使用。独立测试谱、Windows原生窗口、实际演奏事件及保存文件均已核对。

## 实际操作

- 开启演奏调整后，实心条显示真实按键，原谱轮廓保持。真实鼠标移动主体、拖松键点、Esc取消、选音恢复均通过。
- 两个选中音一起移动，相对距离保持，一次拖动一次撤销。窗口失焦时结束已拖出的修改，归还鼠标；随后仍能点击、恢复和关闭工具。
- 指向移动、拉长后的实际音符滚轮调力度，更新正确的音。力度改变后演奏事件缓存继续复用，发声条与数量保持可用。
- 原生普通音、同小节与跨小节延音、倚音、琶音和颤音的起音／松键偏移与输出一致；原NoteEvent、Auto/User模式和记谱时值保持。
- 链接总谱与分谱的调整一同撤销、重做。保存MSCZ后重开，偏移及真实演奏结果一致；音符复制携带调整。
- 导出的MIDI重新读取，改动后的起止与原生事件一致。发声次数不符的旧调整保留并显示音型变化提示，可恢复后重调。
- 较大提前起音扩展原生播放准备，连续播放会提前读到对应事件。普通谱的空数据路径保持原处理。

![本批实际编辑器](images/performance-timing-161.png)

## 已有操作回查

多轨实际输出、导入／录制／草稿采用、原曲对齐、独立与随谱播放、Home、辅助资料撤销版本、长按力度和P键盘通过。原生编辑器的多音滚轮、手势中断、力度保存、mf/p分别换算、链接分谱、踏板、选音与筛选继续通过。

复制已有工作区的60项设置首次打开，卷帘328像素、参数区201像素均可见，布局后高度保持。截图保留原配色，控件按实际宽度排列。

原生窗口整组17项通过（含初始化和结束）；原编辑器整组15项通过，旧工作区3项通过。具体过程保存在本批日志中。

## 完整程序与普通版

- 0.161普通MIDI与0.160逐字节相同，均181字节；PDF正常导出。
- 官方MuseScore3.6.2实际打开并重存测试谱，6个音的音高、时值及谱面内容保持。本分支重新打开并导出MIDI、PDF成功。
- 官方版重存会移除逐音演奏时间资料；本分支原稿保留这组资料，导出MIDI携带实际演奏。

程序SHA-256：`'''+program['sha256']+'''`。发布定位：`personal-v0.161.0`。当前准备更新原安装目录，安装结果随后记入本页。

接着处理N6频谱固定块与缩放复用、键盘／谐波和MIDI叠加，然后N7关联控件、N8动态乐谱。实体键盘与演奏者听感按用户安排补查。
'''
(NATIVE/'personal/docs/PERFORMANCE_TIMING_161_CHECKS.md').write_bytes(text.encode('utf8'))
progress=NATIVE/'personal/docs/REWORK_PROGRESS.md';text=progress.read_text('utf8')
if '## 2026-11-07：0.161 卷帘演奏起止' not in text:
    heading='''## 2026-11-07：0.161 卷帘演奏起止

N5已完成实际起音／松键拖动、恢复、链接与保存。鼠标、多选、失焦、滚轮、实际MIDI、旧工作区和普通版读取已检查，正在更新程序目录。见[操作](PERFORMANCE_TIMING_161_GUIDE.md)与[检查](PERFORMANCE_TIMING_161_CHECKS.md)。

| 编号 | 当前结果与下一项 |
|---|---|
| N1—N3 | 0.159操作、Kawai混响及上游适配已交付 |
| N4 | 0.160多轨MIDI、录制、对齐、编辑与写谱草稿已交付 |
| N5 | 0.161谱面轨演奏起止与恢复已检查 |
| N6 | 下一项：频谱固定分析块、相邻准备与缩放复用、键盘／谐波、MIDI叠加 |
| N7 | 原曲关联范围、分体播放和可移动／隐藏控件 |
| N8 | 动态乐谱、实际谱表组合、换行时间、MP4和透明MOV |
| N9 | AI44项工具、数据与流程报告已交付，后续结构另行讨论 |

接着按N6、N7、N8推进；实体键盘和真实音乐听感继续保留。以下为已交付记录。

'''
    text=text.replace('# 当前进度与后续完整计划\n\n','# 当前进度与后续完整计划\n\n'+heading,1)
progress.write_bytes(text.encode('utf8'))
plan=ROOT/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';text=plan.read_text('utf8').replace('临时轨与量化草稿已接通；接着实现谱面轨实际起止调整','0.161谱面轨实际起止、恢复、保存与撤销已检查；临时轨与量化草稿继续使用',1);plan.write_bytes(text.encode('utf8'))
print('Recorded N5 results and N6–N8 order')
