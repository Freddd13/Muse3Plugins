# P1 工作流模块

批准范围及状态见 ../Planning/P1_IMPLEMENTATION.md。`native` 为新增宿主模块的可维护镜像；`apply_native.py` 仅复制本批模块及唯一锚点接线，不运行 P0 安装脚本或覆盖后续演奏编辑器。新插件独立目录，直接复用 HarmonyAssistant 的主题/紧凑控件。

依赖源由 fetch_dependencies.py 从上游取得并记录 SHA256/许可；构建和验收输出保留在忽略的 build/out，不提交二进制。
