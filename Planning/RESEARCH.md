# 研究记录与当前能力边界

核查日期：2026-10-10。源码定位基线：插件 `637a42a`（`harmony-v1.5.0`）；宿主 `4c04ca7`（个人版本 `0.22.0`）。两仓库本轮已执行快进拉取，均已是最新。下面描述的是源码/文档核查，不是新功能运行验收。

## 一、本机可复用能力

| 位置 | 已有能力 | 本轮规划必须遵守的边界 |
| --- | --- | --- |
| [ScoreObserver](../../muse3_dev/MuseScore/mscore/plugin/api/scoreobserver.h)、[说明](../../muse3_dev/MuseScore/personal/docs/10-score-observer.md) | 位置/谱面变化通知、持续音与上下文、分批分析帧、独立临时色层/记号、JSON 配置 | `analysisNotes` 会按音高合并，不是完整复调事件；现有 fingerprint 不是所有谱面属性的完整修订号。需要另读声部、拼写、延音线、指法等数据 |
| [QML 读写谱 API](../../muse3_dev/MuseScore/mscore/plugin/api/qmlpluginapi.cpp) | `readScore`、`writeScore`、`closeScore` | `readScore` 会打开谱页；`writeScore` 调用宿主 `saveAs`。路径、保存状态、撤销栈是否受影响必须先实测，不能把它冒充无副作用的内存快照 |
| [Score 克隆](../../muse3_dev/MuseScore/libmscore/score.cpp) | `MasterScore::clone()` 经序列化重建并排版 | 尚未通过 QML 提供完整方案工作区；副本、分谱、链接对象、个人演奏属性的完整性都需专门验证 |
| [乐谱比较](../../muse3_dev/MuseScore/mscore/scorecmp/scorecmp.h) | 现有比较面板/差异模型 | 是比较工具，不证明支持安全的局部合并、自动重基或分支播放 |
| [演奏参数编辑](../../muse3_dev/MuseScore/mscore/performanceeditor/parameteredit.h)、[说明](../../muse3_dev/MuseScore/personal/docs/14-performance-editor.md) | 力度、速度、速度曲线、踏板的原生编辑路径 | 不等于已开放 QML 通用批量写接口。复用 Undo、原有标记保护和安全播放边界；待提交预览与谱内已提交数据要分开 |
| [NoteEvent](../../muse3_dev/MuseScore/libmscore/noteevent.h) | 音符演奏事件 | ontime/len 使用名义时值的千分比，不是 MIDI tick；自动事件可能重新生成。视频后处理优先读取实际导出的 MIDI |
| [分手符号](../../muse3_dev/MuseScore/libmscore/symbol.h)、[实现](../../muse3_dev/MuseScore/libmscore/symbol.cpp) | RH/LH 起止符号及相关绘制 | 图形的拉伸范围不能直接当成严格的手分配区间；锚点、端点和交叉谱表的含义必须单独定义 |
| [Seq](../../muse3_dev/MuseScore/mscore/seq.cpp)、[消息](../../muse3_dev/MuseScore/mscore/seq.h)、[PortMidi](../../muse3_dev/MuseScore/audiodrivers/pm.cpp) | 现有输入及播放通道 | 有经过 Seq 队列的路径，也有直接 GUI 输入路径。PortMidi 当前读取消息后未把 `PmEvent.timestamp` 传给接收函数；Seq 输入消息也未提供独立捕获时间戳。后端时钟映射与各平台路径需要验证 |
| [主界面运输控件](../../muse3_dev/MuseScore/mscore/musescore.cpp) | 独立节拍器、已有工具栏 QAction，当前设置为四分音符 BPM | Tap 的位置可少量接线完成。不能只复制按钮而不建菜单动作；复拍子的点击单位需与四分音符 BPM 转换 |
| [旧 WaveView](../../muse3_dev/MuseScore/mscore/waveview.cpp)、[Audio](../../muse3_dev/MuseScore/libmscore/audio.h) | Vorbis 波形相关旧代码、谱内音频容器 | 不是现成的多格式频谱播放器。旧实现涉及静态 Vorbis 数据/整段缓冲；不默认把大型原曲存入谱文件 |

### 与既有 MCP 规划衔接

依据 [AI_CONTEXT_INTEGRATION.md](../../mcp-musescore/docs/AI_CONTEXT_INTEGRATION.md) 与 [AI_SCORE_CONTEXT_DESIGN.md](../../mcp-musescore/docs/AI_SCORE_CONTEXT_DESIGN.md)。这些也是规划，不能称为已实现接口。

共同约定：以当前内存谱为事实源；材料可选且覆盖可局部；区分分析解释、谱面标记、实际配音修改；以 snapshot/旧值/范围保护候选应用；外部材料通过 alignment 对应，不按同一小节编号猜对应。数据集合沿用 `scoreSnapshot / assertions / materials / alignments / taskBrief / analysisRuns / proposals`。轻量工具可独立运行；复杂服务复用同一契约，不另造一套冲突的数据仓库。

## 二、用户给出的项目与相关原始资料

