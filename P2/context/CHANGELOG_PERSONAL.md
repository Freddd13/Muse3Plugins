# 个人开发更新日志

## 2.3.0 — 2026-10-18

- 新增随软件提供的独立 MCP 程序，内置 Python 与通信依赖。
- 自动寻找正在运行的程序，支持多窗口选择及连接恢复。
- 配置 Codex 前备份原文件，保留其它服务与个人设置。
- 接入程序旁 kumo.ini，关闭扩展时提供配置状态查询。
- 配置方法、诊断命令及源码运行说明见 docs/CODEX_SETUP.md；提交定位 mcp-runtime-v2.3.0。

## 2.2.0 — 2026-10-18

- 接入软件0.60.0的原生分批查询，读取当前内存谱、精确选区、同音多声部、分数时值、延音和演奏资料。
- 共同Python服务保留各任务的范围和要求；提供取消、资料追加、局部候选、操作结果查询及MCP入口。
- 原生面板比较和试听写法，采用和保存分段方案各为一次撤销。普通读谱查询保留当前编配任务。
- 桥解除关闭回调，并调用宿主的关闭清理；消息日志记录动作和长度。
- 操作、数据和检查入口见[说明](docs/P2_CONTEXT_API.md)。
- 提交定位：mcp-context-v2.2.0。

## 可选上下文与实时/外部集成设计 — 2026-10-10

- 两仓库先 pull，均已同步；本轮 MCP 基线 `2b2d422`，软件 `4c04ca711` / personal 0.22.0。只读核查观察器指南及和声助手 1.5 的边界，读取净书知识入口与个人偏好，保留软件已有本地文档修改。
- 新增 [上下文集成契约](docs/AI_CONTEXT_INTEGRATION.md)，修订主设计与 README：当前内存谱为写作主来源，无需保存/导出 MusicXML；材料、解释、来源对应均可选且可局部增补，可用性/覆盖/计算/过期/采用状态分开。
- 定义材料与计算 provider 适配、格式投影与损失、部分资料/冲突/人工纠正、任务状态和降级，以及解释/标记/实际配音的不同副作用；自然语言明确授权的范围可以直接实施，不设置逐音重复确认。
- 同步软件 `personal/USER_GUIDE.md` 的规划说明。本轮未改原生源码、MCP/QML/skill、乐谱或运行安装，无新增可调用接口；无需重装/重配。
- 检查两份文档 JSON 示例、相对链接/代码块与 git whitespace，对照本地源码和 MCP 官方规范。未进行新架构运行验收。提交定位：`docs: refine optional live context and integration contracts`。

## 乐谱数据与 AI 上下文规划 — 2026-10-09

- 两仓库先 `git pull --ff-only`，均已同步；MCP 基线 `7584651`，软件 `059ddd720` / personal 0.18.0。保留字体任务已有暂存文件，以及软件仓库已有指南/AGENTS 修改。
- 新增 [数据与上下文设计](docs/AI_SCORE_CONTEXT_DESIGN.md)：本地完整模型、多音乐视图、按任务分层包、精确时间/音高/关系、踏板/原生演奏/几何边界、原曲与录音对应、目标与偏好、版本与闭包、提案/副本预览/写回契约、P0–P3 路线及验收集。
- 核查发现：ScoreObserver analysisNotes 按 MIDI 音高去重，适合和声候选、不适合完整声部；其 fingerprint 不是全谱内容版本。个人琶音/倚音/重音/rit./a tempo 属性未在 QML Element 包装完整暴露；新方案优先插件与 Python，仅为已验证缺口增最小原生读取接口。
- 维护 README 入口与软件 `personal/USER_GUIDE.md` 的规划说明。未修改 MCP/QML/skill 或 MuseScore 原生源码，未增加可调用工具、未改个人版本/安装；本次无需重装 MCP/skill/插件。
- 验证范围：文档结构、JSON 示例与链接检查、Git whitespace 检查、对照本地源码与 MusicXML/MEI/MCP 官方规范；设计未做运行功能验收。提交定位使用 `docs: design score data and AI task context` 查询。

