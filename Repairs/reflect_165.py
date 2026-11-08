from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];H=R.parent/'muse3_dev/MuseScore';O=R/'P2/out/repair-165';O.mkdir(parents=True,exist_ok=True)
section='''## 先理解用途，再设计和实现（2026-11-08）

上轮主要精力花在拆分测试和反复补查，实际发布入口、用户操作和整体设计考虑不足，出现“说明写了入口，软件里却找不到”的返工。开发者应承担判断和交付责任，让思考落实到好用的功能。

- 动手前认真审题，理解用户要完成的事、已有使用习惯和期望结果。先把功能的作用、入口、操作顺序、界面安排与结果去向想清楚，给出简明的改法，再按计划实现。
- 把主要精力用于分析根因、音乐与产品判断、交互设计和实现。检查围绕实际问题与关键使用过程展开，复用已有有效结果，减少重复、机械和价值低的基础测试。
- 交付以用户在发布程序中的实际操作为依据。从用户已有工作区找到入口，完成主要操作，核对界面与结果。编译、函数返回和测试数量只提供辅助证据。
- 修复围绕已确认的问题展开，保留原来好用的操作、布局和设置。按需要补齐开关、删除、恢复和保存，让一次操作能顺畅完成。
- 直接说明判断、原因、改动和使用方法。自然表达，减少辩解、术语与防御性叙述。用户指出不好用时，先回到使用过程重新理解并调整设计。

以上作为当前执行原则，指导后文的检查记录；每次工作按实际需要取舍。

'''
record={}
for root in (R,H):
    p=root/'AGENTS.md';raw=p.read_bytes();record[str(p)]=hashlib.sha256(raw).hexdigest();text=raw.decode('utf8')
    if '## 先理解用途，再设计和实现（2026-11-08）' not in text:
        pos=text.find('\n\n')+2;text=text[:pos]+section+text[pos:];p.write_text(text,encoding='utf8',newline='\n')
(O/'agents-before.json').write_text(json.dumps(record,indent=2),encoding='utf8');(O/'agents-section.md').write_text(section,encoding='utf8')
print('Updated both AGENTS.md files; existing content retained.')
