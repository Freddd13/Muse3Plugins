"""Record the focused startup result and keep the overall round in order."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-165'
files = json.loads((O / 'files.json').read_text('utf8'))
log = (O / 'startup-workspace.txt').read_text('utf8', errors='replace')
assert 'PASS   : TestPluginHost::scoreVideoWorkspace164()' in log and 'FAIL!' not in log

name = 'personal/docs/images/score-video-workspace-165.png'
assert not (H / name).exists()
files[name] = None
shutil.copy2(O / 'video-workspace-164.png', N / name)

p = N / 'personal/docs/ROUND_165_REVIEW.md'
t = p.read_text('utf8')
anchor = '上轮检查直接建立了一个菜单和面板，绕过了这些步骤。本次将这一检查改为读取完整启动产生的菜单与工具栏，再载入缺少视频入口的旧菜单，最后打开制作面板、切换视图和关闭。'
assert anchor in t
t = t.replace(anchor, anchor + '\n\n修复后，启动菜单与工具栏指向同一动作；恢复旧菜单及连续更新后保持一项。已从该动作打开面板，自动准备谱行，切到编曲再返回后处理，面板恢复原高度，关闭后鼠标正常释放。查看了这次完整窗口的实际截图：\n\n![0.165完整窗口中的动态乐谱](images/score-video-workspace-165.png)', 1)
p.write_text(t, encoding='utf8', newline='\n')

name = 'personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md'
raw = (H / name).read_bytes()
files[name] = hashlib.sha256(raw).hexdigest()
t = raw.decode('utf8').replace('\r\n', '\n').replace('当前程序0.164.0', '当前程序0.165.0', 1)
(N / name).write_text(t, encoding='utf8', newline='\n')

p = R / 'Planning/ROUND_165_REVIEW.md'
t = p.read_text('utf8')
t = t.replace('旧视频检查直接建立面板，未覆盖这一启动过程。', '旧视频检查直接建立面板，未覆盖这一启动过程。进一步确认动作创建时全局主窗口尚未赋值，已改为显式归属实际主窗口。')
t += '\n## 本次结果\n\nN1—N9的入口、当前对象、编辑、播放与保存衔接已按使用过程审视，具体结论和已有证据见[P2/native/personal/docs/ROUND_165_REVIEW.md](../P2/native/personal/docs/ROUND_165_REVIEW.md)。动态乐谱完整启动、旧菜单恢复、共用胶片入口、打开准备、视图往返和关闭已核对；0.165编译完成。说明整理了重复截图、实际入口和后续顺序。\n\n后续先按原安排补实体MIDI与代表性音乐听感，再讨论AI数据组织及专用工具。\n'
p.write_text(t, encoding='utf8', newline='\n')
p = R / 'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md'
t = p.read_text('utf8').replace('0.164原生谱表、声音、预览、换行、保存及两种容器已检查并安装', '0.165修复完整启动、工具入口、胶片动作及旧菜单恢复；原生谱行、声音、换行和两种容器的具体结果继续保留', 1)
t += '\n## 2026-11-08整轮重新审视\n\n动态乐谱发布入口遗漏已修正。按N1—N9使用过程重新核对，说明与执行要求同步整理；见[本轮审视](ROUND_165_REVIEW.md)。桌面操作集中用于必须实际确认的项目，已有有效结果继续沿用。\n'
p.write_text(t, encoding='utf8', newline='\n')

program = H / 'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
binary = program.read_bytes()
assert all(value in binary for value in (b'0.165.0', b'Kumo branch', b'Freddd13'))
(O / 'program-checks.json').write_text(json.dumps({'version': '0.165.0', 'sha256': hashlib.sha256(binary).hexdigest(), 'startup': 'startup-workspace.txt', 'review': 'personal/docs/ROUND_165_REVIEW.md'}, ensure_ascii=False, indent=2), encoding='utf8')
(O / 'files.json').write_text(json.dumps(files, indent=2), encoding='utf8')
print('Recorded the repaired startup workflow and complete round review.')
