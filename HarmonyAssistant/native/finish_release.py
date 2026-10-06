from pathlib import Path
import shutil, subprocess

base = Path(__file__).resolve().parents[1]
repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def write(file, text):
    with file.open('w',encoding='utf-8',newline='\n') as stream: stream.write(text)

readme = (base/'README.md').read_text(encoding='utf-8')
readme = readme.replace('最终实测数字和结果见主程序个人更新日志。',
    '本机 Release 实测：新原生测试 8 项、原有音符测试 11 项全部通过；1000 小节/6000 音符首次索引 10.13 ms，1000 次缓存查询总计 1.54 ms。真实 QML 宿主 1000 次跨接口查询约 9–18 ms（不同运行负载）；这些数字是当前机器/测试谱的测量，不是所有工程的上限。详细结果见主程序个人更新日志。')
write(base/'README.md',readme)
for target in [repo/'share/plugins/HarmonyAssistant/README.md',repo/'msvc.install_harmony_release_x64/plugins/HarmonyAssistant/README.md']:
    shutil.copy2(base/'README.md',target)
shutil.copy2(base/'test-harmony.cjs',repo/'mtest/mscore/scoreobserver/test-harmony.cjs')
smoke = (base/'tests/native-smoke.qml').read_text(encoding='utf-8').replace('../HarmonyAssistant_MS3.qml','../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml')
write(repo/'mtest/mscore/scoreobserver/smoke.qml',smoke)
runner = (base/'tests/run_native_smoke.py').read_text(encoding='utf-8')
runner = runner.replace("HERE = Path(__file__).resolve().parent", "HERE = Path(__file__).resolve().parents[2]\nPLUGIN = HERE / 'share/plugins/HarmonyAssistant'\nFIXTURE = HERE / 'mtest/mscore/scoreobserver'")
runner = runner.replace("HERE / 'native-smoke.qml'", "FIXTURE / 'smoke.qml'")
runner = runner.replace("'../HarmonyAssistant_MS3.qml', (HERE.parent / 'HarmonyAssistant_MS3.qml').as_uri()", "'../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml', (PLUGIN / 'HarmonyAssistant_MS3.qml').as_uri()")
runner = runner.replace("HERE.parent / 'native' / 'piano.mscx'", "FIXTURE / 'piano.mscx'")
write(repo/'personal/tools/test_harmony_host.py',runner)

