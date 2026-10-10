# -*- coding: utf-8 -*-
"""Cumulative user documentation; retain pre-existing concurrent USER_GUIDE edits."""
from pathlib import Path
import subprocess
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
base=Path(__file__).resolve().parents[1]
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as stream:stream.write(text)
guide='''

## 和声助手 1.5：界面与密集谱面（个人版本 0.22.0）

从「插件 → Harmony Assistant」开启，或先在插件管理器启用 `HarmonyAssistant_MS3.qml`。新安装为 `msvc.install_harmony_1_5_x64/bin/MuseScore3Evo.exe`，旧程序保留；只有新的主程序提供本次自适应避让。

- 界面改为紧凑检查器分区、细分隔线与统一的输入控件，明暗背景跟随主程序；原有功能音配色、记号样式及保存配置保留。顶部左／中／右／自定义位置、右侧共享详情、浮动窗口和稳定的告警／键盘区域均保留。
- 谱面记号在和弦变化的水平位置显示，遇到高音、速度文字或已有记号时按实际障碍边界向上找空位；不再仅尝试六个固定高度。没有冲突的记号仍在共同基线。
- 面板「记号」查看当前乐器的全部识别点及起止范围，点击即可定位、高亮并打开详情。页面确实放不下时入口变为「记号 !」，列表显示「待排」；分析仍保留且可导出。
- 持续同一和弦默认只标在起点；想逐小节提示可开设置中的小节重复。原谱已有和弦／级数按原有优先开关避免重复，可在列表区分无新变化与待排。

限制：预览不增加原谱系统间距、不移动原谱对象，也不写入乐谱或 PDF；极密集／过大字号／页边界无空位仍可能待排。初始避让有成本，播放沿用缓存只切换高亮，不每帧重新排版；不承诺任意工程零开销。仅凭局部截图不能确定某个空白究竟是无新识别点、原谱优先还是待排。

提交定位：`personal-v0.22.0`（原生屏幕避让／状态元数据及插件发布副本），插件源标签 `harmony-v1.5.0`；开发边界见 [观察器说明](docs/10-score-observer.md)。
'''
p=repo/'personal/USER_GUIDE.md';work=p.read_text(encoding='utf-8')
assert '## 和声助手 1.5：' not in work
original=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'show','HEAD:personal/USER_GUIDE.md']).decode('utf-8')
def update(text):return text.replace('当前个人版本 **0.21.0**','当前个人版本 **0.22.0**',1).rstrip()+guide+'\n'
write(p,update(work))
# Commit this HEAD-based version only; unrelated pending guide sections stay in the working tree.
write(base/'native/user-guide-index-1.5.md',update(original))
p=repo/'personal/CHANGELOG.md';text=p.read_text(encoding='utf-8')
entry='''## 0.22.0 — 2026-10-10

- 功能：发布 HarmonyAssistant 1.5.0；参考成熟 DAW 检查器组织方式，插件采用随宿主明暗变化的平面控件、紧凑分区与稳定文本空间。保留顶部定位、共享右侧、悬浮、配置／人工范围／分析交换及功能配色。
- 密集谱面：用通用矩形空位搜索取代六个固定高度，按原谱及已排记号的实际边界上移，x 始终对应变化 tick；包括高音、速度文字及其他谱表。绝对页面边界不足时 `previewStatus.unplaced` 返回待排 tick／track／文本，插件「记号」列表展示完整识别点并可点击定位，不静默丢失。
- 解耦：原生生产改动仅 notepreview.h 的纯几何函数及 ScoreObserver 屏幕布局／状态字段；不改模型、保存、排版、音频、P 键盘或选区框，不增加播放避让或动画计时器。主题及交互集中 UiTheme／Desk*／MarkerList，音乐算法未改。
- 验证：本次最终构建与测试记录见独立安装 validation 和插件 tests/native-*-1-5；用户说明与源码索引同步维护。具体通过项将在最终验收后补记。
- 基准：任务开始两仓库 ff-only 拉取已最新；继承软件父提交 `3dc1d38c837875befe292c7a73f4eecd82dd03cb`（0.21.0 后字体安装说明），保留用户／并行任务 AGENTS.md 与 USER_GUIDE.md 原有未提交内容；只提交本任务用户说明增量。
- Git：主题 `fix(harmony): redesign inspector and adapt chord marker placement`；定位 `personal-v0.22.0`。独立安装 `msvc.install_harmony_1_5_x64`，保留 Kumo branch／Freddd13 与由 personal/VERSION 生成的 v0.22.0 标识；不覆盖旧安装。
- 限制：页面空间有限时仍可待排，列表保留结果；同和弦区间默认仅起点标记。首次索引／布局有成本，实机声卡长时间播放未作为本次验收，不承诺硬实时或零开销。

'''
assert '## 0.22.0 —' not in text
write(p,text.replace('## 0.21.0 —',entry+'## 0.21.0 —',1))
p=repo/'personal/docs/10-score-observer.md'
write(p,p.read_text(encoding='utf-8').rstrip()+'''

## 0.22.0：实际空位搜索与待排元数据

`findPreviewChordBox` 是只处理矩形的内联纯几何函数：从共同基线出发，每次跳到相交障碍的上沿，至多 obstacleCount+1 轮；保持 x，遇页面边界返回空。applyPreview 一次查询该记号 x 范围内从页顶到基线的 Page 空间索引，收集可见对象／谱线以及已排记号；无需六条采样行和六次空间查询。首次构建仍有代价，播放的有序区间索引、高亮切换与音频回调不变。

`previewStatus` 新增 `unplaced` 数值／文本列表 `{tick,track,chord,degree}`，保留 `hidden` 和 `fontFallback`。清全部预览时重置这些字段，避免切谱沿用旧状态。QML MarkerList 以当前乐器区间为模型，待排不删除识别区间；列表激活复用既有 openAnnotation 路径。原谱优先及区间起点规则不变；页内空间不足仍不覆盖原对象、不移动原谱布局。

UiTheme／DeskButton／DeskSwitch／DeskComboBox／DeskSpinBox／DeskTextField 统一宿主调色板与紧凑控件；RangeEditor 和 ConfigurationEditor 保留现有事件／数据语义。新增纯几何六行间隙回归、实际高音＋速度文字点击定位／密集记号／超页待排回归，以及当前版本关于／启动画面检查。提交定位 personal-v0.22.0；最终测试记录见 CHANGELOG。
\n''')
for name,entry in [('04-feature-map.md','0.22.0 和声界面：UiTheme.qml／Desk*.qml 统一主题，MarkerList.qml 展示全部识别点；notepreview.h::findPreviewChordBox 保持 x 的实际空位搜索，ScoreObserver::applyPreview 返回待排元数据。纯几何及真实高音／速度文字回归见 tst_scoreobserver／tst_pluginhost。'),('README.md','0.22.0 和声助手 1.5 的紧凑界面、实际空位避让与待排列表见 [用户说明](../USER_GUIDE.md) 和 [10 观察器](10-score-observer.md)；继承最新 0.21.0 的其他功能。')]:
    p=repo/'personal/docs'/name;write(p,p.read_text(encoding='utf-8').rstrip()+'\n\n'+entry+'\n')
