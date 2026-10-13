# coding: utf-8
"""Write the practical guide and retain unrelated additions to its appendix."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
p=ROOT/'USER_GUIDE.md'
guide=p.read_text(encoding='utf8').replace('当前个人版本 **0.41.0**','当前个人版本 **0.42.1**').replace('当前个人版本 **0.42.0**','当前个人版本 **0.42.1**')
guide=guide.replace('| 比较不同写法 | 启用 ArrangementVariants_MS3.qml，然后插件 → Arrangement Variants |','| 比较不同写法 | 工具 → 分段试写方案；旧版完整副本仍从插件 → Arrangement Variants 打开 |')
start=guide.index('## 13.');end=guide.index('## 14. MIDI裁剪',start)
guide=guide[:start]+'''## 13. 分段试写方案：在一个文件中尝试不同写法

**用途。** 第9–12小节的左手可以有A、B两种写法，第25–28小节的旋律也可以有自己的几种写法。切换左手不会替换右手，也不会替换整首谱。全部写法保存在一个MSCZ文件中；不需要为每一种组合保存一份全谱。

**第一次试写。**

1. 在总谱中选第9–12小节，打开“工具 → 分段试写方案”。旧插件的“内置分段方案”也能打开同一面板。
2. 点“建立组”。填写名称，核对开始和结束小节。在谱表表格中勾选要尝试的声部：每行一个谱表，1–4是MuseScore的四个声部。只想改左手，就只勾选相应谱表和声部。点确定。
3. 列表出现这组方案和“原写法”。悬停组名或范围，可以查看所含谱表、声部。
4. 点“复制写法”，输入“B · 分解和弦”等名称。软件保存原写法，打开新写法；现在直接在谱面改音符、节奏、音旁标记或演奏数值。
5. 点列表中的“原写法”，再点“切换写法”，或双击它。所选小节和声部回到原写法。再切到B，你刚才的编辑仍在。当前所用写法标有“当前”。
6. “同处试听”播放当前组合，并包含必要的进入前文。停止使用原来的播放按钮或空格。没有声音设备时会显示原因，仍可以切换和查看。
7. Ctrl+S保存为MSCZ。以后用本分支打开，恢复上次编辑的组合和全部写法。Ctrl+Z可以撤销编辑、复制、改名、范围扩大和切换；一次切换一次撤销。

可以再为另一段或另一声部建立一组。相同时间的右手与左手能各自切换；同一批音符不能同时属于两组。速度、踏板、调号、谱表文字、和弦文字及力度记号共同使用；单个音的力度、手工演奏事件和附着标记随写法保存。

**范围与连线。** 第一版使用完整小节，各种写法的总拍数、拍号和谱表结构相同。连音组、双音震音、符杠、延音线、圆滑线及歌词延续不能被范围截断；跨谱表记谱须包含相关声部。不能切换时会说明原因。

选中组后点“扩大范围”，选择更早的开始小节或更晚的结束小节。新加入的内容复制给每一种写法，当前谱面不变。需要跨段延音或圆滑线时，先扩大，再添加连接。如果已加了跨界连接，先撤销该连接，扩大后重新添加；软件不会为切换直接删掉它。扩大后不能占用另一组已经使用的声部。改变已有方案段的拍号、总长度或谱表结构会使它暂时不能切换或保存全部写法；撤销这一变化，或导出当前组合的普通版副本。

**主方案、打印和普通版。**

- 每组选择一种写法，点“设为主方案”。普通MuseScore打开这个MSCZ时，会看到各组主方案组成的完整乐谱。
- “显示主方案组合”把屏幕切到这份组合。打印、PDF、MIDI和常规导出使用当前屏幕所示组合；需要另一组合时先切换，再导出。
- “普通版副本”可选“当前屏幕组合”或“普通版主方案组合”，另存为一份不含其它写法的MSCZ。它不改变当前文件的位置，也不覆盖当前打开的谱。
- 含全部方案的乐谱请保存为MSCZ，不能直接另存为MSCX。普通版打开后重新保存，可能丢掉其它写法；向别人发送或用普通版继续编辑时，先导出普通版副本。

**旧项目怎样继续用。** 原来的“Arrangement Variants”仍保留完整谱副本、JSON列表、差异检查及试听。可以直接继续使用。要迁入新功能，先建立接收这些小节和声部的组，点“导入旧写法”，选旧JSON或单独MSCZ／MSCX；JSON中有多组时再选择其中一组。只导入本组范围，段外改动和共同设置不替换。旧谱的拍号、长度和谱表不一致，或文件缺失／已改变时会说明，旧文件不会删除。导入后仍要选择写法并切换，才会显示它。

面板首次与右侧检视器等并列；支持换位置和悬浮。分谱跟随总谱内容；建立或切换方案时先回到总谱。

![分段方案面板](docs/images/regional-042.png)

''' +guide[end:]
guide=guide.replace('本轮正在分批修复。单MSCZ分段方案仍在实现中，不能仅凭计划当成已交付。本版已有受条件保护的旧音松手安排，仍没有完整指法生成。每批发布后会更新对应章节和截图。','本轮修复及多音频、演奏对应、单MSCZ分段方案已交付。裁剪能在条件允许时安排旧音松手，仍没有完整指法生成。')
p.write_bytes((guide.rstrip()+'\n').encode('utf8'))
marker='<summary>展开较早版本说明</summary>'
def history(text):return text.split(marker,1)[1].lstrip('\r\n').rsplit('</details>',1)[0].rstrip('\r\n')
target=HOST/'personal/USER_GUIDE.md'
working=target.read_text(encoding='utf8')
committed=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
prefix=guide.rstrip()+'\n\n'
target.write_bytes((prefix+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((prefix+history(committed)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.42.1\n')
print('0.42说明书与版本已更新；保留其它任务新增的说明。')
