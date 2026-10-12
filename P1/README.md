# P1 工作流模块

批准范围及状态见 ../Planning/P1_IMPLEMENTATION.md。`native` 为新增宿主模块的可维护镜像；`apply_native.py` 仅复制本批模块及唯一锚点接线，不运行 P0 安装脚本或覆盖后续演奏编辑器。新插件独立目录，直接复用 HarmonyAssistant 的主题/紧凑控件。

依赖源由 fetch_dependencies.py 从上游取得并记录 SHA256/许可；构建和验收输出保留在忽略的 build/out，不提交二进制。

批次A/B1/B2/C/D分别发布0.27–0.31；部署于本机msvc.install_p1_x64。新增插件ReferencePlayer、PerformanceExpression、ArrangementVariants及WorkflowCommon独立安装。重建P1请先apply_native.py，再patch_expression.py与patch_midicrop.py，避免重跑P0覆盖后续变化。MIDI裁剪扩展镜像在P1/native/audio/exports与mscore/midicrop；默认导出保持关闭。

完整交付、验证与实际限制见DELIVERY.md。tests/run_native_regressions.py --build只重编当前宿主测试，随后无参数运行复用隔离运行时；同一构建目录不并行构建。

新增中文标签用patch_translation.py追加，保留原翻译；再用Qt lrelease编译mscore_zh_CN.ts并安装。--case p1native可单独重跑新增宿主测试，保留其它已通过套件的结果。
