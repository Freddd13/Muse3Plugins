from pathlib import Path
import shutil,re
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore';N=R/'native'
for source,name in [('repair-current-performanceeditor/expression-same-note-057.png','expression-same-note-057.png'),('repair-current-performanceeditor/expression-time-057.png','expression-time-057.png'),('repair-current-p1native/manual-expression.png','expression-panel-057.png')]:
 p=R/'out'/source
 if p.exists():
  for dest in [N/'personal/docs/images'/name,R/'docs/images'/name]:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
for name in ['repair-055-arrangement.png','repair-055-chord.png','repair-056-reference.png']:
 p=N/'personal/docs/images'/name
 if p.exists():shutil.copyfile(p,R/'docs/images'/name)
guide=R/'docs/REPAIR_057_GUIDE.md';s=guide.read_text(encoding='utf8')+'''
## 对比界面

![在同一谱位并列显示原、新力度](images/expression-same-note-057.png)

![按各自播放秒数显示两种效果](images/expression-time-057.png)

图中同一和弦各音的顶部有细标记，便于查看同时音的不同力度。点击原值选音，拖动蓝色柱修改候选。

## 本轮检查

演奏编辑器 64 项、P1 操作 50 项、插件窗口 14 项通过。后续的光标、旧速度模板和项目设置修正，另通过 8 项编辑操作、5 项面板操作以及三份界面脚本检查。传统匹配、分范围应用、方案和编配规则脚本均通过；力度设置检查覆盖新项目、旧比例及两种保存方式。
''';guide.write_bytes(s.encode());shutil.copyfile(guide,N/'personal/docs'/guide.name)
delivery=R/'docs/REPAIR_053_057_DELIVERY.md';s=delivery.read_text(encoding='utf8')+'''
## 程序、版本和检查结果

当前个人版本为 **0.57.0 · Kumo branch / Freddd13**。本轮各批提交可通过 personal-v0.53.0 至 personal-v0.57.0 标签定位。

安装程序位于 `msvc.install_repair_current_x64/bin/MuseScore3Evo.exe`，目录中的 `personal/USER_GUIDE.md` 可离线阅读。

完整窗口检查通过：演奏编辑器 64 项、P1 操作 50 项、插件窗口 14 项。最终补充检查通过 8 项编辑与布局操作、5 项导入和录制面板操作；三份 QML 界面脚本及五组 JavaScript 脚本通过。

下表使用相同的生成乐谱和窗口测量，数值表示百分之九十五的缩放操作在该时间内完成，包含原生谱面刷新：

| 音符数量 | 关闭谱行带 | 开启谱行带 |
|---|---:|---:|
| 10,080 | 7.17 ms | 7.92 ms |
| 50,064 | 9.08 ms | 10.72 ms |

五万音符局部视图的两区绘制约 3.23 ms，拖动约 1.87 ms。一次选中并写入整份五万音符乐谱约 951 ms；普通局部编辑按当前选音处理。

MSCZ 已完成标准元数据的保存和重新读取。普通版 3.6.2 安装包下载停在约 0.4 MB，跨程序打开、重新保存的实际检查待连接恢复后补齐。官谱继续只读，验证使用独立测试谱。
''';delivery.write_bytes(s.encode());shutil.copyfile(delivery,N/'personal/docs'/delivery.name)
p=N/'personal/CHANGELOG.md';s=p.read_text(encoding='utf8').replace('- 操作：personal/docs/REPAIR_057_GUIDE.md；','- 恢复缺少内部标识的旧 Kumo 速度模板；新旧表达项目分别读取自己的比例和保存方式。\n- 验证：编辑器 64 项、P1 操作 50 项、插件窗口 14 项；最终改动另通过 8 项及 5 项操作检查。具体结果见 personal/docs/REPAIR_053_057_DELIVERY.md。\n- 操作：personal/docs/REPAIR_057_GUIDE.md；',1);p.write_bytes(s.encode())
p=N/'personal/docs/source-map.tsv';s=p.read_text(encoding='utf8')+'演奏项目设置\tshare/plugins/PerformanceExpression/ExpressionSettings.js\trestored\t8\t新默认与旧项目比例\ttest_velocity_adoption.cjs\n';lines=s.splitlines()
for i,line in enumerate(lines):
 f=line.split('\t')
 if len(f)!=6:continue
 q=N/f[1]
 if not q.exists():q=H/f[1]
 if q.exists():
  hits=[n+1 for n,t in enumerate(q.read_text(encoding='utf8').splitlines()) if f[2] in t]
  if hits:f[3]=str(min(hits,key=lambda n:abs(n-int(f[3]))));lines[i]='\t'.join(f)
p.write_bytes(('\n'.join(lines)+'\n').encode())
p=R.parent/'Planning/REPAIR_053_057.md';s=p.read_text(encoding='utf8').replace('- [ ] 0.57：','- [x] 0.57：');s+='\n五批代码、编译及本分支使用检查已完成。九项操作、性能测量和普通版兼容检查进度见 Repairs/docs/REPAIR_053_057_DELIVERY.md。\n';p.write_bytes(s.encode())
print('0.57 guide, screenshots and per-item delivery prepared')
