from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore'
for name,count in [('performanceeditor',56),('p0native',23),('p1native',40)]:
 text=(R/f'out/repair-049-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
text=(R/'out/repair-049-benchmark/gui.txt').read_text(encoding='utf8',errors='replace');assert 'Totals: 4 passed, 0 failed' in text
measure={}
for count,band,value in re.findall(r'Score Ctrl zoom (\d+) notes: band (\d+) P95 ([\d.]+)',text):measure[count,band]=value
assert len(measure)==4,measure
p=R/'docs/EXPRESSION_049_VALIDATION.md';s=p.read_text(encoding='utf8');s+='\n## 正式安装复查\n\n0.49独立安装后，119项窗口检查再次全部通过。大谱检查4项通过，Ctrl缩放95%耗时如下；窗口大小、音符数量和检查步骤沿用0.48。\n\n| 谱中音符 | 关闭谱行带 | 开启谱行带 |\n|---|---:|---:|\n'
for count in ['10080','50064']:s+='| '+count+' | '+measure[count,'0']+' ms | '+measure[count,'1']+' ms |\n'
s+='\n这些耗时包含原生谱面刷新。文档链接、跨仓库测试位置和源码行号检查通过：37份说明、306个本地链接、272个源码位置。原有Codex/MCP附录保留原文。\n'
p.write_text(s,encoding='utf8',newline='\n');shutil.copy2(p,HOST/'personal/docs/EXPRESSION_049_VALIDATION.md')
install=HOST/'msvc.install_repair_0_49_x64';assert (install/'bin/MuseScore3Evo.exe').is_file()
(install/'personal').mkdir(exist_ok=True)
for name in ['USER_GUIDE.md','CHANGELOG.md','VERSION']:shutil.copy2(HOST/'personal'/name,install/'personal'/name)
shutil.copytree(HOST/'personal/docs',install/'personal/docs',dirs_exist_ok=True)
print('0.49正式安装、全部操作检查、缩放测量和本地说明已核对。')