| 来源 | 核查结果 | 本规划采用方式 |
| --- | --- | --- |
| [lynnzYe GitHub](https://github.com/lynnzYe) | 核查了公开项目列表，以及下列项目的 README/部分源码 | 分清“表达录入”“对齐”“模型补全”，不把它们当同一种技术 |
| [PiCoDemo](https://github.com/lynnzYe/PiCoDemo) | README 提供按键触发已有音高、部分演奏控制缺失部分的时间/力度等模式；[interpolator.py](https://github.com/lynnzYe/PiCoDemo/blob/main/pico/pneno/interpolator.py) 实现 IOI 比例、历史/模板速度预测和移动平均力度插值。仓库标示 Apache-2.0 | 很适合“音高已有，我只表达节奏/力度”。借鉴传统基线；离线回填可用后续事件，实时预测则天然不知道下一次点击，不承诺二者同等精度 |
| [MaskedExpressiveness](https://github.com/lynnzYe/MaskedExpressiveness) | 使用 masked language model 补全力度；需模型与演奏/谱对应。仓库主要许可 MIT，部分依赖另有许可 | 放入未来学习模型 provider；不纳入本次传统算法第一版 |
| [3D-DTW-Visualizer](https://github.com/lynnzYe/3D-DTW-Visualizer)、[MidiAlignVisualizer](https://github.com/lynnzYe/MidiAlignVisualizer) | 公开项目可见；前者仓库 API 标示 MIT。未在本轮运行或验证全套算法 | 借鉴对齐结果可视化方向；不声称已验证在本软件适用 |
| [Tap2Music_Web](https://github.com/lynnzYe/Tap2Music_Web) | README 涉及模型接入/推理；不证明是无需训练的传统节奏转谱 | 后续研究，避免第一阶段引入模型服务 |
| [PiCo-Web](https://github.com/lynnzYe/PiCo-Web)、[TapArranger](https://github.com/lynnzYe/TapArranger) | 前者 README 主要是前端运行说明，后者 README 为空；本轮未运行 | 不从名称推断完整功能。复用前先核查代码、许可及测试 |
| [PiCoMaestro](https://www.picomaestro.com) | 本次未能读取该站正文 | 功能、当前状态、是否对应以上仓库及许可均待核验；不能把未读取当作站点不存在 |

GitHub API 未识别许可的项目，不代表已经确认没有许可；实际代码复用时必须读取 LICENSE、NOTICE、依赖和资源许可。当前只是规划，没有复制第三方代码或下载模型。

## 三、算法与媒体参考

| 原始资料 | 支持的判断 / 使用限制 |
| --- | --- |
| [music21 VoiceLeading](https://music21.org/music21docs/moduleReference/moduleVoiceLeading.html)、[FiguredBass rules](https://music21.org/music21docs/moduleReference/moduleFiguredBassRules.html) | 可参考对位检测及边界测试。规则需区分独立声部、拼写、反向/同向运动、风格，不直接把库中某个布尔结果变成所有编配的错误 |
| [Parangonar](https://github.com/sildater/parangonar) | 提供传统 DTW/锚点对齐，也含学习匹配器；若采用，只选明确的传统路径并锁版本。Apache-2.0；并非整个包都无需学习模型 |
| [钢琴指法统计模型论文配套](https://statpianofingering.github.io/demo.html)、[Merged-output HMM 论文](https://eita-nakamura.github.io/articles/Nakamura_etal_MergedOutputHMMForPianoFingering_ISMIR2014.pdf) | 说明指法可作为序列优化问题。第一版用显式成本和 DP/beam；HMM 的学习参数另列实验路线，不包装成完全无需训练的规则算法 |
| [节奏转写研究](https://arxiv.org/abs/1701.08343)、[控制演奏难度的钢琴缩编](https://arxiv.org/abs/1808.05006) | 自由节奏转谱及配音难度优化有研究基础，但不证明在任意用户输入下能自动可靠解决；先缩小任务和明示不确定性 |
| [WaveTone 官方帮助](https://ackiesound.ifdef.jp/doc/wthelp/index.html)、[基础操作](https://ackiesound.ifdef.jp/doc/wthelp/htuse1.html)、[高级操作](https://ackiesound.ifdef.jp/doc/wthelp/htuse2.html) | 参考循环、定位、速度/音高、分析与标签等工作流。不假设 WaveTone 源码可嵌入或其二进制可再分发 |
| [WaveTone 频谱说明](https://ackiesound.ifdef.jp/doc/wthelp/graph.html) | 谐波亮线不等于多个实际弹奏音；自研频谱必须避免给用户这种误导 |
| [Qt 5 QElapsedTimer](https://doc.qt.io/archives/qt-5.15/qelapsedtimer.html) | Tap 和捕获会话使用单调时间。不能持久化原始参考时钟值当跨会话绝对时间 |
| [Qt 5 QMediaPlayer](https://doc.qt.io/archives/qt-5.15/qmediaplayer.html) | 可探索播放器原型，但格式、定位、速度改变、错误处理取决于部署/后端。该接口不保证采样精度同步或变速不变调 |

未实测项：新功能原型、真实 MIDI 设备与端口并用、录入延迟、第三方项目运行、媒体格式部署、音频同步精度。相应验证已拆入待办，不能用本次文档核查代替验收。
