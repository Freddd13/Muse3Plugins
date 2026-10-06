# -*- coding: utf-8 -*-
"""Release sync and guide index; no source rewriting or file removal."""
from pathlib import Path
import shutil,subprocess,csv,io
base=Path(__file__).resolve().parents[1]
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
installed=repo/'msvc.install_harmony_1_4_x64'
enabled=Path('C:/Users/Fred/Documents/MuseScore3/插件/HarmonyAssistant')
def write(path,text):
    with path.open('w',encoding='utf-8',newline='\n') as out:out.write(text)
p=repo/'mscore/notepreview.h';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
p=base/'README.md';s=p.read_text(encoding='utf-8').replace('两项 Python 面板测试','Python 面板测试')
s+='\n最终安装程序连续启动两次通过，样式及 `Am/C` 人工区间均从隔离设置自动恢复；原有音符 suite 11 项通过。导入先校验全部区间再写状态，坏数据不会改动已有人工修正。\n';write(p,s)
runtime=sorted(p for p in base.iterdir() if p.suffix in ('.qml','.js') or p.name=='README.md')
assert len(runtime)==14
# Reject concurrent edits of the enabled 1.3 copy before making any changes.
for p in runtime:
    target=enabled/p.name;old=base/'backups/1.3.0'/(p.name+'.bak')
    if target.exists():
        assert old.exists() and target.read_bytes()==old.read_bytes(), 'Enabled copy was independently changed: '+p.name
for p in runtime:
    target=enabled/p.name
    if target.exists():
        backup=enabled/(p.name+'.pre-1.4.0.bak')
        assert not backup.exists() or backup.read_bytes()==target.read_bytes()
        if not backup.exists():shutil.copy2(str(target),str(backup))
    for destination in (repo/'share/plugins/HarmonyAssistant',installed/'plugins/HarmonyAssistant',enabled):
        shutil.copy2(str(p),str(destination/p.name))
# Refresh only anchors affected by the changed files, adding the two new modules.
p=repo/'personal/docs/source-map.tsv'
with p.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
extra=[('harmony-regions','share/plugins/HarmonyAssistant/Timeline.js','function createBuilder','Numeric interval builder and manual overlays','mtest/mscore/scoreobserver'),
       ('harmony-range-editing','share/plugins/HarmonyAssistant/RangeEditor.qml','objectName:"harmonyRangeEditor"','Range handles, ticks and independent history','mtest/mscore/pluginhost')]
for topic,path,symbol,role,tests in extra:
    assert not any(r['topic']==topic for r in rows)
    rows.append(dict(topic=topic,path=path,symbol=symbol,line='',role=role,tests=tests))
for row in rows:
    lines=(repo/row['path']).read_text(encoding='utf-8').splitlines()
    matches=[i+1 for i,line in enumerate(lines) if row['symbol'] in line]
    assert matches,(row['path'],row['symbol'])
    current=int(row['line'] or 0)
    if current not in matches:row['line']=str(matches[0])
output=io.StringIO();writer=csv.DictWriter(output,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows);write(p,output.getvalue())
parent=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'rev-parse','HEAD']).decode().strip()
assert parent=='abf9e3453ce1aee4ca8268f854cc02cba45404bb2' or parent.startswith('abf9e3453'), 'Native HEAD changed concurrently'
p=repo/'personal/CHANGELOG.md';s=p.read_text(encoding='utf-8');assert '## 0.8.0 — ' not in s
entry='''## 0.8.0 — 2026-10-06

- 类型：和声助手 1.4.0 的区间识别/人工修正、专用字形与原生颜色保护；上游仍 3.7.0，保留 0.7.1 自动记谱与 0.6 音源改动。
- 插件：Timeline.js 加权模板、单/多和弦踏板开关、低音/转位与攻击起点连续性、相邻区间合并；高声部扩展音不重设低音和声。摘要/详情各选实时或所属区间；手柄/精确 tick、指定/拆分/合并/抑制/恢复、独立 Undo/Redo。指纹绑定人工修正自动读写，谱面改变须复核；schema 2 分析交换兼容 schema 1，坏导入全量验证后才写盘。
- 原生边界：仅 events.cpp、notepreview.h、scoreview.cpp、scoreobserver.h/.cpp 五处生产文件。补充攻击 tick、每乐器当前踏板元数据与二分索引；独立 MasterScore 样式副本/原生 Harmony/QPicture，加载尚未使用的 chord list，渲染内容哈希使样式变化失效。最多六条避让行保留 x，单击/双击激活；不创建保存谱面元素，不改音频回调。
- 原功能：预览调用 Element::curColor 保持原生选中/播放/拖放/隐藏优先级，去除覆盖原生播放颜色的预览下划线；HPiano、原生 curColor 和选区框宽度均未改动。测试中逐像素对照并检验清理恢复。
- 验证：tst_scoreobserver 16、实际 tst_pluginhost 10、tst_note 11 项全部通过，0 失败/跳过。插件逻辑/配置交换/区间、固定布局/双面板/人工历史/坏导入、真实手柄拖动吸附与绑定恢复通过。最终安装真实宿主连续启动两次，样式与 Am/C 人工区间自动恢复、谱面颜色不变。GUI 使用独立设置与测试进程，未控制用户已打开的谱面。
- 性能：1000 小节/6000 音符：索引 26.468 ms、1000 快照 1.948 ms、1000 上下文 6.464 ms、数值分析帧 24.044 ms、基础色层几何 21.655 ms；1000 次标记索引高亮 0.703 ms，不含绘制。离线 Node 10000 切片约 1.9 秒，生产 QML 分批最多 32 步/约 6 ms 预算。首次建索引/全谱分析/字形避让仍有成本，无零开销或音频硬实时承诺。
- 部署：x64 Release 链接/新目录 msvc.install_harmony_1_4_x64 安装通过；同 SDK Qt5QmlModels/WorkerScript 补齐。插件 14 个发布文件在工作区、share/plugins、新安装、已启用副本逐个核对；启用副本旧文件备份 .pre-1.4.0.bak，旧安装/音源/所有历史文件保留。
- 维护：更新 personal/docs/10、04、README、source-map 与插件 README。音高/踏板不能唯一决定和声，复杂复调可人工修正；最多六行仍可能省略，提供计数。未做用户实谱、长期会话和真实音频/MIDI 硬件验收。
- Git 父提交：PARENT。
- Git 提交主题：feat(harmony): add editable harmonic regions and native symbol previews。
- 提交定位：personal-v0.8.0 标签指向本次提交；普通 push 分支/标签，不强推。

'''.replace('PARENT',parent)
s=s.replace('## 0.7.1 — ',entry+'## 0.7.1 — ',1);write(p,s)
print('Synced 14 release files with guarded enabled backups; guides/log ready')
