# coding: utf-8
from pathlib import Path
import subprocess,shutil
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix=ROOT/'USER_GUIDE.md';text=prefix.read_text(encoding='utf8').replace('**0.35.0**','**0.36.0**')
old='附点、符杠和延音分别表达时长、分组和持续。自动分割不代表所有延音两端都应该用符杠连接。手动指定的符杠、复杂连音、自定义演奏等保留原设置。特殊记谱需要原样输入时可暂时关闭开关。'
new='''**例子一：改掉附点四分后面的八分。** 在4/4第一拍输入附点四分，再输入八分。选后面的八分，把时值改为四分；它会写成八分＋八分，延音跨过第三拍。前面的附点四分保持原样，持续时长和输入光标的位置都不丢失。

**例子二：3-3-2。** 第一拍起输入“附点八分、附点八分、八分”。中间的附点八分在第二拍处分为十六分＋八分，以延音相连。下面是协调符干后的效果，两个延音音符仍按拍点分成两组符杠。

![4/4的3-3-2输入与延音两端符干](docs/images/input-332-036.png)

**跨拍是否连符杠。** “工具 → 允许延音音符跨拍连符杠”首次关闭，保留主要拍点的分组。开启后，同一小节内完整延音连接的短音可以跨拍相连；不会跨小节自动连，也不会覆盖手动指定的分组。这个开关只改变净谱，不改变发声时长。

**协调延音两端的方向。** “工具 → 协调延音两端的自动符干”首次开启。普通单声部、音区相近的音组按这一小段音符的主要方向协调；同一个持续音只算一次。多声部、跨谱表、宽音区、震音、连音组及手动方向继续用原有规则。关闭即可使用原来的自动方向。

这两个设置会重新排版已打开的谱子；播放时先停止，等待乐谱准备完成。它们不写成音符的手动属性；普通MuseScore按自己的规则显示。需要固定保存一种符杠／符干写法时，用原有手动设置，或导出PDF。

附点、符杠和延音分别表达时长、分组和持续。手动指定“不连符杠”的音也会保留设置，自动时值重组不再把它改掉。复杂连音、自定义演奏等保留原设置；特殊记谱需要原样输入时可暂时关闭自动规范开关。'''
assert old in text;text=text.replace(old,new);prefix.write_bytes(text.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n'
guide=HOST/'personal/USER_GUIDE.md';working=guide.read_text(encoding='utf8');committed=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(committed)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.36.0\n')
shutil.copyfile(ROOT.parent/'P1/out/final-regression/input-332-coherent.png',HOST/'personal/docs/images/input-332-036.png')
log=HOST/'personal/CHANGELOG.md';s=log.read_text(encoding='utf8');at=s.index('## 0.35.0')
entry='''## 0.36.0 — 2026-10-13

- 修复自动时值重组覆盖手动“不连符杠”的情况。核对4/4第一拍的附点四分＋八分改四分，以及附点八分＋附点八分＋八分输入：拍点拆分、延音总时长和光标正确。
- 工具菜单增加跨拍延音连符杠开关，默认关闭；同小节完整延音的短音可相连，手动分组优先。不增加手动音符属性，也不改变MIDI事件。
- 增加自动延音符干协调，默认开启；只处理普通单声部、音区相近的局部音组。手动方向／符杠、多声部、跨谱表、宽音区、连音组和震音保留原规则。控制器与计算独立；只调整排版缓存，无音频回调改动。
- Git父提交4ea0121df；提交定位personal-v0.36.0。输入44项、原有符杠19项、原MIDI79项、实际菜单／设置及既有P0操作14项通过。原符杠测试补Windows类型限定与宿主链接，预期结果文件未改。说明书加入两个完整例子及实际图示。
- 此处符干协调为本分支在普通紧凑音组中的选择；参考Dorico公开符干／分组说明，尚未逐条核对Behind Bars完整正文，不把所有延音同向当成通用规定。

'''
log.write_bytes((s[:at]+entry+s[at:]).encode('utf8'))
index=HOST/'personal/docs/source-map.tsv';s=index.read_text(encoding='utf8')
for path,symbol,role in [('libmscore/inputnotation.cpp','bool joinTiedChords','完整延音、同小节与手动分组保护'),('libmscore/inputnotation.cpp','void coordinateTieStems','紧凑普通音组的自动方向协调'),('mscore/inputnotationmenu.cpp','void addInputNotationMenu','工具菜单、设置记忆及停止播放后排版')]:
 line=next(i for i,v in enumerate((HOST/path).read_text(encoding='utf8').splitlines(),1) if symbol in v)
 s+='\t'.join(['输入净谱',path,symbol,str(line),role,'mtest/libmscore/inputrhythm; mtest/libmscore/beam; mtest/mscore/p0native'])+'\n'
index.write_bytes(s.encode('utf8'))
plan=ROOT.parent/'Planning/REPAIR_IMPLEMENTATION.md';s=plan.read_text(encoding='utf8').replace('第3批记谱、线条与分手项目以及第4–6批继续实施。','第3批输入净谱已发布0.36.0：两个4/4例子、手动不连符杠保护、跨拍连符杠选择和紧凑音组的符干协调；输入44、符杠19、MIDI79及菜单／P0操作14项通过。第3批速度符号面板、自由圆滑线与分手项目，以及第4–6批继续实施。');plan.write_bytes(s.encode('utf8'))
readme=ROOT/'README.md';s=readme.read_text(encoding='utf8').replace('0.32.0–0.35.0','0.32.0–0.36.0').replace('和Tap速度标记联动','、Tap速度标记联动和输入净谱');readme.write_bytes(s.encode('utf8'))
