from pathlib import Path
import shutil
R=Path(__file__).resolve().parent
for source,name in [('repair-current-p1native/arrangement-range-050.png','repair-055-arrangement.png'),('repair-current-pluginhost/C_E-baseline.png','repair-055-chord.png')]:
 p=R/'native/personal/docs/images'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'out'/source,p)
for p in [R/'docs/REPAIR_055_GUIDE.md',R/'native/personal/docs/REPAIR_055_GUIDE.md']:
 s=p.read_text(encoding='utf8')+'\n## 本轮界面与操作检查\n\n![编配检查的范围、分类与详情](images/repair-055-arrangement.png)\n\n![共同基线上的和弦与转位级数](images/repair-055-chord.png)\n\n使用真实窗口完成范围拖动、位置拖动、撤销、重做、分类、谱旁提示和保存重开。插件面板 14 项及 P1 操作 49 项通过。速度面板保留当前对象，重复整理后仍可添加渐慢。\n'
 p.write_bytes(s.encode())
p=R/'native/personal/CHANGELOG.md';s=p.read_text(encoding='utf8').replace('- 操作：personal/docs/REPAIR_055_GUIDE.md；','- 速度面板重复整理时保留已有对象，修复旧引用失效；主动打开面板时明确接收键盘焦点。\n- 验证：插件窗口 14 项、P1 操作 49 项，以及渐慢与手部文字布局检查通过。\n- 操作：personal/docs/REPAIR_055_GUIDE.md；',1);p.write_bytes(s.encode())
p=R.parent/'Planning/REPAIR_053_057.md';s=p.read_text(encoding='utf8').replace('- [ ] 0.55：','- [x] 0.55：');p.write_bytes(s.encode())
