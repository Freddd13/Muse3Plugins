from pathlib import Path
import csv,hashlib,io,json,shutil
R=Path(__file__).resolve().parents[1];N=R/'P2/native';H=R.parent/'muse3_dev/MuseScore';O=R/'P2/out/repair-164';manifest=O/'files.json';files=json.loads(manifest.read_text('utf8'))
names=['personal/VERSION','personal/USER_GUIDE.md','personal/CHANGELOG.md','personal/docs/source-map.tsv','personal/docs/REWORK_PROGRESS.md','personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md','personal/docs/SCORE_VIDEO_164_GUIDE.md','personal/docs/SCORE_VIDEO_164_CHECKS.md','personal/docs/VIDEO_ENCODER_164.md','personal/tools/install_score_video_tools.py','personal/docs/images/score-video-panel-164.png','personal/docs/images/score-video-workspace-164.png']
for name in names:
    if name not in files:files[name]=hashlib.sha256((H/name).read_bytes()).hexdigest() if (H/name).is_file() else None
(N/'personal/VERSION').write_bytes(b'0.164.0\n')
p=N/'personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md';t=p.read_text('utf8').replace('核对日期：2026-11-07。当前安装程序0.158.1，随包MCP客户端2.7.2，通信桥2.7.0。本轮声音与编辑修复沿用这些读谱接口。','核对日期：2026-11-08。当前程序0.164.0，随包MCP客户端2.7.2，通信桥2.7.0，共44项工具。当前工具覆盖读谱、原生谱图、建议、试听和编辑；多轨MIDI与动态视频的专用AI操作安排在后续接口扩展中。');p.write_bytes(t.encode('utf8'))
p=N/'personal/USER_GUIDE.md';t=p.read_text('utf8').replace('当前版本：**0.163.0','当前版本：**0.164.0',1)
if '| 用原生谱面制作' not in t:t=t.replace('|---|---|','|---|---|\n| 用原生谱面制作带声音或透明背景的视频 | [动态乐谱完整操作](docs/SCORE_VIDEO_164_GUIDE.md) |\n| 了解当前44项AI工具、数据和调用方法 | [AI连接完整实现报告](docs/AI_CONNECTION_IMPLEMENTATION_159.md) |',1)
p.write_bytes(t.encode('utf8'))
p=N/'personal/CHANGELOG.md';t=p.read_text('utf8')
if '## 0.164.0' not in t:t=t.replace('# 个人版本更新日志\n','# 个人版本更新日志\n\n## 0.164.0 — 2026-11-08\n\n- N8：后处理中的动态乐谱，原生两／三／四谱表、上谱表对齐、时间轴、换行和本行位置调整。\n- 乐谱或原曲声音、已有片段与内部对齐点、反复和停顿共用冻结的时间资料；预览与导出共用逐帧绘图。\n- H.264 MP4和透明ProRes4444 MOV；离线声音、有界供帧、取消和目标文件替换，附带核对版本的FFmpeg及许可。\n- 视频设置与摆放通过原生撤销随MSCZ保存；窗口可关闭、悬浮、全屏，工作视图分别恢复显隐。\n- 说明与检查见SCORE_VIDEO_164_GUIDE.md、SCORE_VIDEO_164_CHECKS.md。发布定位personal-v0.164.0。\n',1)
p.write_bytes(t.encode('utf8'))
p=N/'personal/docs/REWORK_PROGRESS.md';t=p.read_text('utf8')
if '## 2026-11-08：0.164' not in t:t=t.replace('# 当前进度与后续完整计划\n','# 当前进度与后续完整计划\n\n## 2026-11-08：0.164 动态乐谱与本轮收尾\n\n动态乐谱的谱行、声音、换行、保存与MP4／透明MOV已检查。正在更新程序目录。见[操作](SCORE_VIDEO_164_GUIDE.md)与[检查](SCORE_VIDEO_164_CHECKS.md)。\n\n| 编号 | 当前结果 |\n|---|---|\n| N1 | 0.159长按力度、P键盘、Home及倚音间距 |\n| N2 | 0.159混响CC91、SF2与逐乐器效果路由 |\n| N3 | 五项上游修复，57项提交报告 |\n| N4 | 0.160多轨MIDI、录制、对齐、保存及写谱草稿 |\n| N5 | 0.161实际演奏起音、松键与恢复 |\n| N6 | 0.162固定频谱块、整轨准备、键盘与倍频、MIDI对照 |\n| N7 | 0.163原曲谱面范围、分体播放、移位显隐及撤销 |\n| N8 | 0.164动态乐谱、谱表组合、时间与外观、原曲／乐谱声音、视频输出 |\n| N9 | [44项AI工具与流程](AI_CONNECTION_IMPLEMENTATION_159.md) |\n\n下一步按原安排补实体MIDI键盘及代表性音乐听感；AI结构改进在现有报告上继续讨论。自动音符候选、音频和弦、自由演奏转谱、完整雕版与后处理扩展保留在后续清单。本轮软件检查结果与这些后续构想分别记录。\n',1)
p.write_bytes(t.encode('utf8'))
rows=list(csv.reader(io.StringIO((N/'personal/docs/source-map.tsv').read_text('utf8')),delimiter='\t'))
for row in [
['动态乐谱资料','mscore/scorevideo/scorevideo.cpp','void ScoreVideoDocument::prepare(',0,'原生谱行、副本与分批图像准备','mtest/mscore/pluginhost/scorevideo_164_tests.inc'],
['动态乐谱时间','mscore/scorevideo/scorevideotimeline.cpp','void ScoreVideoDocument::rebuildTimeline(',0,'反复、原曲关联与手动换行','mtest/mscore/pluginhost/scorevideo_164_tests.inc'],
['动态乐谱画面','mscore/scorevideo/scorevideoframe.cpp','QImage scoreVideoFrame(',0,'统一对齐、透明、反相与光标高亮','mtest/mscore/pluginhost/scorevideo_164_tests.inc'],
['动态乐谱视频','mscore/scorevideo/scorevideoexport.cpp','void ScoreVideoExport::encode(',0,'后台编码、有限队列与取消','mtest/mscore/pluginhost/scorevideo_164_tests.inc'],
['动态乐谱面板','mscore/scorevideo/scorevideopanel.cpp','ScoreVideoPanel::ScoreVideoPanel(',0,'预览、试听、时间与位置编辑','mtest/mscore/pluginhost/scorevideo_164_tests.inc'],
['视频原曲声音','mscore/referenceaudio/mediaexport.cpp','void ReferenceAudioExport::render(',0,'有界离线解码、空隙与原子声音文件','mtest/mscore/spectrum/tst_spectrum.cpp']]:
    if not any(old and old[0]==row[0] for old in rows):rows.append(row)
for row in rows[1:]:
    path=N/row[1] if row[1] in files else H/row[1]
    if not path.is_file():path=N/row[1]
    hits=[i+1 for i,line in enumerate(path.read_text('utf8').splitlines()) if row[2] in line]
    if not hits:raise ValueError('Missing source symbol '+str(row))
    row[3]=str(min(hits,key=lambda i:abs(i-int(row[3]))))
buffer=io.StringIO(newline='');csv.writer(buffer,delimiter='\t',lineterminator='\n').writerows(rows);(N/'personal/docs/source-map.tsv').write_bytes(buffer.getvalue().encode('utf8'))
for source,target in [('video-panel-164.png','score-video-panel-164.png'),('video-workspace-164.png','score-video-workspace-164.png')]:
    if (O/source).is_file():shutil.copy2(O/source,N/'personal/docs/images'/target)
manifest.write_text(json.dumps(files,indent=2),encoding='utf8')
