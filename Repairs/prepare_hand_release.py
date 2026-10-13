# coding: utf-8
"""Update the hand-marker release documentation without replacing other tasks' text."""
from pathlib import Path
import shutil,subprocess
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
p=ROOT/'USER_GUIDE.md';guide=p.read_text(encoding='utf8')
guide=guide.replace('当前个人版本 **0.38.0**','当前个人版本 **0.39.0**')
guide=guide.replace('虚线长度和间隔。隐藏线条仍会渐慢。','虚线长度和间隔。需要自定虚线长度和间隔时选择“自定义虚线”；普通虚线使用固定比例。隐藏线条仍会渐慢。')
guide=guide.replace('a tempo表示回到这次渐变前的速度；','a tempo在恢复所在的拍位上方对齐，不再因为位于第一拍而偏到拍号上方；手动偏移保留。a tempo表示回到这次渐变前的速度；')
old='选中记号，检视器可改横／竖长度、粗细、是否显示LH/RH及方向。双击后拖端点改形状，拖整体改位置，Esc取消。关闭可伸缩模式恢复原字形。保存到本分支的MSCZ会保留形状；其它版本可能不保留个人扩展。'
new='''**第一次添加。** “指法”面板现在有左手开始、右手开始、左手结束、右手结束四种格子，缩小图例以便辨认。选中具体音后添加：右手标记先放在这个音上方，左手先放在下方；若附在整个和弦，分别参考最高音／最低音。自动布局会在附近尝试避开音头、变音记号和符干。特别密的写法仍可手调，不保证每种排列都能找到空位。

**调形状与位置。** 检视器改横／竖长度、粗细、是否显示LH/RH及方向。双击后拖端点改形状，拖整体改位置，Esc取消。调整过形状或整体位置后保留当前放置，不让再次排版把折线挪回去。重新开启“自动布局”可以重新寻找放置位置；关闭自动布局后仍给出靠近所指音的初始位置。线附近可以点击选中，整块空白区域不会挡住音符。

**保存常用形状。** 只选一个标记，调好长度和线宽，再点“保存为以后添加的形状”。四种标记分别保存；新建默认指法面板时使用它，已有格子保留自己的设置。想在当前标记上采用保存的形状，点“使用保存的默认形状”。播放时未保存的调整需先停播。此按钮改当前标记，可一次撤销；保存个人默认设置不改变谱子。

开始和结束成对时，编配检查读取这段分手信息；只有一个标记时只解释它所指的音或和弦，不影响后面整段。标在和弦里的单个音上，也不会把整个和弦都当成同一只手。范围内有多个声部而不能确定所指线条时会要求确认。折线是否开启、是否显示LH/RH都不改变左／右手含义。

关闭可伸缩模式恢复原字形。当前版MSCX／MSCZ会保存形状与手动放置；较早个人版及普通MuseScore可能不保留这些外观扩展。新默认位置和自动避让只作用于本项目的可伸缩分手标记。

![左右手折线的形状和默认设置](docs/images/hand-039.png)'''
if old in guide:guide=guide.replace(old,new)
elif 'hand-039.png' not in guide:raise RuntimeError('Cannot identify hand instructions')
p.write_bytes(guide.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n'
target=HOST/'personal/USER_GUIDE.md';working=target.read_text(encoding='utf8')
committed=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(text):return text.split(marker,1)[1].rsplit('\n</details>',1)[0]
target.write_bytes((guide+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((guide+history(committed)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.39.0\n')
image=HOST/'personal/docs/images/hand-039.png';image.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'out/hand-gui/hand-symbol-inspector.png',image)
report='''# 左右手标记与恢复速度检查（0.39.0）

- 演奏编辑器全部51项通过；分手标记专项6项通过，编配规则29项通过。
- 实际鼠标：折线端点、整体点击、箭头、Esc取消、撤销、保存／读取个人默认形状、使用默认形状；播放中修改仍等待停播。
- MSCX／MSCZ、分谱链接、原MIDI事件、PDF／SVG、自动与手动放置已检查。四种面板格子保持独立，重复补齐不重复添加。
- a tempo在拍位处对齐，普通速度文字对齐保持原规则。手动偏移保留。
- 没有修改任何OneDrive官谱。系统剪贴板子检查未运行，不能把这次结果当作剪贴板功能验收。
- 自动放置只寻找附近有限位置；密集内容仍可手动调整。标记之间多个同时音不能可靠归入一个连续声部时提示确认。
- 本批提交定位：personal-v0.39.0；父提交531f11267。
'''
(HOST/'personal/docs/HAND_MARKER_VALIDATION.md').write_bytes(report.encode('utf8'))
log=HOST/'personal/CHANGELOG.md';text=log.read_text(encoding='utf8');anchor='## 0.38.0 —'
entry='''## 0.39.0 — 2026-10-13

- 左右手折线按所指音／和弦寻找附近位置，四种开始／结束格子缩小显示；手动偏移与形状调整保留，保存MSCX／MSCZ后恢复。点击范围贴近折线。
- 新增按四种标记分别保存的个人默认形状及使用按钮。已有自定义格子保留，不自动改写。
- 查询返回左／右手、开始／结束和附着音信息。编配检查不再用外形决定范围；未成对标记只作用于所指音，冲突／多声部关系需确认。对位检查补齐前后音说明和单声部移动的交叉检查。
- a tempo在第一拍也对齐恢复拍位，普通速度文字的原对齐保持。说明补齐自定义虚线的选择方法。
- Git父提交531f11267；提交定位personal-v0.39.0。演奏编辑器51项、分手标记专项6项、编配规则29项通过。详情personal/docs/HAND_MARKER_VALIDATION.md；系统剪贴板仍未验收。

'''
if '## 0.39.0 —' not in text:text=text.replace(anchor,entry+anchor,1)
log.write_bytes(text.encode('utf8'))
index=HOST/'personal/docs/source-map.tsv';text=index.read_text(encoding='utf8')
for title,file,symbol,description in [
 ('分手标记','libmscore/handbracket.cpp','QPointF position(','附着音附近的有限位置候选与碰撞检查'),
 ('分手标记','mscore/handbracketsettings.cpp','void addHandBracketDefaultControls(','四种个人默认形状、设置读写与面板按钮'),
 ('分手标记','mscore/handbracketsettings.cpp','void completeHandBracketPalette(','四种格子补齐与缩小显示'),
 ('分手标记','mscore/plugin/api/arrangementsnapshot.cpp','auto handData','完整分手含义与附着音信息')]:
 lines=(HOST/file).read_text(encoding='utf8').splitlines();matches=[i+1 for i,line in enumerate(lines) if symbol in line]
 if len(matches)!=1:raise RuntimeError('Source index symbol: '+symbol)
 entry='\t'.join([title,file,symbol,str(matches[0]),description,'mtest/mscore/performanceeditor; ArrangementAssistant/tests/test-rules.cjs'])+'\n'
 if file+'\t'+symbol+'\t' not in text:text+=entry
index.write_bytes(text.encode('utf8'))
print('0.39说明和发布记录已准备；其它任务的用户说明保留。')
