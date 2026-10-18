"""Collect verified writing results and screenshots before installation."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
path = root / "docs/WORKSPACE_067_DELIVERY.md"
text = path.read_text("utf8").replace(
    "完整检查结果随本版安装记录补齐。对应文件为 P2/out/067-final-ui.txt、067-final-existing.txt、067-final-off.txt、067-final-startup.txt。",
    "内置窗口 41 项通过，3 项使用各自的独立启动方式检查；原有工作流 53 项、演奏编辑 64 项通过。关闭扩展启动 3 项通过。实际 0.67.0 程序自动启动内置服务，随包 MCP 在移除系统 Python PATH 后读取 6 个测试音。记录：P2/out/067-final-ui.txt、067-final-existing.txt、067-final-off.txt、067-final-startup.txt。")
path.write_text(text, encoding="utf8", newline="\n")
shutil.copyfile(path, root / "native/personal/docs" / path.name)
for name in ("roll-writing-067.png", "roll-writing-narrow-067.png"):
    for folder in (root / "docs/images", root / "native/personal/docs/images"):
        shutil.copyfile(root.parent / "P1/out/final-regression" / name, folder / name)
path = root / "native/mscore/performanceeditor/rollwriting.h"
path.write_text(path.read_text("utf8").replace("    bool eventFilter(QObject *, QEvent *) override;", "  bool eventFilter(QObject *, QEvent *) override;"), encoding="utf8", newline="\n")
path = root.parent / "Planning/WORKSPACE_IMPLEMENTATION.md"
path.write_text(path.read_text("utf8").replace("实施中：记谱转换与鼠标操作", "0.67.0 已完成；[操作与检查](../P2/docs/WORKSPACE_067_DELIVERY.md)").replace("| 待实施 |", "| 准备 VST 模块、行锁定与上游更新 |"), encoding="utf8", newline="\n")
