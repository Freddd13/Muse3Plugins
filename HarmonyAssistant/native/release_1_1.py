"""One-time verified local release, with backups; not a general installer."""
from pathlib import Path
import csv
import hashlib
import shutil
import subprocess
import zipfile

plugin = Path(__file__).resolve().parents[1]
repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
install = repo / 'msvc.install_harmony_1_1_x64'
user = Path(r'C:\Users\Fred\Documents\MuseScore3\插件\HarmonyAssistant')
git = r'E:\Git\cmd\git.exe'
names = ['HarmonyAssistant_MS3.qml', 'Harmony.js', 'Preferences.js', 'Analysis.js',
         'ConfigurationEditor.qml', 'SettingsStore.qml', 'PanelCard.qml', 'UiLabel.qml', 'README.md']

def write(path, value):
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(value)

# Require the enabled user copy to be the previous committed release, not user edits.
for name in names:
    target = user / name
    if not target.exists():
        continue
    previous = subprocess.check_output([git, '-C', str(repo), 'show', 'HEAD:share/plugins/HarmonyAssistant/' + name])
    assert target.read_bytes().replace(b'\r\n', b'\n') == previous.replace(b'\r\n', b'\n'), name
    backup = user / (name + '.pre-1.1.0.bak')
    if backup.exists():
        assert backup.read_bytes() == target.read_bytes(), backup
    else:
        shutil.copy2(str(target), str(backup))

for directory in [repo / 'share/plugins/HarmonyAssistant', install / 'plugins/HarmonyAssistant', user]:
    directory.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(str(plugin / name), str(directory / name))
        assert hashlib.sha256((directory / name).read_bytes()).digest() == hashlib.sha256((plugin / name).read_bytes()).digest()

# Native repository owns reproducible host regressions; editing sources remain here.
shutil.copy2(str(plugin / 'tests/run_native_gui.py'), str(repo / 'personal/tools/test_harmony_gui.py'))
source = (plugin / 'tests/native-smoke.qml').read_text(encoding='utf-8')
write(repo / 'mtest/mscore/scoreobserver/smoke.qml', source.replace('../HarmonyAssistant_MS3.qml', '../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml'))
p = repo / 'personal/tools/test_harmony_host.py'
s = p.read_text(encoding='utf-8').replace('WORK.mkdir(parents=True, exist_ok=True)', 'WORK.mkdir(parents=True, exist_ok=True)\n(WORK / "settings").mkdir(parents=True, exist_ok=True)')
s = s.replace("source = source.replace('../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml', (PLUGIN / 'HarmonyAssistant_MS3.qml').as_uri())", "panel = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else PLUGIN / 'HarmonyAssistant_MS3.qml'\nsource = source.replace('../../../share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml', panel.as_uri())")
s = s.replace("sys.exit(bool(report['failures']))", "sys.exit(bool(report['failures']) or status != 0)")
write(p, s)

