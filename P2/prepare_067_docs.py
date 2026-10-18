"""Update the writing guide and source map for the fifth delivery."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
guide = root / "docs/WORKSPACE_067_GUIDE.md"
text = guide.read_text("utf8").replace(
    "从“视图 → 演奏编辑器”打开，在钢琴卷帘左上的音域按钮旁点“写音”。",
    "从“视图 → 卷帘写音”直接打开，或在演奏编辑器钢琴卷帘左上的音域按钮旁点“写音”。")
text = text.replace("## 声部、筛选与力度", "![草稿写音与比较](images/roll-writing-067.png)\n\n## 声部、筛选与力度")
guide.write_text(text, encoding="utf8", newline="\n")
shutil.copyfile(guide, root / "native/personal/docs" / guide.name)

path = root / "native/personal/USER_GUIDE.md"
text = path.read_text("utf8").replace("0.66.0", "0.67.0", 2)
text = text.replace("| 给已经写好的音高换节奏 |", "| 在卷帘画音、移动或先试草稿 | [卷帘写音完整步骤](docs/WORKSPACE_067_GUIDE.md) |\n| 给已经写好的音高换节奏 |")
text = text.replace("### 力度参考线、谱中力度与一起调整", "### 在卷帘画音与试草稿\n\n点卷帘左上方的“写音”开启，选择“直接写谱”或“草稿”。拖空白处画音，拖音符移动，拖右端改长度。Ctrl+拖动复制，Delete删除；每次手势可用一次Ctrl+Z撤销。“草稿”可比较试听，再点“使用草稿”。完整例子见[卷帘写音](docs/WORKSPACE_067_GUIDE.md)。\n\n### 力度参考线、谱中力度与一起调整", 1)
path.write_text(text, encoding="utf8", newline="\n")

path = root / "native/personal/CHANGELOG.md"
text = path.read_text("utf8").replace("# 个人版本更新日志\n", """# 个人版本更新日志

## 0.67.0 — 2026-10-18

- 卷帘新增默认关闭的写音模式，共用菜单与区域按钮，可直接写谱或先试草稿。
- 支持画音、移动、复制、删除、拖尾端、框选及常用和三连音网格；一次手势一次撤销。
- 复用原生记谱编辑，整理休止与每个音的延音；保留已有音、复制音的力度、指法和演奏设置。
- 草稿随谱保存，提供谱中／草稿效果比较与整体采用；保留原始演奏时间，可选择细微偏移。
- 采用工作线程计算修改范围和时值，只重写涉及的小节及声部；可见音符使用区间索引。
- 操作见 docs/WORKSPACE_067_GUIDE.md；检查见 docs/WORKSPACE_067_DELIVERY.md；提交定位 personal-v0.67.0。
""", 1)
path.write_text(text, encoding="utf8", newline="\n")

path = root / "refresh_sources.py"
text = path.read_text("utf8").replace("rows += [", """rows += [
 dict(topic="卷帘写音交互",path="mscore/performanceeditor/rollwritinginteraction.cpp",symbol="void RollWritingBar::begin(",line="1",role="画音、移动、复制、尾端和选择",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="卷帘写音转换",path="mscore/performanceeditor/rollnotation.cpp",symbol="QVariantMap buildRollEdit(",line="1",role="工作线程中的修改范围、声部、时值与连音组",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),
 dict(topic="卷帘草稿保存",path="mscore/performanceeditor/rollwritingmodel.cpp",symbol="void RollWritingBar::saveDraft(",line="1",role="草稿、试听、采用与撤销",tests="mtest/mscore/pluginhost/tst_pluginhost.cpp"),""", 1)
path.write_text(text, encoding="utf8", newline="\n")

for name in ("roll-writing-067.png", "roll-writing-narrow-067.png"):
    source = root.parent / "P1/out/final-regression" / name
    if source.exists():
        for folder in (root / "docs/images", root / "native/personal/docs/images"):
            shutil.copyfile(source, folder / name)
