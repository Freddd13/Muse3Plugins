# coding: utf-8
"""Prepare the reviewed chord-display release notes without staging user edits."""
from pathlib import Path
import subprocess, shutil

ROOT = Path(__file__).resolve().parent
HOST = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix = ROOT/'USER_GUIDE.md'
text = prefix.read_text(encoding='utf8').replace('**0.33.0**', '**0.34.0**')
old = '顶部摘要可与右侧详情同时显示。摘要选择实时音或所属和弦；拖到上方后调左右位置。谱面文字可选和弦、级数或两者，改排列、字号、配色和遮罩。双击谱面标记进入详情。'
new = '''**放在顶部看摘要。** 拖住和弦面板标题放到窗口顶部，摘要只占一行。点“靠左／居中／靠右／自定位置”按钮选择位置；自定位置可用滑条调整。点“详情”同时打开右侧完整面板；点“更多”可打开记号列表或悬浮面板。顶部菜单在独立小窗展开，不受摘要栏高度限制。摘要仍可选择实时音或所属和弦。

**谱面记号和遮挡。** 设置 → 外观中开启“谱面和弦”，选择和弦、级数或两者，再改左右／上下排列、字号和颜色。默认记号画在其它谱面内容上方；两个和弦互相挤到时上下排列，横向仍对齐各自开始的音符，不因找不到空位而省略。

“避让其它谱面内容”首次关闭。开启后尽量找空位，实在放不下仍显示；“遮罩”只控制记号背后的浅色底，两个开关分别生效。页面上方特别密集时也可能排到较低的位置，可关闭避让或调整字号。默认“优先已有和弦记号”会省去与原谱已有和弦相同的临时标记；要逐个查看助手的分析，可关闭这个选项。

点选和播放都强调当前固定位置的记号，双击进入详情。临时记号不会进入打印或PDF，退出插件即清除。

![相邻和弦上下排列，当前和弦高亮](docs/images/chord-034.png)'''
assert old in text
text = text.replace(old,new)
prefix.write_bytes(text.encode('utf8'))
marker = '<summary>展开较早版本说明</summary>\n\n'
guide = HOST/'personal/USER_GUIDE.md'
working = guide.read_text(encoding='utf8')
committed = subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):
    return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(committed)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.34.0\n')
log=HOST/'personal/CHANGELOG.md'
entry='''## 0.34.0 — 2026-10-13

- 和弦助手默认把临时和弦画在其它谱面内容上方；避让和遮罩可分别设置。自己的相邻记号上下排列，保持原拍位，不因空间不足省略。旧插件没有选用新显示方式时沿用原行为。
- 顶部摘要改为一行44像素内容；仍支持左、中、右和自定位置以及右侧详情。位置和更多菜单另开小窗，避免被矮栏裁切；保留标题栏拖动、悬浮、设置记忆和已有功能。
- Git父提交8d4edd2ff；提交定位personal-v0.34.0。实际鼠标菜单、停靠／悬浮、字体、选区、播放高亮、打印检查12/12；观察与临时显示17/17。原有识别算法本次未改，后续继续处理。

'''
s=log.read_text(encoding='utf8');at=s.index('## 0.33.0');s=s[:at]+entry+s[at:];log.write_bytes(s.encode('utf8'))
image=HOST/'personal/docs/images/chord-034.png'
shutil.copyfile(ROOT.parent/'P1/out/final-regression/chord-on-top.png',image)
index=HOST/'personal/docs/source-map.tsv'
s=index.read_text(encoding='utf8')
rows=s.splitlines()
for path,symbol,role in [('mscore/workflow/chordoverlay.cpp','void ScoreView::paintTopChordPreview','最上层临时和弦；不进入打印'),('mscore/notepreview.h','inline QRectF stackVisiblePreviewChord','自己的和弦上下排列，保持拍位')]:
    line=next(i for i,v in enumerate((HOST/path).read_text(encoding='utf8').splitlines(),1) if symbol in v)
    rows.append('\t'.join(['和弦显示',path,symbol,str(line),role,'mtest/mscore/pluginhost; mtest/mscore/scoreobserver']))
index.write_bytes(('\n'.join(rows)+'\n').encode('utf8'))
plan=ROOT.parent/'Planning/REPAIR_IMPLEMENTATION.md'
s=plan.read_text(encoding='utf8').replace('第3–6批继续实施。','第3批的和弦显示已发布0.34.0：顶栏一行、独立小菜单、最上层绘制、可选避让和遮罩，相邻记号固定拍位上下排列。菜单／实际显示12项和读取／临时显示17项通过；识别算法还未改。第3批其余项目与第4–6批继续实施。')
plan.write_bytes(s.encode('utf8'))
readme=ROOT/'README.md';s=readme.read_text(encoding='utf8').replace('当前已发布 0.32.0 和 0.33.0；','当前已发布 0.32.0、0.33.0 和 0.34.0；').replace('演奏编辑器修复和相关验证已完成。','演奏编辑器和和弦显示修复及相关验证已完成。')
readme.write_bytes(s.encode('utf8'))
