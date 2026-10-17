from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore';D=R/'staged057/native'
def stage(k,s):
 p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
guide='''# 演奏力度：对比、试听和使用

## 力度参考线是什么

这条虚线表示谱上的 p、mf、渐强渐弱在这一拍给出的力度。例如右手 mf 为 80、左手 p 为 48，两条线分别显示在 80 和 48。按相对方式保存的音，还会结合重音等演奏处理计算播放力度；指向对比柱可以一起查看。

“MIDI力度”显示 1–127 的实际数值；“相对%”显示各音相对自身演奏基础力度的增减。两个谱表都是 0% 时，分别沿用各自力度。想同时观察高低谱表的差别，选择“MIDI力度”，勾选“显示力度参考线”。“力度同图／按谱表分区”可以切换排列。

## 从 MIDI 采用一段演奏力度

1. 在谱面选中要调整的一段，打开“演奏表达”。
2. 点“导入MIDI”，选择演奏文件。全曲 MIDI 会先寻找所选谱段，再显示对应结果。实时演奏可用“录制／停止”。
3. 对应完成后，在演奏编辑器查看“演奏前后对比”。默认“同音对比”：中性色柱是谱中力度，强调色柱是拟采用力度；同一个音的两根柱排在一起。
4. 新导入默认“采用演奏力度的比例”为 100%。例如原值 80、导入值 100，100%采用 100，50%采用约 90。
5. 选择“逐音固定力度”或“继续跟随力度记号”。
6. 选择应用范围：“选中音／当前选段／全部已对应范围”，点击“使用力度”。一次应用可以用 Ctrl+Z 撤销。

已经使用的音退出待处理对比，普通编辑器显示保存后的结果。项目中剩余的匹配仍可继续使用。

## 两种保存方式

**逐音固定力度**是新材料的默认方式。例如导入值为 100，这个音保存为 MIDI 力度 100。谱上的 p、mf 仍然显示，其它音继续采用各自设置。

**继续跟随力度记号**把目标值换算成这个音的相对增减。例如当前位置给出的基础力度为 80，目标为 100，保存约 +25%。以后修改这一处的力度记号或渐强渐弱，这个音会跟着变化。相对百分比按整数保存，界面会显示取整后的结果。

已有项目恢复自己的比例和保存设置。“保留各音原保存方式”可继续使用先前的相对或固定方式。

## 查看速度变化

“同音对比”把原、新力度对齐到同一谱位，方便判断每个音变了多少。

选择“真实播放时间对比”后，时间尺显示秒数，两种效果按各自速度排列。慢下来的候选会展开到更后面。鼠标缩放、水平浏览和选音沿用编辑器的操作。对应轨中保留导入 MIDI 的原始演奏时间。

点击中性色柱选择谱中音；拖动强调色柱调整拟采用力度。有选音时，铅笔和直线只调整所选音。声部与谱表筛选共同作用于两边。

## 参考线、试听和恢复

对比时默认收起力度参考线，方便看清两根柱；可勾选“显示力度参考线”。普通编辑和对比各自记住这个开关。

点“谱中效果”或“拟采用效果”试听，界面显示当前播放对象。切换时保持当前小节、拍位和反复次数。试听、绘图和“使用力度”采用同一份候选。

首次使用力度前，原值随音符保存。通过“恢复应用前力度”按选音、选段或全曲恢复；保存 MSCZ 后重新打开仍可恢复。人工对应、原始 MIDI 和比例等项目设置可在演奏表达项目中保存。
'''
stage('personal/docs/REPAIR_057_GUIDE.md',guide)
(R/'docs/REPAIR_057_GUIDE.md').write_text(guide,encoding='utf8')
stage('personal/VERSION','0.57.0\n')
s=(H/'personal/USER_GUIDE.md').read_text(encoding='utf8').replace('当前个人版本：**0.56.0**','当前个人版本：**0.57.0**')
s=s.replace('记号力度','力度参考线').replace('显示力度参考线线','显示力度参考线').replace('力度强度 %','采用演奏力度的比例')
s=s.replace('本轮各项问题和保存方式见[逐项说明](docs/REPAIR_048_052_DELIVERY.md)。','本轮操作和九项问题的处理结果见[本轮逐项说明](docs/REPAIR_053_057_DELIVERY.md)。')
s=s.replace('## 打开功能','## 0.57 的力度对比\n\n新导入和录制默认采用全部演奏力度，并逐音固定保存。编辑器默认同音对比，可切换真实播放时间；原值与拟采用值用并列实心柱显示。完整操作见[演奏力度说明](docs/REPAIR_057_GUIDE.md)。\n\n## 打开功能',1)
s=s.replace('mf、p和渐强渐弱给出的数值叫“力度参考线”；','“力度参考线”显示 mf、p 和渐强渐弱在当前位置给出的数值；')
s=s.replace('细框是谱中力度，实心条是拟采用力度。','中性色柱是谱中力度，强调色柱是拟采用力度。').replace('实心条也可以直接拖动','强调色柱也可以直接拖动').replace('docs/images/expression-049-editor.png','docs/images/expression-same-note-057.png')
stage('personal/USER_GUIDE.md',s)
s=(H/'personal/CHANGELOG.md').read_text(encoding='utf8').replace('# 个人版本更新日志','# 个人版本更新日志\n\n## 0.57.0 — 2026-10-17\n\n- 编辑器采用并列实心柱显示同音力度对比，可切换秒数时间尺查看不同速度的实际播放位置。\n- 新 MIDI 和录制默认 100% 演奏力度、逐音固定；可选择跟随力度记号，已有项目保留原设置。\n- 力度参考线分别读取谱表动态，重音等播放处理单独说明；普通编辑和演奏对比各自记住显示开关。\n- 试听、候选绘图与应用共用保存方式；按音、选段、全部对应范围应用，继续支持撤销及保存后恢复原力度。\n- 操作：personal/docs/REPAIR_057_GUIDE.md；提交定位：personal-v0.57.0。',1);stage('personal/CHANGELOG.md',s)
s=(H/'personal/docs/source-map.tsv').read_text(encoding='utf8')+'演奏力度对比\tmscore/performanceeditor/expressioncompare.cpp\tcomparisonDisplayTick\t42\t同音、实际时间与候选编辑\texpressionVelocityModesAndComparison\n力度采用方式\tmscore/workflow/workflowexpression.cpp\tScoreObserver::applyExpression\t77\t固定、跟随与原方式\texpressionVelocityModesAndComparison\n';stage('personal/docs/source-map.tsv',s)
