# -*- coding: utf-8 -*-
"""Record completed checks; copy small evidence only, preserving all old artifacts."""
from pathlib import Path
import shutil,json,hashlib,subprocess
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore');base=Path(__file__).resolve().parents[1]
build=repo/'msvc.build_harmony_release_x64';installed=repo/'msvc.install_harmony_1_5_x64'
def write(p,s):p.write_bytes((s.rstrip()+'\n').encode('utf-8'))
observer=(build/'harmony-observer-1-5/gui.txt').read_text(encoding='utf-8',errors='replace')
host=(build/'harmony-gui-1-5/gui.txt').read_text(encoding='utf-8',errors='replace')
assert '17 passed, 0 failed, 0 skipped' in observer
assert '12 passed, 0 failed, 0 skipped' in host
smoke=json.loads((installed/'validation/smoke/native-smoke.json').read_text(encoding='utf-8-sig'))
assert not smoke['failures'] and smoke['persistedCorrection']=='Am/C'
for source,dest in [(build/'harmony-observer-1-5','native-observer-1-5'),(build/'harmony-gui-1-5','native-gui-1-5'),(installed/'validation/smoke','native-smoke-installed-1-5')]:
    for folder in [base/'tests'/dest,installed/'validation'/dest]:
        folder.mkdir(parents=True,exist_ok=True)
        for p in source.iterdir():
            if p.is_file() and p.suffix in ('.png','.txt','.json','.log'):shutil.copy2(str(p),str(folder/p.name))
p=repo/'personal/CHANGELOG.md';s=p.read_text(encoding='utf-8')
s=s.replace('- 验证：本次最终构建与测试记录见独立安装 validation 和插件 tests/native-*-1-5；用户说明与源码索引同步维护。具体通过项将在最终验收后补记。','''- 验证：最终 x64 Release 构建／独立安装成功；tst_scoreobserver 17、实际 Windows Qt tst_pluginhost 12 项全部通过，0 失败／跳过。新增六条旧行均冲突但行间有空位、原谱高音＋速度文字、相邻长记号保持 x、超页待排与当前版本标识；原有选色／播放／拖放／P 键盘／选区框／原色清理对照保留。JS 和弦／配置交换／区间、Qt 固定布局／双面板／范围交互、真实明暗控件点击输入和待排列表定位通过。正式安装连续两次启动恢复样式与 Am/C 人工区间；关于／启动画面已目视核对 Kumo branch／Freddd13／v0.22.0。已存在 Qt Connections 弃用、临时工作区缺文件及空文件名警告，不宣称无警告。
- 测量：1000 小节／6000 音符索引 27.687 ms，1000 缓存快照 1.962 ms，上下文 6.507 ms；数值分析帧 25.139 ms，基础色层定位 22.434 ms；1000 次既有记号索引高亮 0.736 ms，不含绘制。初始几何／字形／检测仍有成本，未将这些数值表述为音频硬实时指标。
- 文档检查：本次源码锚点已刷新、diff --check 通过；check_guides.py 仍报告 USER_GUIDE 三个原有跨仓库链接（MCP 上下文及字体 README／验证）离开仓库，保留它们且不纳入本任务无关修复。用户／并行说明增量未提交。
- 证据：独立安装 validation 及插件 tests/native-*-1-5 保存小量日志／截图／启动报告。最初测试复制输出误置于安装目录，改为防递归的目录外隔离助手；原临时副本移到构建目录留存，未删除文件。''',1)
write(p,s)
p=base/'README.md';s=p.read_text(encoding='utf-8')
assert '1.5 验证：' not in s
write(p,s+'''

1.5 验证：最终 x64 Release 构建与独立安装成功，观察器 17／真实 Qt 宿主 12 项全部通过，0 失败／跳过。新增旧六行间隙、高音＋速度文字、相邻长记号、超页待排及 v0.22.0 关于／启动画面回归；固定布局、双面板、区域历史／拖动和原生选择配色对照保留。明暗控件真实点击／输入、完整列表与定位通过，安装连续启动两次恢复样式及 Am/C 人工区间。现有弃用／临时工作区警告仍在日志中，不宣称无警告。

本次 1000 小节／6000 音符：索引 27.687 ms、1000 缓存快照 1.962 ms、上下文 6.507 ms、数值帧 25.139 ms、基础色层 22.434 ms；1000 次记号高亮索引切换 0.736 ms，不含实际重绘。日志见 tests/native-*-1-5。防递归的目录外测试助手为 tests/run_gui_1_5.py。
''')
for folder in (repo/'share/plugins/HarmonyAssistant',installed/'plugins/HarmonyAssistant',Path('C:/Users/Fred/Documents/MuseScore3/插件/HarmonyAssistant')):
    shutil.copy2(str(p),str(folder/p.name))
exe=installed/'bin/MuseScore3Evo.exe'
report={'pluginVersion':'1.5.0','personalVersion':'0.22.0','nativeBase':'3dc1d38c837875befe292c7a73f4eecd82dd03cb','exeSHA256':hashlib.sha256(exe.read_bytes()).hexdigest(),
 'checks':{'observer':17,'pluginhost':12,'failed':0,'skipped':0,'restartCorrection':'Am/C','lightDarkControls':True,'markerListClick':True,'fixedAndDualPanel':True,'nativeColorPriority':True,'highTrebleAndTempo':True},
 'limits':['Finite page space can still require pending markers; full analysis remains in the list.','No real audio-device long-session stress test.','Existing Qt warnings remain.','Three pre-existing guide links leave the software repository.']}
write(installed/'validation/release-1.5-validation.json',json.dumps(report,ensure_ascii=False,indent=2))
print('Recorded 17 observer / 12 real host checks, restart persistence and reviewed screenshots; runtime docs synchronized')