guideFile = repo/'personal/docs/10-score-observer.md'
guide = guideFile.read_text(encoding='utf-8')
guide += '''
### 本机已通过的运行与缓存绕行

2026-10-05：新原生 suite 8/8、既有音符 suite 11/11、逻辑 JS 和真实 Release 插件加载全部通过。长谱首次索引 10.13 ms，1000 次缓存查询 1.54 ms。

这台电脑 MSVC/CMake 的共享 PCH 在重建后仍被清理，测试最终用进程变量 `$env:_CL_='/Y-'` 编译（不修改应用源码或系统环境）；依赖库先完成后，对各测试 `.vcxproj` 使用 `/p:BuildProjectReferences=false`。既有测试还必须在进程 PATH 中包含 Git 的 `usr/bin`，以提供 GNU diff，不能用 PowerShell 的 diff 别名代替。缺少 diff 时首次五项比对失败，补齐后 11 项通过，未更改参考谱。

可独立复现 JS 与真实宿主回归：

```powershell
node mtest/mscore/scoreobserver/test-harmony.cjs share/plugins/HarmonyAssistant/Harmony.js
python personal/tools/test_harmony_host.py msvc.install_harmony_release_x64/bin/MuseScore3Evo.exe msvc.build_harmony_release_x64/harmony-smoke-final
```

测试输出在忽略的构建目录。实际音频/MIDI 硬件和长时间交互未验收；离屏验证不代表 DAW 硬实时承诺。
'''
write(guideFile,guide)
write(repo/'personal/VERSION','0.2.0\n')
parent = subprocess.check_output(['git','rev-parse','HEAD'],cwd=str(repo)).decode().strip()
logfile = repo/'personal/CHANGELOG.md'
log = logfile.read_text(encoding='utf-8')
entry = '''## 0.2.0 — 2026-10-05

- 类型：钢琴和声插件 1.0.0 + 通用原生观察/预览接口；应用上游基线仍为 3.7.0，不修改应用版本或谱面文件格式。
- 结果：当前和弦/级数、1/3/5/7/9/11/13 功能音、持续音/左右手、真实播放事件跟随和屏幕临时配色；响应式窄面板、手动识别/调性/键盘/恢复/刷新功能保留。颜色不写 Note 属性，不触发 undo，不进入保存/导出。
- 解耦评估：纯插件无法获得精确播放通知或独立临时色层；选择插件音乐/UI + 泛用原生接口。没有修改 Seq/Driver/音频回调，不以定时器模拟播放进度，不引入外部依赖或文件格式字段。
- 新模块：`mscore/plugin/api/scoreobserver.h/.cpp` 提供 GUI 侧 Seq/Score 事件、数值快照与按内容状态/范围失效的声部索引；`mscore/notepreview.h` 提供按 owner 隔离的视图图层。
- 最小接线：`qmlpluginapi.h/.cpp` 工厂、`plugin.cmake` 编译清单；`ScoreView.h/.cpp` 屏幕绘制/局部刷新/换谱与删除清理；`libmscore/note.h/.cpp` draw 颜色重载。默认选中颜色、播放标记、不可见音符和音域提示保留。
- 发布：`share/plugins/HarmonyAssistant/` 含四个运行文件及 README，现有 share 递归安装规则直接打包；日常编辑源仍是独立 `muse3_plugins/HarmonyAssistant/` 工作区，没有删除原稿或其他插件。
- 测试：新增 `mtest/mscore/scoreobserver/` 的小谱、Qt suite、JS 和真实 CLI smoke；`personal/tools/test_harmony_host.py` 用独立配置和超时。`mtest/CMakeLists.txt` 注册新 suite，并补齐 testutils 的 FreeType 头依赖；`tst_note.cpp` 原有 Windows Chord 名称保护扩展到 MSVC，应用行为不变。
- 构建：完整 x64 Debug 构建/链接/安装通过；Release 优化构建/链接/安装通过。最终可执行程序 `msvc.install_harmony_release_x64/bin/MuseScore3Evo.exe`，完整插件已安装到同级 `plugins/HarmonyAssistant`。
- 功能验证：新 Release 实际加载插件，Cmaj13 持续音 6 个，原始音符颜色不变，空拍清空，缓存不重建；JS 回归和 Qt5 模拟选区/播放/隐藏/撤销/280/360/460px 排版通过。原生 `tst_scoreobserver` 8 通过，`tst_note` 11 通过，无跳过/失败；保存前后 MSCX 字节一致，预览与默认绘图隔离，撤销失效与颜色层移除验证通过。
- 性能：1000 小节/6000 音符索引 10.130 ms；1000 次原生缓存查询总计 1.538 ms，小谱基准约 0.001 ms/次；真实 QML 跨接口 1000 次约 9–18 ms（运行负载不同）。GUI 心跳沿原程序约 20 ms，插件最多合并等待 16 ms；相同音集合跳过和弦识别/色层重绘，隐藏停止计时。不是硬实时上限或 DAW 全设备性能保证。
- 恢复与环境：编译期间用户电脑蓝屏，源码/Release 产物保存完好，恢复后实际加载与回归复验。没有证据认定蓝屏原因。共享 PCH 缓存失效/被清理，最终测试进程临时 `/Y-` 并使用已编译依赖；既有 suite 最初缺 GNU diff 的 5 项失败，在 PATH 补 Git usr/bin 后 11 项全部通过，不更改参考谱。Debug 测试运行时不匹配，验证以完整 Release Qt 配置为准。
- 未验收项：实际音频/MIDI 硬件、长时间编辑/播放、所有特殊谱法及停靠视图的完整人工交互；踏板下 Note-off 后声学残响不纳入和弦。播放读取 GUI 侧活动 NoteEvent，支持发声音高偏移及分谱投射；不能仅凭 pitch 集合保证唯一根音。
- 记录：本机测试日志 `msvc.build_harmony_release_x64/harmony-regression/observer.txt`、`note-with-diff.txt`，真实宿主报告 `harmony-smoke-final/native-smoke.json`；构建日志在 `msvc.build_probe_x64/harmony-*.log`，产物与日志均忽略。
- 指南：同步架构、功能表、钢琴专题、构建验证、入口、受影响源码索引；新增 `personal/docs/10-score-observer.md`。初始 baseline 不改写。
- Git 父提交：`PARENT`。
- Git 提交主题：`feat(plugins): add score observation and screen-only harmony preview`。
- 提交定位：`personal-v0.2.0` 标签指向本条提交，用 `git rev-parse personal-v0.2.0` 核对 SHA。
- 合并影响：核心接线为少量局部行，其余为新增 helper、测试、独立插件和 personal 文档；普通绘制/模型/序列化路径保留。推送前已核对个人 origin 3.x 为父提交，没有额外合并上游。

'''.replace('PARENT',parent)
log = log.replace('## 0.1.1 — 2026-10-05',entry+'## 0.1.1 — 2026-10-05',1)
write(logfile,log)
print('Personal version 0.2.0, changelog and reproducible tests recorded')
