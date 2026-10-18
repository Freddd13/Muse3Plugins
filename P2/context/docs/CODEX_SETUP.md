# Codex 安装与使用

## 使用完整程序包

0.63 起从 MuseScore 的“视图 → AI 连接”点“配置 Codex”，再点“检查连接”。打开多个窗口时选择谱名。重新连接 Codex 或新建对话后，可以直接说“读取当前谱名和选区”。

程序包包含 `bin/tools/mcp/MuseScoreMCP.exe` 和运行文件。用户直接使用 exe；开发环境的 Python 与虚拟环境留在本仓库。

Codex 使用本地 stdio 启动命令。手动配置可从程序窗口复制，示例如下，路径按安装位置调整：

```toml
[mcp_servers.musescore]
command = 'E:\programming\funcodes\muse3_dev\MuseScore\msvc.install_repair_current_x64\bin\tools\mcp\MuseScoreMCP.exe'
args = ['--stdio', '--application', 'E:\programming\funcodes\muse3_dev\MuseScore\msvc.install_repair_current_x64\bin\MuseScore3Evo.exe']
startup_timeout_sec = 20
tool_timeout_sec = 60
```

配置默认保存在 `~/.codex/config.toml`。程序修改 MuseScore 一项前会备份，保留其它设置。移动程序后再点“配置 Codex”更新路径。可用 `codex mcp list` 检查登记。

AI 连接受程序旁 `kumo.ini` 的 `features/enable_exp_feature` 控制。关闭后，MCP 仅提供开关状态查询。开启并重启程序后重新连接 Codex。

## 从源码运行与 0.62 及更早程序

下面保留开发者和旧程序的安装方法。新程序使用上面的完整程序包即可。

## 1. 安装 Python 服务、注册 MCP 与 skill

在本项目根目录运行（需要已安装 uv 和 Codex CLI）：

```powershell
pwsh -NoProfile -File .\scripts\install-codex.ps1 -WhatIf
pwsh -NoProfile -File .\scripts\install-codex.ps1
codex mcp get musescore
```

安装器使用 Python 3.13 的项目 `.venv`，自动安装 requirements，将服务注册为 `musescore`，并把 `skills/mcp-musescore` 复制到 `$HOME/.agents/skills/mcp-musescore`。已有同名 skill 先备份到项目 `.cache/skill-backups`，不删除文件。MCP 的同名配置会更新，因此已有自定义 `musescore` 配置时先保存它。用 `-SkipMcp`、`-SkipSkill` 或 `-SkipEnvironment` 跳过对应步骤；`-Scope Project` 改为项目 `.agents/skills`，MCP 仍注册到用户配置。安装 skill 本身不会自动连接 MuseScore。

也可手动注册：

```powershell
codex mcp add musescore --env 'MCP_MUSESCORE_DIR=E:\programming\funcodes\mcp-musescore' -- E:\programming\funcodes\mcp-musescore\.venv\Scripts\python.exe E:\programming\funcodes\mcp-musescore\server.py
```

或在已有 `~/.codex/config.toml` 中加入此表（不要覆盖其他配置；路径按机器调整）：

```toml
[mcp_servers.musescore]
command = 'E:\programming\funcodes\mcp-musescore\.venv\Scripts\python.exe'
args = ['E:\programming\funcodes\mcp-musescore\server.py']
startup_timeout_sec = 20
tool_timeout_sec = 60
```

跨机器使用自己的 checkout 路径；`MCP_MUSESCORE_HOST`/`MCP_MUSESCORE_PORT` 可配置 Python 连接，默认 `127.0.0.1:8765`。端口改变时也要修改 QML 的 `port`。不要将 `ws://127.0.0.1:8765` 填作 MCP 的 HTTP 地址。

## 2. 在 MuseScore 3 Evolution 中启动插件

1. 把根目录 `musescore-mcp-websocket.qml` 复制到 MuseScore **编辑 → 偏好设置 → 常规 → 文件夹 → 插件** 指定的目录。建议使用该目录的 `mcp-musescore` 子目录，保留其他插件。
2. 在插件管理器启用插件，打开乐谱，从 **插件 → MuseScore API Server** 运行。只启用而没有运行时端口不会开启。启动插件不再重置乐谱选择。
3. Windows 需要同 Qt SDK 的 `qml/QtWebSockets` 模块和 `bin/Qt5WebSockets.dll`。本机 0.10/0.11 独立安装原有 QML 模块，但 DLL 缺失；本轮只添加了该 DLL，SDK Qt5Core 与安装 Qt5Core 的 SHA256 完全一致。其他机器应从构建该 MuseScore 的同版本、同架构、同编译器 SDK 部署，不能混用 Qt 6/不同 ABI。
4. 开启新 Codex 聊天，使新的 MCP 配置生效。执行 `ping_musescore`、`get_capabilities`、`get_score_data` 验证连接。服务由 Codex 自动启动，无需另外常驻运行 Python。

插件绑定本机回环地址。一个 MuseScore 插件实例占用 8765；重新运行出现占用时先关闭原插件/对应应用实例，避免同时运行两个桥接插件。

## 3. 使用 skill

在 Codex 输入：

```text
$mcp-musescore 分析当前钢琴谱第1–8小节的和声、左右手跨度与声部进行，先给建议。
$mcp-musescore 在当前选定位置写入四分音符C4，并读取乐谱核验。
$mcp-musescore 检查第9–16小节的休止、延音和声部，列出净书建议。
```

skill 支持自然语言自动匹配。`get_score_data` 提供原始 JSON，`get_score` 保留 LilyPond 阅读视图。小节从 1 开始，谱表/声部从 0 开始；自定义选区的末谱表包含在范围内，末 tick 不包含。写入失败且 `outcomeUnknown=true` 时先读谱，不能直接重复加音。批处理失败会返回完成数和失败下标；已完成动作仍保留，不是整体事务。

当前支持音符/和弦、休止、连音、歌词、小节、导航、选区、拍号、速度与撤销。谱面查看器保留，但不能保证所有 Codex 宿主显示 MCP App；VexFlow 不画延音线/连音括号，不能作为最终净书验收。旧 `set_staff_mute` 尝试修改可见性，但 MS3 不提供该属性，会明确报不支持；`set_instrument_sound` 打开人工对话框。力度/踏板曲线、SF2 选择和真正音频调音尚无 MCP 写入工具。

## 4. 验证与故障定位

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
$env:MCP_MUSESCORE_DIR = (Get-Location).Path
& .\skills\mcp-musescore\scripts\check-mcp-musescore.ps1
```

检查脚本先编译/导入服务，再进行真实 WebSocket ping。没有运行插件时应报错；mock 测试通过不等于连接了真实软件。原生宿主测试可运行 `scripts/test-native-bridge.py --exe <MuseScore3Evo.exe> --score <测试谱.mscx>`；它使用隔离设置、offscreen 和静音模式，不改当前打开的谱，也不保存输入测试谱。

安装在项目外的 skill 脚本请设置 `MCP_MUSESCORE_DIR`；Windows 默认系统 Python 3.7 不适用，必须使用项目 `.venv`。

依据：[Codex MCP 官方文档](https://developers.openai.com/codex/mcp)、[Codex skills 官方文档](https://developers.openai.com/codex/skills)。
