# P2 开发

2026-10-19：近期新增和修改的功能全部重新验收，当前进度见[完整使用检查与返工记录](../Planning/USABILITY_REWORK_20261019.md)。首先处理窗口、尺寸、全屏与面板组合。


批准内容见 [实施计划](../Planning/P2_IMPLEMENTATION.md)。

`native` 保存本轮宿主代码；`apply.py` 只更新明确列出的文件，先检查目标内容再写入。插件界面与规则继续在各自目录维护，宿主发布时携带相同版本。现有构建目录和测试运行目录继续使用。

已交付：[0.58 内置工具](docs/BUILTIN_058_DELIVERY.md)、[0.59 频谱扒谱](docs/SPECTRUM_059_DELIVERY.md)。

0.60：[编配建议操作](docs/CONTEXT_060_GUIDE.md)、[实际检查](docs/CONTEXT_060_DELIVERY.md)。`context`保存MCP桥与共同Python服务，`apply_context.py`核对原文件后同步。

0.61：[指法与编配建议](docs/SUGGESTIONS_061_GUIDE.md)、[计算方法](docs/SUGGESTIONS_METHOD.md)。

0.62：[给定音高写节奏](docs/RHYTHM_062_GUIDE.md)、[检查结果](docs/RHYTHM_062_DELIVERY.md)。所有P2功能的操作入口、保存方式和检查结果见[交付总览](docs/P2_DELIVERY.md)。

## 工作区、DAW 与连接功能

完整方案已按六批交付到 0.69.0。操作见 [用户说明](native/personal/USER_GUIDE.md)，本次问题逐项对应见 [交付记录](docs/WORKSPACE_069_DELIVERY.md)。

VST 代码在 `native/audio/vst`，原生面板在 `native/mscore/workflow/vstpanel.cpp`；接口、扫描与效果检查在 `tests/vst`，真实音源、保存和撤销检查在宿主 `mtest/mscore/pluginhost/vst_tests.inc`。默认构建更新依赖，并生成随包的 `MuseScoreVstHost.exe`。

0.70：[分段写法的保存、切换、删除与按钮摆放](docs/VARIANTS_070_GUIDE.md)。
