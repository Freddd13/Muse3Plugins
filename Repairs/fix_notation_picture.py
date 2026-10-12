from pathlib import Path
import subprocess,shutil
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
prefix=ROOT/'USER_GUIDE.md';text=prefix.read_text(encoding='utf8').replace('**0.36.0**','**0.36.1**');prefix.write_bytes(text.encode('utf8'))
marker='<summary>展开较早版本说明</summary>\n\n';guide=HOST/'personal/USER_GUIDE.md'
working=guide.read_text(encoding='utf8');head=subprocess.check_output(['git','show','HEAD:personal/USER_GUIDE.md'],cwd=HOST).decode('utf8')
def history(value):return value.split(marker,1)[1].rsplit('\n</details>',1)[0]
guide.write_bytes((text.rstrip()+'\n\n'+history(working)+'\n</details>\n').encode('utf8'))
(ROOT/'out/guide-index.md').write_bytes((text.rstrip()+'\n\n'+history(head)+'\n</details>\n').encode('utf8'))
(HOST/'personal/VERSION').write_bytes(b'0.36.1\n')
shutil.copyfile(ROOT.parent/'P1/out/final-regression/input-332-coherent.png',HOST/'personal/docs/images/input-332-036.png')
path=HOST/'personal/CHANGELOG.md';s=path.read_text(encoding='utf8');at=s.index('## 0.36.0')
s=s[:at]+'''## 0.36.1 — 2026-10-13

- 修正说明书3-3-2图示的空白截图：捕获前定位实际音符，检查画面确有谱面内容。原菜单与输入操作检查仍14/14通过。
- Git父提交41bf0d727；提交定位personal-v0.36.1。保留0.36全部音乐用例和剪贴板未验收记录。

'''+s[at:];path.write_bytes(s.encode('utf8'))
for relative in ['Planning/REPAIR_IMPLEMENTATION.md','Repairs/README.md']:
 path=ROOT.parent/relative;s=path.read_text(encoding='utf8').replace('0.32.0–0.36.0','0.32.0–0.36.1').replace('输入净谱已发布0.36.0','输入净谱已发布0.36.1（含图示修正）');path.write_bytes(s.encode('utf8'))
