# 钢琴编曲工具与后续构想

更新：2026-10-17。当前个人版本为 **0.57.0 · Kumo branch / Freddd13**。

日常使用从[用户说明](../../muse3_dev/MuseScore/personal/USER_GUIDE.md)开始。本轮九项调整的操作、截图和检查结果见[逐项说明](../Repairs/docs/REPAIR_053_057_DELIVERY.md)。

## 当前可用的工具

| 工具 | 打开位置与主要用途 |
|---|---|
| 演奏编辑器 | 视图菜单；编辑力度、速度、踏板，与谱面选音同步 |
| 敲击测速 | 节拍器旁图标；测量速度，并可用于速度记号 |
| 和弦助手 | 插件菜单 Harmony Assistant；分析、谱面显示、人工范围与位置调整 |
| 编配检查 | 插件菜单 Arrangement Check；检查和声、对位及可弹性，保留范围并筛选结果 |
| 原曲参考 | 视图菜单或原插件入口；多轨、片段关联、一起播放，项目随谱保存 |
| 演奏表达 | 插件菜单 Performance Expression；导入或录制 MIDI、对应、试听及分范围采用力度和速度 |
| 分段试写 | 插件菜单 Arrangement Variants；切换写法、组合、叠加差异与同处试听 |
| MIDI 人性化导出 | MIDI 导出选项；预览按键长度，结合踏板安排松手 |

## 本轮修复记录

[五批实施记录](REPAIR_053_057.md)对应以下用户说明：

- [0.53：插件重载与窗口](../Repairs/docs/REPAIR_053_GUIDE.md)
- [0.54：圆滑线、速度记号与分手标记](../Repairs/docs/REPAIR_054_GUIDE.md)
- [0.55：和弦与编配检查](../Repairs/docs/REPAIR_055_GUIDE.md)
- [0.56：原曲参考](../Repairs/docs/REPAIR_056_GUIDE.md)
- [0.57：演奏力度对比与应用](../Repairs/docs/REPAIR_057_GUIDE.md)

## 后续讨论

继续讨论的内容包括：连续手位和完整指法、对位写作建议、参考音频频谱及编辑器音轨、动态乐谱视频和 AI 辅助。每项可结合实际编曲片段选择实施顺序。

早期构想和取舍保留在[详细设计](PIANO_WORKFLOW_DESIGN.md)、[P0](P0_IMPLEMENTATION.md)、[P1](P1_IMPLEMENTATION.md)和[研究记录](RESEARCH.md)中，方便回看。当前操作以用户说明和各批发布记录为准。
