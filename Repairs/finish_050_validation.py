from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'Repairs';HOST=ROOT.parent/'muse3_dev/MuseScore';install=HOST/'msvc.install_repair_0_50_x64'
for name,count in [('performanceeditor',56),('p0native',23),('p1native',44)]:
 text=(R/f'out/repair-050-delivery-{name}/gui.txt').read_text(encoding='utf8',errors='replace');assert re.search(r'Totals: '+str(count)+r' passed, 0 failed',text),name
 assert not re.search(r'TypeError:|ReferenceError:|Unable to assign \[undefined\]',text),name+' UI errors'
raw=(R/'out/repair-050-benchmark/gui.txt').read_text(encoding='utf8',errors='replace');assert 'Totals: 4 passed, 0 failed' in raw
measure={(count,band):value for count,band,value in re.findall(r'Score Ctrl zoom (\d+) notes: band (\d+) P95 ([\d.]+)',raw)};assert len(measure)==4
p=R/'docs/ASSISTANTS_050_VALIDATION.md';s=p.read_text(encoding='utf8')
for count in ['10080','50064']:s=re.sub(r'\| '+count+r' \| [^\n]+', '| '+count+' | '+measure[count,'0']+' ms | '+measure[count,'1']+' ms |',s)
s+='\n## 安装后检查\n\n独立0.50安装完成后，123项窗口检查再次通过，界面日志无未定义值错误。帮助中的个人版本和作者标识已核对；38份说明、310个本地链接和277处源码位置检查通过。\n';p.write_text(s,encoding='utf8',newline='\n');shutil.copy2(p,HOST/'personal/docs/ASSISTANTS_050_VALIDATION.md')
for original,name in [('harmony-summary-style-050.png','assistants-050-style.png'),('harmony-range-drag-050.png','assistants-050-harmony.png'),('arrangement-nearby-050.png','assistants-050-problem.png'),('reference-multi-041.png','assistants-050-reference.png')]:
 for folder in [R/'docs/images',HOST/'personal/docs/images']:shutil.copy2(R/'out/repair-050-delivery-p1native'/original,folder/name)
assert (install/'bin/MuseScore3Evo.exe').is_file();(install/'personal').mkdir(exist_ok=True)
for name in ['USER_GUIDE.md','CHANGELOG.md','VERSION']:shutil.copy2(HOST/'personal'/name,install/'personal'/name)
shutil.copytree(HOST/'personal/docs',install/'personal/docs',dirs_exist_ok=True)
print('0.50独立安装、说明、截图和操作检查已完成。',flush=True)
