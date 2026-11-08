"""Keep the review, instructions and actual encoded-frame example together."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-166'
files = json.loads((O / 'release-files.json').read_text('utf8'))
for name in ('native-video-review.txt', 'continuous-workflows.txt'):
    log = (O / name).read_text('utf8', errors='replace')
    assert 'FAIL!' not in log and '0 failed' in log, name
comparison = json.loads((O / 'native-video-comparison.json').read_text('utf8'))
assert all(p['sourceDifference'] == 0 for p in comparison['pictures'])
assert json.loads((O/'ai-image-comparison.json').read_text('utf8'))['difference'] < .002

image = 'personal/docs/images/score-video-output-166.png'
encoder = H / 'msvc.install_repair_current_x64/bin/tools/video/ffmpeg.exe'
subprocess.run([str(encoder), '-hide_banner', '-loglevel', 'error', '-y', '-ss', '1',
                '-i', str(O/'default-1080-164.mp4'), '-frames:v', '1', str(N/image)], check=True)
shutil.copy2(N / image, H / image)
files.append(image)
for base in (N, H):
    p = base / 'personal/docs/SCORE_VIDEO_164_GUIDE.md'
    text = p.read_text('utf8').replace('![动态乐谱预览](images/score-video-panel-164.png)',
        '![动态乐谱预览](images/score-video-panel-164.png)\n\n下面是0.166实际导出的1080p视频画面，使用独立示例谱：\n\n![视频导出画面](images/score-video-output-166.png)', 1)
    p.write_text(text, encoding='utf8', newline='\n')
    p = base / 'personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md'
    text = p.read_text('utf8').replace('当前程序0.165.0', '当前程序0.166.0', 1)
    anchor = '当前取图需要暂停播放。'
    text = text.replace(anchor, anchor+'0.166修正了原生谱图的设备分辨率，文字和音乐符号按原谱比例显示。', 1)
    p.write_text(text, encoding='utf8', newline='\n')
files.append('personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md')
program = H / 'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe'
binary = program.read_bytes()
assert all(marker in binary for marker in (b'0.166.0', b'Kumo branch', b'Freddd13'))
(O / 'program-checks.json').write_text(json.dumps({'version': '0.166.0',
    'sha256': hashlib.sha256(binary).hexdigest(), 'nativeComparison': 'native-video-comparison.json',
    'workflows': 'continuous-workflows.txt'}, indent=2), encoding='utf8')
(O / 'release-files.json').write_text(json.dumps(files, indent=2), encoding='utf8')
p = R / 'Planning/ROUND_166_REVIEW.md'
text = p.read_text('utf8')
text += '''
## 本次结果

视频文字、音乐符号的分辨率与各行统一缩放已修正；AI原生图片一并修正。真实谱第一行、中间三谱表及末行的原生输出与视频谱行逐像素一致。最终1080p画面已查看，实际MP4和透明MOV已生成。

N1—N9按当前对象、编辑、试听、采用、保存的顺序完成审视；重新操作了MIDI轨编辑采用、演奏起止、频谱定位和空格、原曲多片段停止，以及视频输出。详细结果与后续顺序见[0.166记录](../P2/native/personal/docs/ROUND_166_REVIEW.md)。本轮沿用已有布局、颜色和设置。
'''
p.write_text(text, encoding='utf8', newline='\n')
p = R / 'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md'
text = p.read_text('utf8').replace('0.165修复完整启动、工具入口、胶片动作及旧菜单恢复；原生谱行、声音、换行和两种容器的具体结果继续保留',
    '0.166修正原生文字尺寸及统一缩放；入口、真实钢琴谱对照、时间与实际MP4／透明MOV已核对', 1)
text += '\n## 0.166继续返工\n\n修复谱面输出的实际比例，继续审视N1—N9；具体结果见[整轮记录](../P2/native/personal/docs/ROUND_166_REVIEW.md)。\n'
p.write_text(text, encoding='utf8', newline='\n')
print('Recorded actual score fidelity, continuous workflows and encoded-frame example.')
