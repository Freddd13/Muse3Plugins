from pathlib import Path
import shutil,re
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
for folder,count in [('full-performanceeditor',60),('full-p1native-retry',44),('full-p0native',23)]:
 assert f'Totals: {count} passed, 0 failed' in (R/f'out/repair-051-{folder}/gui.txt').read_text(encoding='utf8',errors='replace'),folder
for folder in [R/'docs/images',HOST/'personal/docs/images']:
 folder.mkdir(parents=True,exist_ok=True)
 shutil.copy2(R/'out/repair-051-full-performanceeditor/slur-routes-inspector-051.png',folder/'notation-051-slur.png')
 shutil.copy2(R/'out/repair-051-full-performanceeditor/hand-placement-score-051.png',folder/'notation-051-hands.png')
p=R/'USER_GUIDE_CURRENT.md';s=p.read_text(encoding='utf8').replace('**0.50.0**','**0.51.0**').replace('`personal-v0.50.0`','`personal-v0.51.0`');p.write_text(s,encoding='utf8',newline='\n')
(R/'USER_GUIDE.md').write_text(s.replace('[开发日志](CHANGELOG.md)','[开发日志](../../muse3_dev/MuseScore/personal/CHANGELOG.md)'),encoding='utf8',newline='\n')
p=HOST/'personal/USER_GUIDE.md';existing=p.read_bytes();marker='## Codex 钢琴编曲与 MCP 桥接'.encode();tail=existing[existing.index(marker):];p.write_bytes(s.rstrip().encode()+b'\n\n'+tail);assert p.read_bytes().endswith(tail)
(HOST/'personal/VERSION').write_bytes(b'0.51.0\n')
p=HOST/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8');entry='''## 0.51.0 — 2026-10-16

- 自由圆滑线可选择整条线或两点之间的一段，指定从音符上方或下方经过；相邻曲线共用切线。“整理这一段”保持中间点位置，整理切线。整条线选择方向时同时使用原生端点方向，一次撤销恢复。
- 区段走向随节点保存，拖动、锁定和整理继续保留；沿用旧谱节点格式。相同几何结果可复用，减少重复排版计算。
- 分手折线根据实际所指音、谱间、加线和附近符杠摆放；点击范围与实际线条分别计算。可显示斜体l.h.／r.h.；修复建立链接分谱时读取旧加线谱表编号造成的崩溃。
- 整理本分支生成的旧rit.、a tempo和四方向折线格子，保留自制格子；调整缩略图比例。
- 说明第8章随实际按钮重写。窗口操作、保存重开、撤销和导出检查见personal/docs/NOTATION_051_VALIDATION.md。提交定位：personal-v0.51.0。

'''
assert '## 0.51.0' not in s;s=s.replace('## 0.50.0',entry+'## 0.50.0',1);p.write_text(s,encoding='utf8',newline='\n')
p=HOST/'personal/docs/source-map.tsv';rows=p.read_text(encoding='utf8').splitlines()
for topic,path,symbol,role in [('圆滑线区段走向','libmscore/freeslur.cpp','QVector<Route> routing','区段与跨谱行坐标'),('圆滑线整理切线','libmscore/freeslur.cpp','bool FreeSlur::smoothNode','保持点位置整理共用切线'),('圆滑线绕行','libmscore/freesluravoidance.cpp','AvoidanceResult avoid(','方向约束与形状复用'),('分手折线位置','libmscore/handbracket.cpp','QPointF position(','谱间位置与音头符杠碰撞'),('速度符号升级','mscore/temposymbols.cpp','void appendPlayableTempoSymbols','升级旧格子并保留自制符号')]:
 hits=[i+1 for i,line in enumerate((HOST/path).read_text(encoding='utf8').splitlines()) if symbol in line];assert len(hits)==1,(path,symbol);rows=[r for r in rows if '\t'+path+'\t'+symbol+'\t' not in r];rows.append('\t'.join([topic,path,symbol,str(hits[0]),role,'mtest/mscore/performanceeditor/notation_051_tests.inc']))
for i,row in enumerate(rows):
 fields=row.split('\t')
 if len(fields)==6 and (HOST/fields[1]).is_file():
  hits=[n+1 for n,line in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
  if hits:fields[3]=str(min(hits,key=lambda n:abs(n-int(fields[3]))));rows[i]='\t'.join(fields)
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
text='''# 0.51 记谱操作检查

选中圆滑线，开启自由曲线，添加两个点，分别指定起始段上行、结束段下行。鼠标选择方向、整理切线、一次撤销、保存MSCX/MSCZ重开及换行均通过；曲线两侧切线连续。谱面、检视器截图和PDF保存在本轮检查目录。

分手折线覆盖32个所指音，含线、间、加线、和弦内音与跨谱表。四个方向、直接拖动、个人默认设置、旧字形和链接分谱保存通过。建立分谱时发现的加线坐标崩溃已修复。

速度面板导入含旧标识、重复格子和自制格子的工作区，保留一项可播放rit.和a tempo、四方向折线及自制格子。面板保存重开后仍一致。

窗口检查：演奏编辑器60项、P1工具44项、P0导出23项通过。完整辅助面板第一次检查曾偶发崩溃；后续带调试器和普通运行均通过，安装后继续重复同一顺序检查。

局部路线形状复用200次耗时0.25ms左右；完整大谱缩放数字随发布后检查记录。测试使用独立乐谱，参考官谱仅查看图片。

![区段设置](images/notation-051-slur.png)

![不同谱位的分手折线](images/notation-051-hands.png)
'''
(R/'docs/NOTATION_051_VALIDATION.md').write_text(text,encoding='utf8',newline='\n');shutil.copy2(R/'docs/NOTATION_051_VALIDATION.md',HOST/'personal/docs/NOTATION_051_VALIDATION.md')
p=ROOT/'Planning/REPAIR_2026_10_SECOND_PASS.md';s=p.read_text(encoding='utf8').replace('- [ ] 4：','- [x] 4：');s+='\n0.51：第四批完成，区段走向、平滑切线、分手折线位置和旧符号清理已加入实际窗口检查。继续第五批写法对比、组合与MIDI音长编辑。\n';p.write_text(s,encoding='utf8',newline='\n')
print('0.51说明、源码位置和发布记录已写入。')
