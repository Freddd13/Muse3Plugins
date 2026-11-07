from pathlib import Path
import json,re,shutil
R=Path(__file__).resolve().parents[1];N=R/'P2/native';O=R/'P2/out/repair-164'
for name in ('pluginhost-scoreVideoPictures164.txt','spectrum-checks.txt'):
    if not re.search(r'Totals: \d+ passed, 0 failed, 0 skipped',(O/name).read_text('utf8',errors='replace')):raise ValueError('Incomplete checks '+name)
files=json.loads((O/'video-files.json').read_text('utf8'));assert len(files)>=6
p=N/'personal/docs/SCORE_VIDEO_164_CHECKS.md';t=p.read_text('utf8');t=t.replace('最终编码、声音与普通版兼容检查结果在本批发布前补充。实体MIDI键盘和代表性音乐的人工听感按原安排继续核对。','''## 最终结果

- 动态乐谱的谱表、预览、时间、保存和导出，以及原曲窗口的连续操作全部通过。频谱与声音处理回查通过。旧谱谱例先保留原样式，再继续窗口操作；原曲设置按实际可见条目点击。
- 普通短片80帧／8秒，关联原曲155帧／15.5秒；两者声音与画面时长一致。默认1080p／30fps已实际编码240帧。十分钟视频600帧／1fps，声音与画面均为600秒，编码约13.5秒。
- 透明MOV为ProRes4444、yuva444p12le，解码后同时存在完全透明、不透明及半透明边缘。原生与原曲声音均检出实际非零输出。
- 关闭原资料后，已经开始的视频仍使用独立的声音和画面材料完成输出；取消保留已有同名视频。
- 三谱表图像已修正未选中谱表的括号、小节线和乐器名称位置。已查看实际图片及正常、小窗口、工作视图截图。
- 官方MuseScore3.6.2打开并重存20音测试谱，音符、时值、指法、谱表移动、连线及kumo.scoreVideo元数据保持一致。
- 最终程序普通MIDI与0.163逐字节一致，原谱与普通版重存文件导出的MIDI一致，PDF正常。

当前准备更新原安装目录。实体MIDI键盘和代表性音乐的人工听感按原安排继续核对。''');p.write_bytes(t.encode('utf8'))
for source,target in [('video-panel-164.png','score-video-panel-164.png'),('video-workspace-164.png','score-video-workspace-164.png')]:shutil.copy2(O/source,N/'personal/docs/images'/target)
p=R/'Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md';t=p.read_text('utf8').replace('| N8 | 动态乐谱预览、换行时间、MP4及透明MOV | 待实施 |','| N8 | 动态乐谱预览、换行时间、MP4及透明MOV | 0.164原生谱表、声音、预览、换行、保存及两种容器已检查，正在更新程序目录 |');p.write_bytes(t.encode('utf8'))
p=R/'Planning/SCORE_VIDEO_164_DESIGN.md';t=p.read_text('utf8');at=t.find('## 尚待实现')
if at>=0:t=t[:at]+'''## 当前结果

原生资料、分批谱行、共同画面合成、工作视图、预览和编码已完成；普通与透明视频、原曲关联、长视频、保存撤销及普通版读取已检查。原生声音准备持有自己的副本，编码使用冻结的图片与数值。发布说明见SCORE_VIDEO_164_GUIDE.md与SCORE_VIDEO_164_CHECKS.md，当前准备安装0.164。
'''
p.write_bytes(t.encode('utf8'))
