from pathlib import Path
import csv, io, shutil
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'

def read(k):
 p=R/'native'/k
 return (p if p.exists() else H/k).read_text('utf8')
def put(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode('utf8'))

guide=(R/'docs/BUILTIN_058_GUIDE.md').read_text('utf8')
put('personal/docs/P2_BUILTIN_058_GUIDE.md',guide)
s=read('personal/USER_GUIDE.md').replace('当前个人版本：**0.57.0**','当前个人版本：**0.58.0**',1)
section='''## 0.58 的内置工具

从“视图 → 和弦助手”打开和弦工具；从“视图 → 演奏表达”进入编辑器内的导入、录制、比较和采用操作。原插件菜单入口打开同一个工具。完整步骤和界面见[内置工具使用说明](docs/P2_BUILTIN_058_GUIDE.md)。

'''
if '## 0.58 的内置工具' not in s:s=s.replace('## 0.53 的操作修复',section+'## 0.53 的操作修复',1)
s=s.replace('| 查看和弦、级数和构成音 | 插件 → Harmony Assistant |','| 查看和弦、级数和构成音 | 视图 → 和弦助手 |')
s=s.replace('| 把演奏 MIDI 的力度用于谱子 | 插件 → Performance Expression |','| 把演奏 MIDI 的力度用于谱子 | 视图 → 演奏表达 |')
s=s.replace('| 听原曲、慢放、循环 | 插件 → Reference Player |','| 听原曲、慢放、循环 | 视图 → 原曲参考 |')
if 'personal-v0.58.0' not in s:s+='\n\n本批版本定位：`personal-v0.58.0`。\n'
put('personal/USER_GUIDE.md',s)
s=read('personal/CHANGELOG.md')
section='''## 0.58.0 — 2026-10-17

- 和弦助手增加原生视图菜单与独立窗口管理；顶部摘要、详情、范围及旧配置沿用，插件入口打开同一个工具。
- 演奏表达主要操作放入演奏编辑器工具页，导入、录制、比例、保存方式、试听和采用集中显示。
- 设置与核对使用独立详情窗口，首次展开保留谱面空间；编辑页切换保留当前演奏项目。
- 新材料沿用 100% 演奏力度、逐音固定与同音对比，已有项目继续恢复原设置。
- 操作：personal/docs/P2_BUILTIN_058_GUIDE.md；提交定位：personal-v0.58.0。

'''
if '## 0.58.0' not in s:s=s.replace('# 个人版本更新日志\n\n','# 个人版本更新日志\n\n'+section,1)
put('personal/CHANGELOG.md',s)
rows=list(csv.DictReader(io.StringIO(read('personal/docs/source-map.tsv')),delimiter='\t'))
rows += [dict(topic='内置和弦工具',path='mscore/workflow/builtinpanels.cpp',symbol='void showHarmonyPanel(',line='1',role='单实例停靠、插件兼容入口',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),dict(topic='编辑器演奏表达',path='mscore/workflow/builtinpanels.cpp',symbol='void installExpressionTools(',line='1',role='共享表达界面、原生编辑器工具页',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp')]
seen=set();unique=[]
for row in rows:
 if row['path']=='share/plugins/HarmonyAssistant/HarmonyAssistant_MS3.qml' and 'followNativePosition' in row['symbol']:row['path']='share/plugins/HarmonyAssistant/HarmonyAssistant.view.qml'
 test_aliases={
  'reloadActiveWorkflowPanels':'mtest/mscore/pluginhost/tst_pluginhost.cpp',
  'realPanelMouseActions':'mtest/mscore/p1native/tst_p1native.cpp',
  'repair054EndpointSidesAndHandText':'mtest/mscore/performanceeditor/tst_performanceeditor.cpp',
  'nativeWorkflowDocumentAndTypography':'mtest/mscore/pluginhost/tst_pluginhost.cpp',
  'nativeReferenceDocumentAndMenu':'mtest/mscore/p1native/tst_p1native.cpp',
  'expressionVelocityModesAndComparison':'mtest/mscore/performanceeditor/tst_performanceeditor.cpp',
  'test-rules.cjs':'../../muse3_plugins/ArrangementAssistant/tests/test-rules.cjs',
  'test_velocity_adoption.cjs':'../../muse3_plugins/Repairs/tests/test_velocity_adoption.cjs'}
 row['tests']=';'.join(test_aliases.get(t.strip(),t.strip()) for t in row['tests'].split(';'))
 key=(row['path'],row['symbol'])
 if key in seen:continue
 seen.add(key)
 f=R/'native'/row['path']
 if not f.exists():f=H/row['path']
 if f.exists() and row['symbol']!='-':
  matches=[i+1 for i,l in enumerate(f.read_text('utf8',errors='replace').splitlines()) if row['symbol'] in l]
  if matches:row['line']=str(min(matches,key=lambda n:abs(n-int(row['line']))))
 unique.append(row)
out=io.StringIO();writer=csv.DictWriter(out,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(unique)
put('personal/docs/source-map.tsv',out.getvalue())
image=R.parent/'P1/out/final-regression/builtin-expression-ready-058.png'
if image.exists():
 for target in (R/'native/personal/docs/images',R/'docs/images'):
  target.mkdir(parents=True,exist_ok=True);shutil.copyfile(image,target/image.name)
print('已整理 0.58 操作说明、开发记录和源码位置')
