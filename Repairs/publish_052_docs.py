"""Publish the tested 0.52 guide and source locations. Run once for this release."""
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / 'Repairs'
HOST = ROOT.parent / 'muse3_dev/MuseScore'

for name, count in [('p1native', 49), ('performanceeditor', 62), ('p0native-retry', 23)]:
    log = (R / f'out/repair-052-candidate-{name}/gui.txt').read_text(encoding='utf8', errors='replace')
    assert f'Totals: {count} passed, 0 failed' in log, name
    assert not re.search(r'TypeError:|ReferenceError:|Unable to assign \[undefined\]', log), name

images = [
    ('regional-comparison-panel-052.png', 'comparison-052-variants.png'),
    ('regional-comparison-score-052.png', 'comparison-052-score.png'),
    ('midi-length-comparison-052.png', 'comparison-052-midi.png'),
    ('midi-length-editor-052.png', 'comparison-052-midi-editor.png'),
]
for folder in [R / 'docs/images', HOST / 'personal/docs/images']:
    folder.mkdir(parents=True, exist_ok=True)
    for source, destination in images:
        shutil.copy2(R / 'out/repair-052-candidate-p1native' / source, folder / destination)

guide = (R / 'USER_GUIDE_CURRENT.md').read_text(encoding='utf8')
start, end = guide.index('## 13. 分段试写'), guide.index('## 15. 字体')
guide = guide[:start] + (R / 'docs/COMPARISON_052_GUIDE.md').read_text(encoding='utf8').replace('(images/', '(docs/images/').rstrip() + '\n\n' + guide[end:]
guide = guide.replace('**0.51.0**', '**0.52.0**').replace('`personal-v0.51.0`', '`personal-v0.52.0`')
guide = guide.replace('## 打开功能', '本轮各项问题和保存方式见[逐项说明](docs/REPAIR_048_052_DELIVERY.md)。\n\n## 打开功能', 1)
(R / 'USER_GUIDE_CURRENT.md').write_text(guide, encoding='utf8', newline='\n')
(R / 'USER_GUIDE.md').write_text(guide.replace('[开发日志](CHANGELOG.md)', '[开发日志](../../muse3_dev/MuseScore/personal/CHANGELOG.md)'), encoding='utf8', newline='\n')
path = HOST / 'personal/USER_GUIDE.md'
existing = path.read_bytes()
marker = '## Codex 钢琴编曲与 MCP 桥接'.encode()
tail = existing[existing.index(marker):]
committed = subprocess.check_output(['git', 'show', 'HEAD:personal/USER_GUIDE.md'], cwd=HOST)
assert tail == committed[committed.index(marker):]
path.write_bytes(guide.rstrip().encode() + b'\n\n' + tail)
assert path.read_bytes().endswith(tail)
(HOST / 'personal/VERSION').write_bytes(b'0.52.0\n')

validation = '''# 0.52 写法和MIDI音长比较检查

2026-10-17，Windows x64、Qt 5.15.2。安装目录：msvc.install_repair_0_52_x64；提交标签：personal-v0.52.0。

## 写法对比与组合

实际打开面板，勾选显示差异，点变化列表定位，再用谱面按钮上的Ctrl+滚轮换写法。音高和力度变化出现在列表，另一写法以淡色叠加；缩放后按当前谱面的音符位置绘制。符杠各段使用对应起音位置。

两个声部分别保存A/B，保存组合、切换组合、整组撤销和重做均通过。保存MSCZ重开后，组合仍在。另行读取MSCZ中的普通乐谱入口，确认它显示主方案；本分支重开恢复正在编辑的组合。导出普通版副本读回后只有所选乐谱。

试听比较使用真实Seq与可记录输出的测试设备。切换后从同一谱段开始，B的指定力度112进入播放事件；标签页数量保持。

![组合和变化列表](images/comparison-052-variants.png)

## MIDI音长编辑与试听

鼠标拖动实心条尾端后，当前导出设置得到手动松手点；快速拖动后立即松开也保存最终位置。保护音、踏板边界、最短按键时长、恢复原长度和固定种子重复计算均检查通过。手动恢复原长度后，详情会更新对下一组音的说明。

打开演奏编辑器音长窗口，再返回导出，原编辑器父窗口和可见状态恢复。整个操作保持原谱内容、撤销位置和标签页数量。最终MIDI与按相同参数、手动点独立生成的文件逐字节一致。

原／新试听核对了实际播放事件：起音帧一致，候选的松手帧提前；切换保持当前拍位。反复出现的音使用各自导出位置匹配。顺带修复P键盘从未打开时清理播放音符的崩溃。

![音长前后对比](images/comparison-052-midi.png)

![演奏编辑器音长窗口](images/comparison-052-midi-editor.png)

## 整组检查

演奏编辑器62项、P1工作流49项、P0工具23项，共134项窗口与文件检查通过。P0使用当前SF3渲染两段材料，处理前后最大样本差为0。完整输出位于插件仓库Repairs/out/repair-052-candidate-*。

说明第13、14章按新按钮重写；本轮0–12项答复见[逐项说明](REPAIR_048_052_DELIVERY.md)。
'''
(R / 'docs/COMPARISON_052_VALIDATION.md').write_text(validation, encoding='utf8', newline='\n')
for name in ['COMPARISON_052_VALIDATION.md', 'REPAIR_048_052_DELIVERY.md']:
    text = (R / 'docs' / name).read_text(encoding='utf8').replace('../USER_GUIDE_CURRENT.md', '../USER_GUIDE.md')
    (HOST / 'personal/docs' / name).write_text(text, encoding='utf8', newline='\n')