p=repo/'personal/docs/source-map.tsv';lines=p.read_text(encoding='utf-8').splitlines()
changed=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp','share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml']
for i,line in enumerate(lines[1:],1):
    cells=line.split('\t')
    if len(cells)<6 or cells[1] not in changed:continue
    source=(repo/cells[1]).read_text(encoding='utf-8').splitlines()
    hits=[n+1 for n,text in enumerate(source) if cells[2] in text]
    if hits:cells[3]=str(hits[0]);lines[i]='\t'.join(cells)
for topic,path,symbol,role in [
 ('和弦空位搜索','mscore/notepreview.h','inline QRectF findPreviewChordBox','保持 x；按障碍上沿查空隙，页面有限边界'),
 ('和弦识别点列表','share/plugins/HarmonyAssistant/MarkerList.qml','ColumnLayout {','完整当前乐器区间及待排；点击定位'),
 ('和声宿主主题','share/plugins/HarmonyAssistant/UiTheme.qml','QtObject {','明暗系统调色板与统一紧凑控件')]:
    source=(repo/path).read_text(encoding='utf-8').splitlines();line=next(n+1 for n,text in enumerate(source) if symbol in text)
    lines.append('\t'.join([topic,path,symbol,str(line),role,'mtest/mscore/pluginhost']))
write(p,'\n'.join(lines)+'\n')
(repo/'share/plugins/HarmonyAssistant/README.md').write_bytes((base/'README.md').read_bytes())
print('Updated separate user guide, development log and source map; saved task-only guide index candidate')
