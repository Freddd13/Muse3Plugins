from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix=ROOT/'USER_GUIDE.md';text=prefix.read_text(encoding='utf8').replace('**0.36.1**','**0.37.0**')
needle='选择一段连续乐谱，用“添加 → 文本 → 渐变速度（rit.）”。'
replacement='''**从符号面板添加。** 展开左侧“速度”，把鼠标放在rit.上可看到“渐慢 rit.（可播放）”。先在谱面拖选一段连续范围，再双击这个格子；或把它拖到谱表小节内，从落下的位置渐慢到该小节末尾。a tempo格子显示“恢复渐变前的速度”：先点选恢复位置，再双击，或直接拖到该位置。两种操作都可一次撤销。

旧速度面板会保留你已有的格子，并补上这两个可播放记号；再次加载不会重复增加。纯文字a tempo格子仍保留，新格子的鼠标说明明确写出播放功能。有速度记号或渐变冲突时会说明原因，不覆盖它们；播放时先停止。

**改变文字和线条。** 选中rit.，检视器的文字线区域分别设置“开始文字”“续行文字”“结束文字”，例如poco rit.。线条区域可控制是否显示线、线条样式、粗细、虚线长度和间隔。隐藏线条仍会渐慢。手动拖动位置后保留你的设置；与其它文字拥挤时可调整位置和文字字号。

原菜单也保留：选择一段连续乐谱，用“添加 → 文本 → 渐变速度（rit.）”。'''
assert needle in text;text=text.replace(needle,replacement);prefix.write_bytes(text.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n';guide=HOST/'personal/USER_GUIDE.md'
working=guide.read_text(encoding='utf8');head=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(head)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.37.0\n')
path=HOST/'personal/CHANGELOG.md';s=path.read_text(encoding='utf8');at=s.index('## 0.36.1')
s=s[:at]+'''## 0.37.0 — 2026-10-13

- 速度符号面板加入可播放rit.和a tempo。旧速度面板读取后保留原格子并补齐新格子，重复读取不重复添加；其它类型和个人混合面板保持原内容。
- 双击和拖放走已有演奏参数操作，完整检查速度冲突、停止／准备状态，显示成功或具体原因；一次撤销。调过的文字、前后缀、线条样式、字体及速度目标从格子复制，不只使用固定默认文本。
- 用户说明补齐面板、恢复速度、开始／续行／结束文字、线条显隐及虚线设置。文字自动摆放沿用原生排版；更复杂的线条避让继续在后面的工作中处理。
- Git父提交2aee11019；提交定位personal-v0.37.0。工作流18项通过，含实际鼠标双击、旧面板保留／重复读取、文字与线条设置、一次撤销和冲突保护。保留先前系统剪贴板未验收记录。

'''+s[at:];path.write_bytes(s.encode('utf8'))
index=HOST/'personal/docs/source-map.tsv';s=index.read_text(encoding='utf8')
for path,symbol,role in [('mscore/temposymbols.cpp','void appendPlayableTempoSymbols','补齐速度格子，保留已有内容'),('mscore/temposymbols.cpp','bool applyPlayableTempoSymbol','双击的范围、播放与冲突检查'),('mscore/temposymbols.cpp','bool applyPlayableTempoDrop','拖放位置与小节末尾范围')]:
 line=next(i for i,v in enumerate((HOST/path).read_text(encoding='utf8').splitlines(),1) if symbol in v)
 s+='\t'.join(['速度符号面板',path,symbol,str(line),role,'mtest/mscore/p1native'])+'\n'
index.write_bytes(s.encode('utf8'))
plan=ROOT.parent/'Planning/REPAIR_IMPLEMENTATION.md';s=plan.read_text(encoding='utf8').replace('第3批速度符号面板、自由圆滑线与分手项目，以及第4–6批继续实施。','第3批速度符号面板入口已发布0.37.0：rit./a tempo、旧面板补齐、实际双击、冲突保护及样式复制；工作流18项通过。更复杂的文字／线条避让、自由圆滑线与分手项目，以及第4–6批继续实施。');plan.write_bytes(s.encode('utf8'))
readme=ROOT/'README.md';s=readme.read_text(encoding='utf8').replace('0.32.0–0.36.1','0.32.0–0.37.0');readme.write_bytes(s.encode('utf8'))
