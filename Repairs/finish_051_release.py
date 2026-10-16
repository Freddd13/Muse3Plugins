from pathlib import Path
import re,shutil,subprocess
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore';install=HOST/'msvc.install_repair_0_51_x64'
for name,count in [('performanceeditor',60),('p0native',23),('p1native',45)]:
 text=(R/f'out/repair-051-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert f'Totals: {count} passed, 0 failed' in text,name;assert not re.search(r'TypeError:|ReferenceError:|Unable to assign \[undefined\]',text),name
for n in [1,2]:assert 'Totals: 45 passed, 0 failed' in (R/f'out/repair-051-lifetime-repeat{n}/gui.txt').read_text(encoding='utf8',errors='replace')
for folder in [R/'docs/images',HOST/'personal/docs/images']:
 for source,dest in [('slur-routes-inspector-051.png','notation-051-slur.png'),('hand-placement-score-051.png','notation-051-hands.png')]:shutil.copy2(R/'out/repair-051-delivery-performanceeditor'/source,folder/dest)
p=R/'docs/NOTATION_051_VALIDATION.md';s=p.read_text(encoding='utf8');s=s.replace('P1工具44项','P1工具45项').replace('完整辅助面板第一次检查曾偶发崩溃；后续带调试器和普通运行均通过，安装后继续重复同一顺序检查。','完整辅助面板检查中捕捉到了图像绘制访问失效资源的问题。各窗口改为分别建立控件、复用图像缓存，并调整退出清理顺序后，安装版完整流程连续三次通过；每次包含六次双窗口开关与停靠位置变化。').replace('完整大谱缩放数字随发布后检查记录。','完整大谱缩放数字见下表。')
raw=(R/'out/repair-051-benchmark/gui.txt').read_text(encoding='utf8',errors='replace');assert 'Totals: 4 passed, 0 failed' in raw
measure={(a,b):c for a,b,c in re.findall(r'Score Ctrl zoom (\d+) notes: band (\d+) P95 ([\d.]+)',raw)}
s+='\n| 谱中音符 | 关闭谱行带 | 开启谱行带 |\n|---|---:|---:|\n'
for count in ['10080','50064']:s+=f'| {count} | {measure[count,"0"]} ms | {measure[count,"1"]} ms |\n'
s+='\n关于窗口已显示Kumo branch / Freddd13 · v0.51.0。\n';p.write_text(s,encoding='utf8',newline='\n');shutil.copy2(p,HOST/'personal/docs/NOTATION_051_VALIDATION.md')
p=HOST/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8').replace('- 说明第8章随实际按钮重写。','- 和弦与编配检查的摘要、详情各自在固定窗口建立控件，共用设置和结果；复用和弦图像缓存，调整窗口退出清理顺序，修复软件绘制模式下反复开关时的偶发崩溃。\n- 说明第8章随实际按钮重写。');p.write_text(s,encoding='utf8',newline='\n')
for name,version in [('HarmonyAssistant','1.10.1'),('ArrangementAssistant','1.3.1')]:
 p=ROOT/name/(name+'_MS3.qml');s=p.read_text(encoding='utf8');s,n=re.subn(r'(\bversion\s*:\s*)"[^"]+"',lambda m:m[1]+'"'+version+'"',s,count=1);assert n==1;p.write_text(s,encoding='utf8',newline='\n');shutil.copy2(p,HOST/'share/plugins'/name/p.name);shutil.copy2(p,install/'plugins'/name/p.name) if (install/'plugins'/name).is_dir() else None
p=HOST/'personal/docs/source-map.tsv';rows=p.read_text(encoding='utf8').splitlines()
for i,row in enumerate(rows):
 fields=row.split('\t')
 if len(fields)==6 and (HOST/fields[1]).is_file():
  hits=[n+1 for n,line in enumerate((HOST/fields[1]).read_text(encoding='utf8').splitlines()) if fields[2] in line]
  if hits:fields[3]=str(min(hits,key=lambda n:abs(n-int(fields[3]))));rows[i]='\t'.join(fields)
p.write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
marker='## Codex 钢琴编曲与 MCP 桥接'.encode();old=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST);now=(HOST/'personal/USER_GUIDE.md').read_bytes();assert now[now.index(marker):]==old[old.index(marker):]
(install/'personal').mkdir(exist_ok=True)
for name in ['USER_GUIDE.md','CHANGELOG.md','VERSION']:shutil.copy2(HOST/'personal'/name,install/'personal'/name)
shutil.copytree(HOST/'personal/docs',install/'personal/docs',dirs_exist_ok=True)
print('0.51安装后检查、截图与说明已整理。')
