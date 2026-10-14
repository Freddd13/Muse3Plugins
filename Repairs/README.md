# 集中修复代码与操作记录

正式软件源码位于 `E:/programming/funcodes/muse3_dev/MuseScore`。本次修复进度见 [实施记录](../Planning/REPAIR_2026_10_IMPLEMENTATION.md)，使用方法见 [功能说明](USER_GUIDE.md)。

0.43 修复了日常编辑、菜单和速度标记；0.44 整理了和弦窗口、分手折线与演奏表达；0.45 增加 MIDI 录制。后续继续处理音乐算法、松手安排和分段方案连接。

`native/` 保存对应的独立模块与修改文件。`apply_native.py` 核对目标文件后复制这些模块，并补上必要接线；`midi-recording-host.patch` 保存 0.44 到 0.45 的输入接线。目标已有其它改动时先合并，再应用。

`prepare_*.py` 和各发布脚本保留每批开发过程。更新正式源码时使用当前文件和 Git 提交记录。`tests/run_gui_cases.py` 用独立设置运行真实 Qt 窗口，支持指定测试项。编译输出、操作图片和完整结果保存在 `out/`；每批结果也写入正式仓库的 `personal/docs/`。
