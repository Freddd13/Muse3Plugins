from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
for name,count in [('performanceeditor',56),('p0native',23),('p1native',44)]:
 text=(R/f'out/repair-050-full-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
assert 'Totals: 4 passed, 0 failed' in (R/'out/repair-050-benchmark/gui.txt').read_text(encoding='utf8',errors='replace')
assert 'Totals: 12 passed, 0 failed, 0 skipped' in (R/'out/repair-050-media-device.txt').read_text(encoding='utf8',errors='replace')
source=R/'out/repair-050-full-p1native'
for original,name in [('harmony-summary-style-050.png','assistants-050-style.png'),('harmony-range-drag-050.png','assistants-050-harmony.png'),('arrangement-nearby-050.png','assistants-050-problem.png'),('reference-multi-041.png','assistants-050-reference.png')]:
 for folder in [R/'docs/images',HOST/'personal/docs/images']:
  folder.mkdir(parents=True,exist_ok=True);shutil.copy2(source/original,folder/name)
p=R/'docs/ASSISTANTS_050_VALIDATION.md';s=p.read_text(encoding='utf8');s=s.replace('完整检查数量与缩放耗时在发布前补入本页。','窗口检查123项全部通过：演奏编辑器56项、P0导出23项、P1工具44项；另有12项音频检查和10份JS规则检查文件。')
raw=(R/'out/repair-050-benchmark/gui.txt').read_text(encoding='utf8',errors='replace');measure={(count,band):value for count,band,value in re.findall(r'Score Ctrl zoom (\d+) notes: band (\d+) P95 ([\d.]+)',raw)};assert len(measure)==4,measure
if '## 缩放耗时' not in s:
 s+='\n## 缩放耗时\n\n| 谱中音符 | 关闭谱行带 | 开启谱行带 |\n|---|---:|---:|\n'
 for count in ['10080','50064']:s+='| '+count+' | '+measure[count,'0']+' ms | '+measure[count,'1']+' ms |\n'
 s+='\n窗口大小和乐谱与0.48、0.49检查相同，数字包含原生谱面刷新。\n'
p.write_text(s,encoding='utf8',newline='\n');shutil.copy2(p,HOST/'personal/docs/ASSISTANTS_050_VALIDATION.md')
p=R/'USER_GUIDE_CURRENT.md';s=p.read_text(encoding='utf8').replace('**0.49.0**','**0.50.0**').replace('`personal-v0.49.0`','`personal-v0.50.0`');s=s.replace('## 10. 编配检查','![和弦范围调整](docs/images/assistants-050-harmony.png)\n\n## 10. 编配检查').replace('## 11. 原曲参考','![谱旁问题说明](docs/images/assistants-050-problem.png)\n\n## 11. 原曲参考');s=s.replace('## 12. 演奏表达','![原曲多音轨](docs/images/assistants-050-reference.png)\n\n## 12. 演奏表达');s=s.replace('停靠到顶部后，','停靠到顶部后，')
p.write_text(s,encoding='utf8',newline='\n');(R/'USER_GUIDE.md').write_text(s.replace('[开发日志](CHANGELOG.md)','[开发日志](../../muse3_dev/MuseScore/personal/CHANGELOG.md)'),encoding='utf8',newline='\n')
p=HOST/'personal/USER_GUIDE.md';existing=p.read_bytes();marker='## Codex 钢琴编曲与 MCP 桥接'.encode();assert marker in existing;tail=existing[existing.index(marker):];p.write_bytes(s.rstrip().encode()+b'\n\n'+tail);assert p.read_bytes().endswith(tail)
(HOST/'personal/VERSION').write_bytes(b'0.50.0\n')
for folder,version in [('HarmonyAssistant','1.10.0'),('ArrangementAssistant','1.3.0'),('ReferencePlayer','1.3.0'),('PerformanceExpression','1.5.1')]:
 p=ROOT/folder/(folder+'_MS3.qml');text=p.read_text(encoding='utf8');text,n=re.subn(r'(\bversion\s*:\s*)"[^"]+"',lambda m:m[1]+'"'+version+'"',text,count=1);assert n==1;p.write_text(text,encoding='utf8',newline='\n')
p=HOST/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8');entry="""## 0.50.0 — 2026-10-16

- 和弦摘要使用原生和弦字体排版，字号、级数大小、间距、排列与调性可调整；修复短面板菜单、浮窗位置和详情显示。谱面记号可拖位置，范围两端与面板同步，支持修正撤销和分析文件保存。
- 编配检查保留检查范围和各谱结果，顶部摘要与右侧分别开关；同位置问题合并入口，谱旁显示解释。自动和弦参与持续冲突检查，显示实际涉及的音。
- 原曲参考支持直接选片段、拖数值、空格播放和按住空格平移；关联可逐条播放、修改、删除与恢复，内部对齐点在独立详情窗调整。一次播放选择一条重叠关联。
- 原位试听与联合播放补齐循环、末尾休止、两边长度不同的结束处理，并恢复用户原先的预备拍和乐谱循环设置；总音量立即作用于准备好的声音。
- 用户说明第9–11章按按钮与操作重写。123项窗口检查、12项音频检查通过；截图和耗时见personal/docs/ASSISTANTS_050_VALIDATION.md。
- 提交定位：personal-v0.50.0。继续已批准的符号、分手折线、圆滑线、试写和MIDI音长对比调整。

"""
if '## 0.50.0' not in s:s=s.replace('## 0.49.0',entry+'## 0.49.0',1);p.write_text(s,encoding='utf8',newline='\n')
p=HOST/'personal/docs/source-map.tsv';rows=p.read_text(encoding='utf8').splitlines()
entries=[('乐谱分析身份','mscore/workflow/analysisidentity.cpp','ScoreObserver::analysisScoreId','跨面板的乐谱身份与内容变化','mtest/mscore/p1native/assistant_surface_tests.inc'),('谱面位置提示','mscore/workflow/positionhint.cpp','void showWorkflowPositionHint','定位后短时强调谱段','mtest/mscore/p1native/assistant_surface_tests.inc'),('和弦摘要字体','mscore/workflow/harmonylabel.cpp','ScoreObserver::harmonyLabel','音乐字体和级数紧凑渲染','mtest/mscore/p1native/assistant_surface_tests.inc'),('谱面和弦编辑','mscore/workflow/chordeditor.cpp','ScoreObserver::setChordEditRegion','作用范围和显示位置拖动','mtest/mscore/p1native/assistant_surface_tests.inc'),('原曲联合播放','mscore/workflow/referenceworkflow.cpp','ScoreObserver::startReferencePlayback','独立结束、循环与设置恢复','mtest/mscore/performanceeditor/expression_playback_tests.inc')]
for topic,path,symbol,role,tests in entries:
 lines=(HOST/path).read_text(encoding='utf8').splitlines();hits=[i+1 for i,line in enumerate(lines) if symbol in line];assert len(hits)==1,(path,symbol)
 rows=[v for v in rows if '\t'+path+'\t'+symbol+'\t' not in v];rows.append('\t'.join([topic,path,symbol,str(hits[0]),role,tests]))
for i,row in enumerate(rows):
 fields=row.split('\t')
 if len(fields)==6 and (HOST/fields[1]).is_file():
  hits=[n+1 for n,line in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
  if hits:fields[3]=str(min(hits,key=lambda n:abs(n-int(fields[3]))));rows[i]='\t'.join(fields)
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8').replace('- [ ] 2：','- [x] 2：').replace('- [ ] 3：','- [x] 3：');s+='\n0.50.0：123项窗口检查、12项音频检查和大谱缩放检查通过。第二、三批完成，接着处理符号、分手折线、圆滑线与试写/MIDI对比。详见Repairs/docs/ASSISTANTS_050_VALIDATION.md。\n';p.write_text(s,encoding='utf8',newline='\n')
print('0.50文档、截图、版本和源码位置已整理。',flush=True)
