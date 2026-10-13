# coding: utf-8
from pathlib import Path
import subprocess,shutil,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
results=json.loads((ROOT.parent/'P1/out/final-regression/summary.json').read_text(encoding='utf8'))
assert all(value['exit']==0 and value['counts'][1]=='0' for value in results.values())
legacy=ET.parse(ROOT/'out/legacy-main.mscx').getroot()
staff=legacy.find("./Score/Staff[@id='2']")
note=staff.find('.//Note')
assert int(note.findtext('pitch'))==36 and int(note.findtext('velocity','0'))==0
shutil.copy2(ROOT.parent/'P1/out/final-regression/regional-042.png',HOST/'personal/docs/images/regional-042.png')
parent=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=HOST).decode().strip()
report='''# 分段方案的保存、切换与兼容检查

2026-10-13，个人版0.42.1，Windows x64、Qt5.15.2。只使用独立测试谱；未改用户谱子或OneDrive官谱。

## 已完成的操作

同一段的不同谱表／声部可以分别建立组和切换。未使用写法压缩保存，当前组合使用普通乐谱对象。复制并打开新写法只产生一次撤销；切换、改名、主方案选择和扩大范围可撤销。图片、分谱链接及手工演奏事件使用原生读写和粘贴。

MSCZ的正常入口保存各组主方案组成的完整乐谱；Kumo/variants/index.json保存当前选择及压缩写法。重新打开本分支后恢复当前组合，加载产生的内部操作不会留在用户撤销列表里。普通版副本可导出当前组合或主方案组合，原文件位置和当前编辑内容不改变。另存MSCX会说明原因并拒绝写入，防止其它写法丢失。

## 实际检查

- 分段专项10项通过，含初始化／结束；覆盖左右手独立组合、连续切换及撤销、旧文件导入、范围扩大、未选声部拒绝、保存主方案／恢复当前组合、普通版副本和保留已有文件。
- 三份现有复杂记谱测试谱逐项比较音符、音高、TPC、时值和延音关系；连音组、圆滑线和延音线保持。资源、手工起音／长度／力度、延长记号、分谱链接经过保存重开验证。
- 实际鼠标点按切换、复制、改名、主方案、显示主方案及试听反馈；复制后列表选中新写法。面板截图已检查，关闭后停止刷新。
- 全部相关检查217项通过：工作流30、插件菜单／显示12、读取／显示17、P0操作22、演奏编辑器51、MIDI79、读写撤销6。系统剪贴板访问关闭，未替代真实剪贴板检查。
- 同一MSCZ用尚不支持分段方案的个人版0.21.0实际打开并转成MSCX，低音C2及力度读取为主方案的值，未读成当前B写法。此处测试的是旧个人版；没有把它说成所有发行版、平台都已实测。

## 范围与代价

总拍数、拍号和谱表结构保持一致。跨界延音、圆滑线、歌词和跨谱表关系不被静默删掉；已有跨界连接时，先撤销连接，扩大范围，再添加连接。其它组占用的声部不能被扩大后的范围覆盖。共同速度、踏板、调号及谱表力度不随局部写法切换。

切换仍包含原生粘贴和排版；保存当前与主方案不同的组合、扩大范围时，会同步读取完整副本。不能把这些操作说成后台或零开销。未使用写法不持续建立可播放、可排版对象；关闭面板不刷新。专项检查约4.3秒，包含窗口操作及多份文件，不能据此声称大型作品的每次操作只需几毫秒。

多音频声音检查见REFERENCE_WORKFLOW_VALIDATION.md。静音设备和合成音的检查不替代代表性钢琴素材的主观听感；频谱、实时录音、完整指法和AI改配没有混入本次交付。
'''
(HOST/'personal/docs/REGIONAL_VARIANTS_VALIDATION.md').write_bytes(report.encode('utf8'))
entry=f'''## 0.42.1 — 2026-10-13

- 新增工具菜单“分段试写方案”：按完整小节、谱表和声部保存多种写法，独立切换，保留编辑与撤销；支持范围扩大、同处试听、名称和主方案选择。
- 一个MSCZ保存全部局部写法。正常入口为主方案组合，本分支重开恢复当前组合；普通版副本明确选择组合，保存失败保留文件。原来的完整副本插件继续使用，可导入符合范围的旧写法。
- 独立模块处理压缩片段、范围、连线、资源和保存；原生音乐对象继续负责排版与播放。常规导出使用屏幕当前组合；不改变默认MIDI路径。
- 重写用户说明第13章，补截图、保存／撤销／迁移和限制。父提交{parent}，提交定位personal-v0.42.1；217项相关检查通过，详见personal/docs/REGIONAL_VARIANTS_VALIDATION.md。

'''
p=HOST/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8');at=s.index('## 0.42.0')
if '## 0.42.1' not in s:p.write_bytes((s[:at]+entry+s[at:]).encode('utf8'))
p=HOST/'personal/docs/source-map.tsv';s=p.read_text(encoding='utf8')
for topic,path,symbol,role in [('分段方案','libmscore/regionalvariants.cpp','QVariantMap select(', '压缩写法、声部范围、原生撤销和连线保护'),('方案保存','libmscore/regionalvariants.cpp','bool save(', '普通主方案入口和本分支当前组合恢复'),('方案面板','mscore/workflow/regionalpanel.cpp','void showRegionalVariantPanel(', '菜单、停靠、复制切换、旧文件和普通版导出')]:
 lines=(HOST/path).read_text(encoding='utf8').splitlines();line=next(i+1 for i,v in enumerate(lines) if symbol in v)
 row='\t'.join([topic,path,symbol,str(line),role,'mtest/mscore/p1native/regional_tests.inc'])
 if '\t'+path+'\t'+symbol+'\t' not in s:s+=row+'\n'
 else:s='\n'.join(row if '\t'+path+'\t'+symbol+'\t' in value else value for value in s.splitlines())+'\n'
