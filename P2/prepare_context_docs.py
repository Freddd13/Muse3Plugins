"""Maintain the P2 user chapter and implementation records together."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / "muse3_dev/MuseScore"
MCP = ROOT.parent.parent / "mcp-musescore"


def native(relative):
    target = ROOT / "native" / relative
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        if (HOST / relative).exists():
            shutil.copyfile(HOST / relative, target)
    return target


def mcp(relative):
    target = ROOT / "context" / relative
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MCP / relative, target)
    return target


native("personal/VERSION").write_text("0.60.0\n", encoding="utf8", newline="\n")
guide = ROOT / "docs/CONTEXT_060_GUIDE.md"
native("personal/docs/P2_CONTEXT_060_GUIDE.md").write_text(guide.read_text("utf8"), encoding="utf8", newline="\n")
p = native("personal/USER_GUIDE.md")
text = p.read_text("utf8").replace("当前个人版本：**0.59.0**", "当前个人版本：**0.60.0**")
chapter = """## 0.60 的编配建议

选中谱段，在 Codex 中说明编配要求，软件会将收到的写法放进“视图 → 编配建议”。可以查看原谱差异、在同一处试听、采用或保存另一种写法。解释与采用记录随 MSCZ 保存。完整例子见[编配建议使用说明](docs/P2_CONTEXT_060_GUIDE.md)。

"""
if "## 0.60 的编配建议" not in text:
    text = text.replace("## 0.59 的频谱扒谱", chapter + "## 0.59 的频谱扒谱", 1)
text = text.replace("当前个人版本：**0.60.0** · Kumo branch / Freddd13。", "当前个人版本：**0.60.0** · Kumo branch / Freddd13。提交定位：`personal-v0.60.0`。")
p.write_text(text, encoding="utf8", newline="\n")
p = native("personal/CHANGELOG.md")
text = p.read_text("utf8")
entry = """## 0.60.0 — 2026-10-18

- 当前内存谱增加精确选区、分批查询、完整声部、分数时值、演奏数值、反复及跨段连线资料；共用和弦分析。
- 增加原生编配建议面板：差异、原／新写法试听、采用和存为分段写法；采用及保存写法各为一次撤销。
- 局部写入先在副本检查，支持逐音设置、整声部音符／休止／连音组，并核对写回与链接分谱。
- 编曲解释、材料对应和采用记录随MSCZ保存；MCP增加独立任务范围、取消、版本检查和操作结果查询。
- Windows补齐QtWebSockets部署；桥关闭解除回调，应用关闭阶段释放SSL／DTLS默认配置。
- 使用说明：personal/docs/P2_CONTEXT_060_GUIDE.md；操作检查和实际结果见插件仓库P2交付记录。
- 提交定位：personal-v0.60.0。

"""
if "## 0.60.0" not in text:
    text = text.replace("## 0.59.0", entry + "## 0.59.0", 1)
p.write_text(text, encoding="utf8", newline="\n")
p = mcp("README.md")
text = p.read_text("utf8").replace("该文档是规划，新接口尚未实现。", "当前选段读取和局部写法已在桥2.2.0／软件0.60.0接入，详见[P2操作与接口](docs/P2_CONTEXT_API.md)。材料解析等后续内容继续按文档推进。")
p.write_text(text, encoding="utf8", newline="\n")
p = mcp("CHANGELOG_PERSONAL.md")
text = p.read_text("utf8")
entry = """## 2.2.0 — 2026-10-18

- 接入软件0.60.0的原生分批查询，读取当前内存谱、精确选区、同音多声部、分数时值、延音和演奏资料。
- 共同Python服务保留各任务的范围和要求；提供取消、资料追加、局部候选、操作结果查询及MCP入口。
- 原生面板比较和试听写法，采用和保存分段方案各为一次撤销。普通读谱查询保留当前编配任务。
- 桥解除关闭回调，并调用宿主的关闭清理；消息日志记录动作和长度。
- 操作、数据和检查入口见[说明](docs/P2_CONTEXT_API.md)。
- 提交定位：mcp-context-v2.2.0。

"""
if "## 2.2.0" not in text:
    at = text.find("\n## ")
    text = text[:at+1] + entry + text[at+1:] if at >= 0 else entry + text
p.write_text(text, encoding="utf8", newline="\n")
p = mcp("docs/AI_CONTEXT_INTEGRATION.md")
text = p.read_text("utf8").replace("状态：**设计修订，本文的新模型、接口和 UI 尚未实现。**", "状态：**0.60.0／桥2.2.0已接入当前谱读取、局部候选和原生建议面板。** 当前用法与字段见[P2接口](P2_CONTEXT_API.md)；本文继续记录后续材料与模型适配的设计。", 1)
p.write_text(text, encoding="utf8", newline="\n")
p = mcp("docs/ARCHITECTURE_AND_PIANO.md")
text = p.read_text("utf8")
if "## P2 当前谱与编配建议" not in text:
    text += "\n## P2 当前谱与编配建议\n\n`src/context/service.py`管理独立任务和资料，`src/tools/arrangement.py`提供MCP入口；QML桥转发到原生ScoreObserver的分批查询与候选处理。参数和完整操作见[P2接口说明](P2_CONTEXT_API.md)。\n"
p.write_text(text, encoding="utf8", newline="\n")
print("已整理0.60说明、版本和MCP结构记录")
