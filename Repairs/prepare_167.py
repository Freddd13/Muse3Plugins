"""Publish the full current feature check and the startup-view repair."""
from pathlib import Path
import json
import shutil

R=Path(__file__).resolve().parents[1]
N=R/'P2/native'
H=R.parent/'muse3_dev/MuseScore'
O=R/'P2/out/usability-167'
report='personal/docs/CURRENT_FEATURE_CHECK_167.md'
(R/'Planning/CURRENT_FEATURE_CHECK_167.md').write_text((N/report).read_text('utf8'),encoding='utf8',newline='\n')
images=[]
for source,name in [('expression-same-note-057.png','current-expression-167.png'),
                    ('midi-only-necessary-preview.png','current-midi-167.png'),
                    ('spectrum-settings-162.png','current-spectrum-167.png')]:
    target='personal/docs/images/'+name
    shutil.copy2(O/source,N/target)
    images.append(target)

for base in (N,H):
    (base/'personal/VERSION').write_text('0.167.0\n',encoding='utf8',newline='\n')
    p=base/'personal/USER_GUIDE.md'
    text=p.read_text('utf8').replace('当前版本：**0.166.0','当前版本：**0.167.0',1)
    previous='本次修正动态乐谱与AI谱图的文字比例，统一各行音符大小；完整进度见[0.166整轮审视](docs/ROUND_166_REVIEW.md)（`personal-v0.166.0`）。'
    assert previous in text
    text=text.replace(previous,'本次修复第一次打开工作视图又跳回的问题，并检查之前全部修复和新增工具。逐项操作、实际画面和后续安排见[本轮完整检查](docs/CURRENT_FEATURE_CHECK_167.md)（`personal-v0.167.0`）。',1)
    text=text.replace('0.166包含之前各版的累计修复和新增工具。','当前程序包含之前各版的累计修复和新增工具。',1)
    p.write_text(text,encoding='utf8',newline='\n')
    p=base/'personal/CHANGELOG.md'
    text=p.read_text('utf8').replace('\n\n','''

## 0.167.0 — 2026-11-08

- 修复延后的启动恢复覆盖刚选择的工作视图，保留当前明确操作及各视图个人布局。
- 从个人设置副本和真实钢琴谱副本完成连续编辑、写法切换、踏板、试听及保存重开。
- 逐项检查此前01—33项和最近N1—N9，补齐真实演奏对应、旧工作区速度面板、MIDI改手／松手与扩展开关保存往返；操作、画面及后续见CURRENT_FEATURE_CHECK_167.md。
- 检查程序按当前标签页、区域开关和Windows焦点准备实际控件，保留产品设置；同步源码索引和累计用户说明。发布定位personal-v0.167.0。
- 安装与提交信息随后补入。

''',1)
    p.write_text(text,encoding='utf8',newline='\n')
    p=base/'personal/docs/REWORK_PROGRESS.md'
    text=p.read_text('utf8')
    anchor='## 2026-11-08：0.166整轮审视与谱面输出修复'
    section='''## 2026-11-08：0.167全部近期功能的实际检查

检查覆盖此前01—33项和最近N1—N9。修复首次选择编曲后，延后的启动恢复又切回后处理、隐藏编辑器的问题；已有工作区、区域开关和个人比例继续保留。实际钢琴谱副本完成编辑、A/B、踏板、播放、视图切换和保存重开。

真实演奏、录制结果、导出比较、旧工作区符号和扩展开关保存往返均有本轮操作记录；逐项结果、画面和固定后续见[完整检查](CURRENT_FEATURE_CHECK_167.md)。安装与提交信息随后补入。

'''
    assert anchor in text
    p.write_text(text.replace(anchor,section+anchor,1),encoding='utf8',newline='\n')
    p=base/'personal/docs/FEATURES_166_OVERVIEW.md'
    text=p.read_text('utf8').replace('**当前程序：0.166.0 · Kumo branch / Freddd13。** 这是累计更新，包含前面各版的修复和新增功能。最近一次修正了动态乐谱及 AI 谱图的尺寸，整套工具继续一起提供。','**当前程序：0.167.0 · Kumo branch / Freddd13。** 包含前面各版的修复和新增功能。本次修复首次工作视图恢复，并检查整套工具；[逐项操作和结果](CURRENT_FEATURE_CHECK_167.md)。',1)
    p.write_text(text,encoding='utf8',newline='\n')

files=['mscore/workflow/workspaceviews.cpp','mtest/mscore/pluginhost/composition_flow_tests.inc',
       'mtest/mscore/pluginhost/playback_159_tests.inc','mtest/mscore/pluginhost/reference_input_120_tests.inc',
       'mtest/mscore/pluginhost/workspace_093_tests.inc','mtest/mscore/pluginhost/layout_079_tests.inc',
       'personal/VERSION','personal/USER_GUIDE.md','personal/CHANGELOG.md',
       'personal/docs/REWORK_PROGRESS.md','personal/docs/FEATURES_166_OVERVIEW.md',report,*images]
p=N/'personal/docs/source-map.tsv'
rows=p.read_text('utf8').splitlines()
for index,row in enumerate(rows):
    cells=row.split('\t')
    if len(cells)<6 or cells[1] not in files or not (N/cells[1]).is_file():continue
    lines=(N/cells[1]).read_text('utf8').splitlines()
    match=next((i+1 for i,line in enumerate(lines) if cells[2] in line),None)
    if match:
        cells[3]=str(match)
        rows[index]='\t'.join(cells)
line=next(i+1 for i,value in enumerate((N/'mscore/workflow/workspaceviews.cpp').read_text('utf8').splitlines()) if 'initialRestorePending = true' in value)
rows.append('\t'.join(['首次工作视图恢复','mscore/workflow/workspaceviews.cpp','bool initialRestorePending',str(line),'明确选择视图后结束排队的启动恢复，保留个人布局','mtest/mscore/pluginhost/composition_flow_tests.inc']))
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
files.append('personal/docs/source-map.tsv')
for name in files:
    if name!='personal/USER_GUIDE.md':shutil.copy2(N/name,H/name)
(O/'release-files.json').write_text(json.dumps(files,indent=2),encoding='utf8')
print('Prepared 0.167 repair, cumulative feature results and user instructions.')