## MCP 桥 2.1.0 — 2026-10-08

- 基线：cab6a74；开发分支 codex/musescore-evolution。软件基线 origin/3.x 的 02346d2dd，本机 personal 0.11.0 工作未提交。本轮两边 pull 后开发，保留软件现有改动。提交定位：`feat(codex): adapt MuseScore Evolution bridge and skill`，通过 `git log --all --grep='adapt MuseScore Evolution bridge'` 查询。
- 方案：只改本项目 Python/QML/skill，未修改 MuseScore 原生源码。使用 QtWebSockets 替代软件未提供的 api.websocketserver；插件绑定 127.0.0.1:8765。向本机 0.10/0.11 的独立安装添加缺失 Qt5WebSockets.dll，先核对 SDK 与安装 Qt5Core 哈希一致，不替换已有 DLL。
- 接口：保留原 27 工具，增加 get_capabilities、get_score_data、set_tempo，共 30。保留 get_score 的 LilyPond 阅读输出，修复读谱/导航解包。增加逐音 tieForward/tieBack、tuning、veloType/veloOffset、书面时值和 ticksPerQuarter。读谱改为独立游标，不触碰乐谱选择和撤销。
- 兼容修复：TempoText 先加入谱段再设置 tempo，避免个人分支 setter 对空 segment 解引用；自定义单谱表选区按原生末谱表排除规则转换；原生 undo 不在新事务中调用。setTempo 加入 Python 批处理类型并验证原生 5–999 BPM 范围。
- 可靠性：并发请求串行配对；连接/接收超时；只读允许恢复重试，写入响应丢失不自动重放并返回 outcomeUnknown。批处理失败返回失败下标及完成数，前面成功的动作仍保留。修正 set_staff_mute 和 set_instrument_sound 的真实能力说明，未删除工具/文件。
- Codex：服务器初始化说明、Codex skill 更新、一键安装器、用户级/项目级 skill 复制、已有 skill 备份、WhatIf、Windows/Git Bash helper、探测失败退出码。保留上游 README 与 Claude 配置作为历史兼容资料，中文入口与当前能力说明置于前。
- 文档：[用户安装与操作](docs/CODEX_SETUP.md)、[实现原理与钢琴扩展方案](docs/ARCHITECTURE_AND_PIANO.md)、[shell 实测](docs/SHELL_BENCHMARK.md)，并同步软件 personal/USER_GUIDE.md 的 MCP 使用说明。
- 验证：Python 3.13 / FastMCP 4.0.11 / websockets 17.2；17 项测试通过，包含 in-memory MCP、真实 WebSocket mock、独立 Python 子进程 stdio、并发响应配对、写响应丢失不重放及超时。实际 0.10/0.11 offscreen 宿主验证 Qt 模块加载、能力读取、读谱保持选择、单谱表范围、批处理失败、撤销及速度写入；0.11 另核验实际速度图值和音符插入。skill validator、安装器 WhatIf 和实际仅环境安装通过。
- 范围：未完成用户桌面中真实乐谱的长期交互、声卡/SF2 听感或 Codex MCP App 渲染验收；原生宿主测试静音，真实网络收发用 mock 和 stdio 验证。get_score_data 的小节筛选在 Python 侧，QML 仍读全谱；密集大谱需后续分段 API。和声临时提示、演奏属性批量写入与净书定向工具是下一轮路线，尚未实现。
- 用户执行偏好：七次短任务实测 Bash 509 ms、旧 PowerShell 707 ms、pwsh 807 ms（中位）；优先 Git Bash 做 Git/文本工作，Windows 原生任务用 pwsh -NoProfile。完整任务仍需计入执行器外层开销。
- 结束复核：并发软件任务已提交 0.11.0（36c3fa12a），当前 VERSION 正在准备 0.12.0。Plugin API 与 TempoText setter 没有新的未提交修改，无需再改本轮桥接接口；0.12 新安装与长期使用尚待实际核验。软件工作保持独立，本次未混入其源码提交。
