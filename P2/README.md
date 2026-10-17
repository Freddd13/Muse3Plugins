# P2 开发

批准内容见 [实施计划](../Planning/P2_IMPLEMENTATION.md)。

`native` 保存本轮宿主代码；`apply.py` 只更新明确列出的文件，先检查目标内容再写入。插件界面与规则继续在各自目录维护，宿主发布时携带相同版本。现有构建目录和测试运行目录继续使用。

已交付：[0.58 内置工具](docs/BUILTIN_058_DELIVERY.md)、[0.59 频谱扒谱](docs/SPECTRUM_059_DELIVERY.md)。

0.60：[编配建议操作](docs/CONTEXT_060_GUIDE.md)、[实际检查](docs/CONTEXT_060_DELIVERY.md)。`context`保存MCP桥与共同Python服务，`apply_context.py`核对原文件后同步。
