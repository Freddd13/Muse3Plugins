# P0 钢琴编配工具

交付三批原生增量：`personal-v0.23.0` Tap BPM、`personal-v0.24.0` 保守 MIDI 裁剪与对比、`personal-v0.25.0` 完整只读快照及独立编配检查。最终修正版 0.25.1 包含三批及旧工作区 TAP 一次性迁移，软件详细说明位于宿主 `personal/docs/14-piano-workflow-p0.md`。

## 源码与合并

- `native/mscore/taptempo/`：单调时间稳健估算器和共享 QAction 工具栏入口。
- `native/audio/exports/midigate*`：值数据事件处理，无谱对象、音频回调或文件访问。
- `native/mscore/midicrop/`：原生导出设置、异步可取消对比和可见范围卷帘。
- `native/mscore/plugin/api/arrangementsnapshot.cpp`：有版本保护的完整分页读取；`readonlyanalysisjob.*` 独立可取消 JS worker。
- `../ArrangementAssistant/`：纯 ES5 规则和独立 QML 面板；直接引用同级 HarmonyAssistant 模块。
- `apply_native.py` 与 `patch_*.py`：将本任务自有文件和少量唯一锚点应用到本机宿主路径，不覆盖其他任务文件。重复执行无变化；上游锚点改变时失败，需人工核对，不能盲目套用。

生产源码也保存在软件仓库，宿主构建不依赖本目录。更新时先改这里自有模块，再同步宿主；通用音乐规则没有复制第二套。

## 构建与检查

Qt 5.15.2 / MSVC2019 x64：

```powershell
cmake -S P0/tests -B P0/tests/build -DCMAKE_PREFIX_PATH=<Qt SDK>
cmake --build P0/tests/build --config Release
P0/tests/build/Release/p0_value_tests.exe
node ArrangementAssistant/tests/test-rules.cjs
python ArrangementAssistant/tests/test_panel.py
```

宿主按既有 Windows 指南构建。MSVC 的原生测试使用对应 `mtest/mscore/p0native/tst_p0native.vcxproj`；本机旧测试 PCH 路径不匹配时，已编译宿主依赖后使用 `/p:BuildProjectReferences=false /p:ForceImportBeforeCppTargets=<本目录>/tests/NoPch.props`，不要对全构建禁用 PCH。

真实 Windows 测试用宿主 `personal/tools/test_harmony_gui.py` 隔离运行，并设置 `P0_TEST_SOUNDFONT` 为当前 `MuseScore_General.sf3`。输出保存在忽略的 `out/`，不会覆盖用户设置。原有 `scoreobserver` 与 `pluginhost` 回归需一起核对。

## MIDI 裁剪

导出 MIDI 页面首次默认关闭。只提前选定钢琴 note-off，使用正常渲染、反复展开和暂停补偿后的事件副本；其余事件不变。新旧释放点必须在同一支持的踏板区间，保护无踏板、跨抬踏板、同音重触、未知来源、手工演奏、装饰与特殊控制。连续中间踏板值和弯音不冒充普通开关踏板。

默认原长度 85%、下一同声部起音间隔 90%、最小 gate 120 ms；微随机 ±2% 可关闭，固定种子可复现。对比和最终导出共用处理器，可排除单音并同时输出 `-original.mid`。GUI 记忆不影响旧 API、QML 或命令行导出；不修改谱、dirty 或撤销栈。

当前 SF3 的代表性固定踏板片段已做原／裁剪 PCM 对比，最大差异 0。此证据不等于任意外部合成器、半踏板或所有乐曲都相同；不支持的语义保持原事件。P0 不提供内置声音 A/B。