p.write_bytes(s.encode('utf8'))
p=ROOT.parent/'Planning/REPAIR_IMPLEMENTATION.md';s=p.read_text(encoding='utf8').replace('- [ ] 6：','- [x] 6：').replace('第5–6批继续实施。','第5批0.41已交付，第6批0.42已交付。')
if '0.42完成第6批' not in s:s+='\n0.42完成第6批：单MSCZ局部分段／声部方案、主方案兼容入口、当前组合恢复、扩大范围、旧写法导入及普通版副本。软件定位personal-v0.42.1。全轮相关检查217项通过；说明书第13章和REGIONAL_VARIANTS_VALIDATION.md记录操作及实际限制。本轮六批已交付，未扩大到尚未批准的频谱、实时录音或AI功能。\n'
p.write_bytes(s.encode('utf8'))
p=ROOT.parent/'Planning/TODO.md';s=p.read_text(encoding='utf8');s=s.replace('日期：2026-10-10。状态：**P0 已批准并实施；其他阶段仍等待逐项选定**。','日期：2026-10-13。状态：**P0、P1及随后批准的集中修复已实施；其余构想仍等待选定**。')
at=s.index('**VAR-03');start=s.rfind('\n',0,at)+1;end=s.index('\n',start)
s=s[:start]+'- [x] **VAR-03 · 已按新计划实施：一个MSCZ内的分段／声部方案。** 0.42采用当前组合使用普通乐谱、未用写法压缩保存的方式；支持停播切换、撤销、资源／分谱、主方案入口和旧项目导入。原完整副本插件保留。具体范围及检查见REPAIR_IMPLEMENTATION.md和用户说明第13章。'+s[end:]
if '## 集中修复交付' not in s:s+='\n## 集中修复交付\n\n2026-10-13：0.32–0.42完成用户批准的六批修复与增强，见[实施记录](REPAIR_IMPLEMENTATION.md)。多音频、三种播放、编辑器演奏对应和局部分段方案按该新计划交付；旧草案中跨完整副本自动合并、频谱、实时捕获、完整指法等仍未勾选，不重复开发已交付的局部切换。\n'
p.write_bytes(s.encode('utf8'))
p=ROOT.parent/'Planning/README.md';s=p.read_text(encoding='utf8')
if '## 集中修复交付' not in s:s+='\n## 集中修复交付\n\n本轮批准内容已按六批完成至0.42.1，见[实施记录](REPAIR_IMPLEMENTATION.md)。日常操作阅读软件personal/USER_GUIDE.md；历史草案中尚未批准的内容继续保留。\n'
p.write_bytes(s.encode('utf8'))
print('检查记录、兼容结果、截图、更新日志和待办已同步。')
