# coding: utf-8
from pathlib import Path
import subprocess, shutil
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix=ROOT/'USER_GUIDE.md'
text=prefix.read_text(encoding='utf8').replace('**0.34.0**','**0.35.0**')
text=text.replace('下拉可选八分、四分、附点四分或二分单位，÷2／×2换算，重置重新测。','下拉可选十六分到全音符及附点单位，÷2／×2换算，“重新测量”从头开始。')
old='修改已有速度标记须先选中它；保留原拍单位和说明文字。a tempo、相对速度或曲线不能当作普通数字直接覆盖。若新值和旧值相同，不会产生多余改动。Ctrl+Z撤销写谱；估计本身不进入撤销记录。'
new='''**直接给速度标记 Tap。**

1. 点选谱面上的速度标记，在检视器点“用 Tap 设置速度…”，或在记号右键菜单使用同名入口。
2. 窗口会按这个记号的拍单位开始测量。例如原来是附点四分80，每次点击就代表一个附点四分。也可改为另一种点击单位。
3. 点击窗口内的“Tap · 点击一拍”，或继续使用原工具栏Tap。第二次起出现谱面预览；至少四次后才能保存。窗口同时显示点击单位速度和换算后的四分音符BPM。
4. 点“保存结果”或按回车，一次写入。Esc或“取消”恢复原来的显示。普通数字记号保留原拍单位和说明；只有文字的普通速度会补上数字速度。Ctrl+Z一次撤销本次结果。

预览不会改变谱内速度或试听声音。播放中可以测量和查看，停止播放、乐谱准备完成后才可保存。长时间没有敲击会提示暂停，可保存已有结果；再次开始长停顿后的点击会重新计算。测量期间换谱、删除或修改了目标记号，请关闭窗口后重新选择。

**rit. 的起速／终速。** 选中渐变速度线，在检视器点“用 Tap 设置起速／终速…”，或用线条右键菜单。选择要设置的端点，再敲击；保存会把这一端设为明确BPM，保留另一端和线条文字。与其它速度冲突时显示原因，不会顺便替换其它记号。

**a tempo 与速度关系。** 普通a tempo表示恢复先前速度，速度等式表示比例关系，不能直接当成固定数字。测速窗口保留其含义，提供“保留原记号，写入另一个位置…”；在位置窗口选择另一个起音点，新建固定速度。“恢复到指定BPM”可以直接Tap改变指定值，文字及恢复方式保留。

若新值与旧值相同，不增加多余改动。原工具栏的独立节拍器、倍／半速和写入指定位置功能仍可使用。

![直接测量所选速度标记，先预览再保存](docs/images/tap-035.png)'''
assert old in text;text=text.replace(old,new);prefix.write_bytes(text.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n'
guide=HOST/'personal/USER_GUIDE.md';working=guide.read_text(encoding='utf8')
committed=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(committed)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.35.0\n')
log=HOST/'personal/CHANGELOG.md';s=log.read_text(encoding='utf8');at=s.index('## 0.34.0')
entry='''## 0.35.0 — 2026-10-13

- Tap增加与运输控件相同风格的图标；工具栏与测速窗口共用八种点击单位和原菜单动作。速度记号右键和检视器直接开始Tap：每拍更新显示，谱面仅作临时预览；至少四拍后一次保存，回车保存、Esc取消，播放期间等待停止后写入。
- 普通速度保留原单位和文字，只有文字时显式补上数字。rit.可设置起速或终速；a tempo和速度关系保留原意思，可将测速结果写到另一个位置；指定BPM恢复可直接更新。换谱／目标被改后拒绝旧结果。
- 修复副本比较把默认MIDI端口／通道省略与明确写出当成不同设置；比较实际路由，非默认改变仍会发现。不改变保存格式、MIDI事件或声音。
- Git父提交a5f0e30a9；提交定位personal-v0.35.0。原生工作流17项通过，含实际检视器鼠标入口、预览与取消、一次保存／撤销／重做、过期目标、回车与指定恢复、rit.端点和MIDI路由差异。Tap重复点击、自动重复及节拍器旧入口另作检查。

'''
log.write_bytes((s[:at]+entry+s[at:]).encode('utf8'))
shutil.copyfile(ROOT.parent/'P1/out/final-regression/tap-dialog.png',HOST/'personal/docs/images/tap-035.png')
index=HOST/'personal/docs/source-map.tsv';s=index.read_text(encoding='utf8')
for path,symbol,role in [('mscore/taptempo/tapmark.cpp','void showTapMarkDialog','选中速度标记的临时预览与一次保存'),('mscore/taptempo/tapmark.cpp','QString tapTempoText','保留拍单位／说明文字的数字更新'),('mscore/workflow/workflowvariants.cpp','QVariantMap ScoreObserver::workflowFingerprint','比较实际MIDI路由，默认等价写法一致')]:
 line=next(i for i,v in enumerate((HOST/path).read_text(encoding='utf8').splitlines(),1) if symbol in v)
 if symbol not in s:s+='\t'.join(['速度与工作流',path,symbol,str(line),role,'mtest/mscore/p1native; mtest/mscore/p0native'])+'\n'
index.write_bytes(s.encode('utf8'))
plan=ROOT.parent/'Planning/REPAIR_IMPLEMENTATION.md';s=plan.read_text(encoding='utf8').replace('第3批其余项目与第4–6批继续实施。','第3批Tap联动已发布0.35.0：图标、更多单位、速度标记预览／一次保存／取消、rit.端点及速度含义保护；工作流17项通过。修复副本默认MIDI路由等价比较。第3批记谱、线条与分手项目以及第4–6批继续实施。');plan.write_bytes(s.encode('utf8'))
