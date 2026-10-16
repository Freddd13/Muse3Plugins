from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'Repairs'
HOST=ROOT.parent/'muse3_dev/MuseScore'
for name,count in [('performanceeditor',56),('p0native',23),('p1native',40)]:
 text=(R/f'out/repair-049-full-{name}/gui.txt').read_text(encoding='utf8',errors='replace')
 assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
for src,name in [('editor-expression-main-049.png','expression-049-editor.png'),('recorded-expression-preview.png','expression-049-panel.png')]:
 source=R/'out/repair-049-expression-4'/src
 for folder in [R/'docs/images',HOST/'personal/docs/images']:
  folder.mkdir(parents=True,exist_ok=True);shutil.copy2(source,folder/name)
guide=R/'USER_GUIDE_CURRENT.md';text=guide.read_text(encoding='utf8').replace('**0.48.0 ·','**0.49.0 ·')
guide.write_text(text,encoding='utf8',newline='\n')
(R/'USER_GUIDE.md').write_text(text.replace('[开发日志](CHANGELOG.md)','[开发日志](../../muse3_dev/MuseScore/personal/CHANGELOG.md)'),encoding='utf8',newline='\n')
p=HOST/'personal/USER_GUIDE.md';existing=p.read_bytes();marker='## Codex 钢琴编曲与 MCP 桥接'.encode();assert marker in existing;tail=existing[existing.index(marker):]
p.write_bytes(text.rstrip().encode()+b'\n\n'+tail);assert p.read_bytes().endswith(tail)
shutil.copy2(R/'docs/EXPRESSION_049_VALIDATION.md',HOST/'personal/docs/EXPRESSION_049_VALIDATION.md')
(HOST/'personal/VERSION').write_bytes(b'0.49.0\n')
p=ROOT/'PerformanceExpression/PerformanceExpression_MS3.qml';s=p.read_text(encoding='utf8').replace('version:"1.4.0"','version:"1.5.0"');p.write_text(s,encoding='utf8',newline='\n')
p=HOST/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8');at=s.index('## 0.48.0');entry='''## 0.49.0 — 2026-10-16

- 演奏表达在原力度／速度区显示谱中与拟采用效果，支持拖动、绘制和预览撤销。保留选音、筛选、时间尺与播放光标，演奏对应可单独展开。
- 试听使用准备好的事件材料，在原谱上保持当前拍位切换；结束比较后恢复正常播放。关闭旧试听页入口保留用户已修改的页面。
- 使用力度／速度可选择音、选段或全部已对应范围，应用后继续处理其余音。首次应用前的力度随音符保存，重开MSCZ后可以按范围恢复，每次应用与恢复各自撤销。
- 记号力度线补动态文字并合并重复标签；修复比较按钮显示时覆盖原参数选择框的问题。选择变化使用轻量状态更新，对应时间在结果变化时准备。
- 用户说明第12章按实际按钮重写，补保存与恢复、错漏音定位和两种试听效果。119项窗口检查通过，具体操作与截图见personal/docs/EXPRESSION_049_VALIDATION.md。
- 提交定位：personal-v0.49.0。参考播放器、和弦、编配检查和其它已批准调整继续分批完成。

'''
if '## 0.49.0' not in s:p.write_text(s[:at]+entry+s[at:],encoding='utf8',newline='\n')
p=HOST/'personal/docs/source-map.tsv';rows=p.read_text(encoding='utf8').splitlines()
entries=[('演奏力度恢复','libmscore/velocitybackup.cpp','void remember(','首次应用前力度、复制读写及撤销','mtest/mscore/p1native/velocity_history_tests.inc'),('演奏对比','mscore/performanceeditor/expressioncompare.cpp','void PerformanceEditor::syncExpressionComparison()','原参数区前后对比、拖动和绘制','mtest/mscore/performanceeditor/expression_compare_tests.inc'),('演奏试听','mscore/workflow/playbackpreview.cpp','QVariantMap startPlaybackPreview(','当前展开拍位切换与普通播放恢复','mtest/mscore/performanceeditor/expression_playback_tests.inc'),('演奏应用','mscore/workflow/workflowexpression.cpp','QVariantMap ScoreObserver::restoreExpressionVelocity(','选音、选段恢复与随谱保存','mtest/mscore/p1native/expression_application_tests.inc'),('记号力度文字','mscore/performanceeditor/markvelocity.cpp','MarkVelocityText readMarkVelocityText(','动态文字与谱表作用范围','mtest/mscore/performanceeditor/tst_performanceeditor.cpp')]
for topic,path,symbol,role,tests in entries:
 lines=(HOST/path).read_text(encoding='utf8').splitlines();hits=[i+1 for i,line in enumerate(lines) if symbol in line];assert len(hits)==1,(path,symbol)
 row='\t'.join([topic,path,symbol,str(hits[0]),role,tests]);rows=[v for v in rows if '\t'+path+'\t'+symbol+'\t' not in v];rows.append(row)
for i,row in enumerate(rows):
 fields=row.split('\t')
 if len(fields)==6 and (HOST/fields[1]).is_file():
  hits=[n+1 for n,line in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
  if len(hits)==1:fields[3]=str(hits[0]);rows[i]='\t'.join(fields)
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8');s+='\n0.49.0：演奏表达原参数区对比、原位试听、分范围应用及力度恢复已实现，119项窗口检查通过。第12章说明与EXPRESSION_049_VALIDATION.md记录操作。联合播放及循环继续随第三批检查，第二批勾选在这一项完成后更新。\n';p.write_text(s,encoding='utf8',newline='\n')
print('0.49说明、版本和源码索引已更新，Codex/MCP附录保持原内容。')
