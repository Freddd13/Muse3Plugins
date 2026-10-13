from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix=ROOT/'USER_GUIDE.md';text=prefix.read_text(encoding='utf8').replace('**0.37.0**','**0.38.0**')
old='当前版手动节点由你绕开音符，后续自动避让会另行说明。'
new='''**自动绕开音符。** 勾选“自动避让音符”，同时保持检视器原有“自动放置”开启。先尝试简单弧线；有遮挡时才增加少量临时弯曲。这些临时点不会写成一串手工节点，也不会改变播放。已经手调过的旧曲线默认不开启此功能。

**保留自己调好的点。** 中间点默认锁定。取消“锁定这个点和切线”后，自动避让才可移动它；再勾选锁定，会保留屏幕上当前位置。拖动或修改数值也会自动锁定。添加点时使用当前曲线的位置。两端仍附在原音符上，排版、缩放或保存不会偷偷改动你的节点数据。

**重新自动调整。** “恢复自动形状”清除中间点并开启避让，一次撤销即可恢复。你调整过的两端和原有手柄偏移仍保留；若希望也恢复它们，请使用原生“重置”。关闭“自由曲线”会暂时使用普通曲线，重新开启可恢复保存的数据。

检视器会提示仍有拥挤位置或内容过密。锁定点处有遮挡时，可先解除该点锁定或手动移动；程序不会为了避让把锁定点挪走，也不会无限增高曲线。跨谱行分别调整该行的形状；跨谱表仍采用该行所属谱表的碰撞信息，必要时手调。

![自由圆滑线的自动避让和锁定设置](docs/images/slur-038.png)'''
assert old in text or '自动绕开音符' in text;text=text.replace(old,new).replace('自动手指释放、自由曲线自动避让等不能仅凭计划当成已交付。','自动手指释放等不能仅凭计划当成已交付。')
prefix.write_bytes(text.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n';guide=HOST/'personal/USER_GUIDE.md'
working=guide.read_text(encoding='utf8');head=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(head)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.38.0\n')
path=HOST/'personal/CHANGELOG.md';s=path.read_text(encoding='utf8');at=s.index('## 0.37.0')
s=s if '## 0.38.0' in s else s[:at]+'''## 0.38.0 — 2026-10-13

- 自由圆滑线新增可选自动避让、点与切线锁定、恢复自动形状及拥挤提示。先尝试普通弧线，必要时最多加4个临时局部点；保持连接平滑，限制高度，不改变保存的手调数据和播放。
- 旧5值节点继续读取并保持锁定；解除锁定写入可选第6项。自动模式单独保存，旧文件默认为关闭。添加、锁定和拖动都从当前显示位置开始，避免突然跳动；恢复自动形状一次撤销。
- 自动计算仅在相关圆滑线排版时进行，2048个障碍以上保留形状并提示。端点不移动；跨谱表及极密内容仍可能需要手调，不声称所有线都能完全避开。
- Git父提交8ade6e8b4；提交定位personal-v0.38.0。测试结果见personal/docs/FREE_SLUR_VALIDATION.md。系统剪贴板复制仍未验收。

'''+s[at:];path.write_bytes(s.encode('utf8'))
index=HOST/'personal/docs/source-map.tsv';s=index.read_text(encoding='utf8')
for path,symbol,role in [('libmscore/freesluravoidance.cpp','AvoidanceResult avoid(','限次曲线候选、碰撞检查与锁定点保护'),('libmscore/freeslur.cpp','bool SlurSegment::displayedFreeNode(double','从当前显示位置添加和锁定节点'),('mscore/inspector/freeslurinspector.h','class FreeSlurInspector','自动避让、锁定、恢复与状态说明')]:
 line=next(i for i,v in enumerate((HOST/path).read_text(encoding='utf8').splitlines(),1) if symbol in v)
 if not any(row.split('\t')[1:3]==[path,symbol] for row in s.splitlines()):s+='\t'.join(['自由圆滑线',path,symbol,str(line),role,'mtest/mscore/performanceeditor'])+'\n'
index.write_bytes(s.encode('utf8'))
print('圆滑线说明、日志和版本已更新。')