entry = '''## 0.3.0 — 2026-10-05

- 类型：修复插件菜单崩溃，发布和声助手 1.1.0；上游应用基线仍为 3.7.0，不修改谱面格式或应用版本字段。
- 崩溃根因：Windows BEX64 / 0xc0000409 转储通过函数映射定位到 QML 缩略谱 doLayout → Element 析构 → ScoreView::onElementDestruction；旧代码调用 e->isNote() 时派生虚函数已经析构。mscore/scoreview.cpp 与 notepreview.h 改为只比较不透明 Element 地址；测试实际创建 native 和 QML 两种视图并触发重排。
- 最小通用宿主接线：mscore/plugin/qmlplugin.h/.cpp 的 QPointer 停靠状态、悬浮控制和可选横条高度；mscorePlugins.cpp 连接已有 QDockWidget；pluginManager.cpp 去除 QDirIterator 已递归后再次递归的重复扫描。其他插件没有声明高度提示时保持原行为。
- 新增通用能力：scoreobserver.h/.cpp 的 contextSnapshot、analysisFrames、setScorePreview/clearAllPreviews、本地原子文本/配置读写。缓存延音线持续终点、所属乐器踏板窗口、数字小节/事件索引和范围内容指纹。即时音与分析上下文分开；无踏板窗口限小节并按声部休止截断。读文件最多 16 MiB，配置跟随 dataPath / -c / 便携设置。
- 屏幕标注：notepreview.h 的可选 label/chord/active 与几何，scoreview.cpp 独立绘制；全谱底层和播放当前层分离，当前高亮复用底层位置。避开现有记谱元素与同批文字，拥挤时省略。打印/foto、Note 原色、音乐模型、undo 和保存字段不改变；未修改 Seq、Driver 或音频回调。
- 插件：share/plugins/HarmonyAssistant 的八个运行文件与 README；Preferences.js、Analysis.js、ConfigurationEditor.qml、SettingsStore.qml 新增。响应式顶栏/侧栏/双列/悬浮、独立详情窗口、Carbon/柔和/单色与自定义标签颜色、自动配置保存加载、全小节配色、JSON 分析交换/CSV 导出、谱面和弦与功能标签独立开关。原选区/调性/手动和弦/键盘/旧宿主恢复功能保留。
- 解耦评估：音乐判断、交换格式和 UI 均留插件；纯插件不能提供无 undo 的屏幕层、真实播放活动音或实际 Qt 停靠状态，故增加泛用数值/视图接口。没有引入运行库、改序列化或改音频调度；合并点限定现有宿主/视图少量局部行。
- 构建：x64 Release 编译、链接、独立安装通过；程序 msvc.install_harmony_1_1_x64/bin/MuseScore3Evo.exe。原安装目录与插件备份保留；用户已启用的个人插件副本经与父提交逐文件比较后备份、同步，防止同名旧入口优先加载。
- 验证：tst_scoreobserver 11、tst_note 11、tst_pluginhost 3 项全部通过，0 失败/跳过；JS 和 Qt5 面板测试通过。真实 GUI suite 覆盖缩略谱重排、四次菜单弹出、加载插件、顶部横条、浮动宽面板、右侧停靠、关闭重开及实际屏幕绘制差异；检查原生 QML 窗口截图。native smoke 使用安装程序、独立设置和测试谱验证 Cmaj13、6 持续音、上下文/分析帧、配置读写、原色不变、空拍清空和缓存复用；原生 suite 还验证 MSCX 保存字节不变。
- 性能：1000 小节/6000 音符索引 24.335 ms；1000 次缓存 snapshot 2.069 ms、contextSnapshot 5.371 ms；6000 音符数值帧 20.204 ms、全谱色层定位 23.227 ms。QML 跨接口 1000 次 snapshot 约 10 ms、context 约 19 ms。插件分批检测另有成本，标注拥挤程度会影响避让时间；这些是本机样本测量，不是零开销或硬实时承诺。播放沿 GUI 心跳，隐藏停止任务。
- 回归资源：mtest/mscore/scoreobserver/arpeggio.mscx 和扩展 suite；mtest/mscore/pluginhost 新 GUI suite 注册到 mtest/CMakeLists。personal/tools/test_harmony_gui.py 为 Windows Qt 测试准备独立相对路径运行时并限时，直接 QTEST_MAIN 不执行 main() 的工作区/硬件初始化；插件销毁已测试，主窗口工作区保存不属于该 fixture。修正 test_harmony_host.py 先创建 -c 目录，避免目录不存在时程序回退到默认设置。
- 测试环境：GUI fixture 的 Qt 样式加载也读取 QLibraryInfo，必须使用一致的相对 QML/plugin 路径与完整资源；早期缺资源/命名空间及 fixture 未初始化工作区的失败已定位并修正测试夹具。Widgets 的 grab 不包含嵌入原生 QML，最终截图改为 QQuickView::grabWindow。没有据此改生产全局导入路径。蓝屏后旧 PCH 无法复用，最终本机 /Y- /MP1 单并行编译；不修改上游构建默认值。
- 未验收项：实际音频/MIDI 设备、长时间播放/编辑和所有特殊谱法；记谱踏板保持不能测量声学衰减，也不能保证唯一和声意图。标注是屏幕临时层，MSCX/PDF 不保存这些文字，需保留分析 JSON。没有复刻或声称掌握 Synthesia 私有算法。
- 日志：msvc.build_harmony_release_x64/harmony-1-1-observer.txt、harmony-1-1-note.txt、harmony-gui-final/gui.txt 与 QML 截图；实际安装宿主报告位于独立插件工作区 tests/native-smoke-installed-1-1。构建日志 harmony-1-1-link.log、harmony-1-1-install.log；运行时、产物、日志均忽略。
- 指南：同步个人入口、架构、功能、钢琴专题、构建验证、通用观察/预览 API 和受影响源码定位；baseline 不改写。
- Git 父提交：b878200db892d62c0481f9d06ae58753cfc6738b。
- Git 提交主题：fix(plugins): stabilize host and extend harmony preview tools。
- 提交定位：personal-v0.3.0 标签指向本条提交，git rev-parse personal-v0.3.0 获取完整 SHA；普通推送到个人 origin/3.x，禁止强推。

'''
p = repo / 'personal/CHANGELOG.md'
s = p.read_text(encoding='utf-8')
assert '## 0.3.0' not in s
write(p, s.replace('## 0.2.0', entry + '## 0.2.0', 1))
p = repo / 'personal/docs/06-build-and-test.md'
write(p, p.read_text(encoding='utf-8') + '''
## 0.3.0 GUI 与上下文回归

新增 tst_pluginhost 验证真实主窗口的菜单、谱面重排、原生 QML 面板和停靠；它关闭硬件音序器，使用临时应用设置，不能替代实际音频设备验收。Windows 测试需要安装资源和 Qt QML/platform 目录；编译测试后运行 `python personal/tools/test_harmony_gui.py <tst_pluginhost.exe> <安装根目录> <输出目录>`，脚本准备隔离运行时并限时 45 秒。直接在原 build 子目录执行时 Qt 资源路径可能不完整。原生 QML 截图用 grabWindow，Widgets grab 不包含嵌入窗口。

tst_scoreobserver 增加踏板边界、时序聚合/休止、全谱帧与原子配置测试；tst_note 保持原测试内容。实际安装插件 smoke 可用 `python personal/tools/test_harmony_host.py <新程序exe> <独立目录> <安装目录内主QML>`；先创建 -c 目录再启动，避免默认设置回退。通过项、性能与限制见个人更新日志 0.3.0。
''')

p = repo / 'personal/docs/source-map.tsv'
rows = list(csv.DictReader(p.open(encoding='utf-8', newline=''), delimiter='\t'))
for row in rows:
    lines = (repo / row['path']).read_text(encoding='utf-8-sig').splitlines()
    hits = [str(i + 1) for i, line in enumerate(lines) if row['symbol'] in line]
    assert hits, row
    row['line'] = hits[0]
with p.open('w', encoding='utf-8', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['topic', 'path', 'symbol', 'line', 'role', 'tests'], delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

archive = plugin / 'dist/HarmonyAssistant-1.1.0.zip'
with zipfile.ZipFile(str(archive), 'w', zipfile.ZIP_DEFLATED) as output:
    for name in names:
        output.write(str(plugin / name), 'HarmonyAssistant/' + name)
print('Release 1.1.0 synchronized with verified backups; personal 0.3.0 documented.')