path = HOST / 'personal/CHANGELOG.md'
text = path.read_text(encoding='utf8')
assert '## 0.52.0' not in text
entry = '''## 0.52.0 — 2026-10-17

- 分段试写增加淡色叠加和变化列表，区分音高、节奏、增删音、力度与标记；缩放后跟随谱面位置。组合保存各组选择，切换为一次撤销；保存和重开继续保留。
- 谱面写法按钮支持Ctrl+滚轮，“试听比较”开关控制切换后从同处听。普通MSCZ入口保留主方案组合，另附全部写法，旧工作区继续可用。
- MIDI松手对比增加可缩放音高行、原／新长度轮廓、踏板与下一组音强调；可拖尾端调整这次导出，进入演奏编辑器大图，再回到导出。
- 原／新MIDI音长使用准备好的实际播放事件试听，切换保持拍位。最终导出使用同一份参数、手动松手点；只调整允许提前的note-off。
- 修复未打开P键盘时播放清理访问空窗口的崩溃，修复快速拖动后松手位置未及时保存。
- 用户说明第13、14章及本轮0–12项操作答复已更新。检查记录：personal/docs/COMPARISON_052_VALIDATION.md；提交定位：personal-v0.52.0。

'''
path.write_text(text.replace('## 0.51.0', entry + '## 0.51.0', 1), encoding='utf8', newline='\n')

path = HOST / 'personal/docs/source-map.tsv'
rows = path.read_text(encoding='utf8').splitlines()
additions = [
    ('写法组合切换', 'libmscore/regionalvarianttools.inc', 'QVariantMap selectMany(', '整组选择和一次撤销', 'mtest/mscore/p1native/regional_comparison_tests.inc'),
    ('写法对比副本', 'libmscore/regionalvarianttools.inc', 'MasterScore* comparison(', '另一写法的只读排版材料', 'mtest/mscore/p1native/regional_comparison_tests.inc'),
    ('写法差异显示', 'mscore/workflow/regionalcomparison.cpp', 'class DifferenceLayer final', '按当前谱面位置显示变化', 'mtest/mscore/p1native/regional_comparison_tests.inc'),
    ('写法同段试听', 'mscore/workflow/regionalcomparison.cpp', 'QVariantMap switchRegionalWriting(', '切换写法及同处播放', 'mtest/mscore/performanceeditor/gate_playback_tests.inc'),
    ('MIDI松手范围', 'audio/exports/midigate.h', 'QPair<int,int> releaseBounds(', '允许手动调整的导出范围', 'mtest/mscore/p1native/gate_comparison_tests.inc'),
    ('MIDI音长试听', 'mscore/midicrop/gateaudition.cpp', 'GateAudition prepareGateAudition(', '导出出现位置与实际播放事件对应', 'mtest/mscore/performanceeditor/gate_playback_tests.inc'),
    ('MIDI音长绘制', 'mscore/midicrop/gateroll.inc', 'class GateRoll final', '原新轮廓和松手点拖动', 'mtest/mscore/p1native/gate_comparison_tests.inc'),
]
for topic, file, symbol, role, tests in additions:
    rows = [r for r in rows if '\t' + file + '\t' + symbol + '\t' not in r]
    hits = [i + 1 for i, line in enumerate((HOST / file).read_text(encoding='utf8').splitlines()) if symbol in line]
    assert len(hits) == 1, (file, symbol)
    rows.append('\t'.join([topic, file, symbol, str(hits[0]), role, tests]))
for i, row in enumerate(rows):
    fields = row.split('\t')
    if len(fields) == 6 and (HOST / fields[1]).is_file():
        hits = [n + 1 for n, line in enumerate((HOST / fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
        if hits:
            fields[3] = str(min(hits, key=lambda n: abs(n - int(fields[3]))))
            rows[i] = '\t'.join(fields)
path.write_text('\n'.join(rows) + '\n', encoding='utf8', newline='\n')
print('0.52说明、截图、版本与源码位置已整理。')
