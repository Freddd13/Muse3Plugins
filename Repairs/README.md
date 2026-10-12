# 本轮修复代码与验证

这些文件对应用户批准的六批修复。最新进度见 `Planning/REPAIR_IMPLEMENTATION.md`。软件本体仍以 `E:/programming/funcodes/muse3_dev/MuseScore` 为正式仓库。

`native/` 保存本轮新增或修改的原生文件。`apply_native.py` 只复制这里列出的文件、项目插件，并修改必需的少量接线。复制前核对目标文件；发现另一个任务的修改就停止，先合并，避免覆盖。

`prepare_*.py`、`editor_wiring.py`、`editor_finish.py`、`finish_copy_context.py` 和各发布脚本都是相应批次开发时的准备记录；不要拿它们重新生成当前模块。已有 `P0`、`P1` 安装脚本也不要覆盖较新的源码。今后以正式仓库和这里的最新文件为准。

验证使用 `P1/tests/run_native_regressions.py`，测试的配置、素材和程序副本放在临时目录。`tests/run_gui_cases.py` 可在已有程序及 Qt 资源中运行指定的鼠标操作测试。报告、构建输出和过程图片放在 `out/`，不作为功能已经完成的证明；只有检查通过并记录实际结果后才发布。

当前已发布 0.32.0–0.37.0；演奏编辑器、和弦显示、Tap速度标记联动和输入净谱及相关验证已完成。音乐记谱、和弦算法、多音频联动和分段方案仍按后续批次继续。
