# coding: utf-8
from pathlib import Path
import subprocess,shutil
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
report='''# 多音频与编辑器对应检查

2026-10-13，个人版0.41.0，Windows x64，Qt5.15.2。测试材料是独立生成的音频和测试谱，未改用户乐谱、OneDrive官谱或声音设备设置。

## 已完成

- 多条WAV／MP3／FLAC通过独立可选模块处理。每轨有固定缓冲，后台解码、保调变速和混音；联合播放复用乐谱声音输出。模块缺失仍保留普通乐谱和原有插件。
- 音轨选择、参与／静音／独听、多对多片段、内部对应点、三种播放方式、只播音轨、整组循环、JSON恢复。旧单曲项目仍可读。
- 编辑器共用时间尺，显示参考片段、对应连线、漏弹／多弹及力度／速度对比。选音、确认、连接和解除对应交给共同数据；写谱仍经过原来的保护检查。
- 原版与候选可带同一组参考音频试听。分谱副本仍打开对应分谱；返回后原谱路径、内容和撤销记录保持。

## 检查结果

- 音频11项通过，包括固定环形缓冲、8轨共同输出、20次快速取消、预备起音、跳转停止、缺失文件／重叠片段、连续变速、真实声音设备8轨静音播放和独立整组循环。
- 合成440Hz测试音连续采用75%、100%、125%速度后，测得440.377Hz；时长1.96667秒，符合所给片段和速度的目标。
- 8轨固定PCM缓冲9,437,184字节，变速处理器、线程和波形数据另外计入。测试中准备约66–79ms；1秒音频的输出回调累计约0.1–0.2ms，单次最长观测约40微秒。此测量不包括后台解码，也不是所有音频／设备的承诺。
- 实际窗口22项通过，包括原功能、三种播放计划、精确选音、速度视图、过期结果拒绝、多轨保存恢复及分谱返回。
- 宽窗、侧栏和顶部截图单独检查，不以函数返回值代替实际显示。

## 仍需说明

联合循环释放音符／踏板后重新进入并准备音频，因此当前不保证两次之间无间隔。单曲和独立整组循环保持连续音频输出。播放时先停止，再改变轨道参与状态、音量、片段和速度，避免界面显示已改、声音却仍使用预先准备的数据。

声音设备测试保持静音；测试音验证音高和时长。钢琴、原曲瞬态和不同声源的主观听感仍应由用户用代表性片段确认。Windows以外的平台未在本次机器上运行。
'''
(HOST/'personal/docs/REFERENCE_WORKFLOW_VALIDATION.md').write_bytes(report.encode('utf8'))
parent=subprocess.check_output(['git','rev-parse','--short','HEAD'],cwd=HOST).decode().strip()
entry=f'''## 0.41.0 — 2026-10-13

- 原曲参考支持多条音轨、重叠源片段和多对多谱段关联；三种联合播放、仅音频合奏、参与／静音／独听、保存恢复及旧项目兼容。菜单动作可设快捷键，编辑器复用同一菜单动作。
- 独立媒体模块固定缓冲、专用后台线程和连续保调变速；普通乐谱未启用时没有媒体任务。联合输出和临时速度在独立工作流桥中，结束／换谱／异常时停止，不写入谱内速度。
- 编辑器增加参考音轨、可点击对应、漏弹／多弹、原值／候选力度和速度视图。确认／连接／解除有反馈，旧结果不能直接改新内容；试听使用独立副本，支持分谱返回与相同参考音频。
- 用户说明按实际按钮补齐使用、保存、限制和恢复。父提交{parent}，提交定位personal-v0.41.0；测试与测量见personal/docs/REFERENCE_WORKFLOW_VALIDATION.md。

'''
p=HOST/'personal/CHANGELOG.md';text=p.read_text(encoding='utf8');at=text.index('## 0.40.0');
if '## 0.41.0' not in text:p.write_bytes((text[:at]+entry+text[at:]).encode('utf8'))
rows=[('联合音频输出','mscore/workflow/referencebus.cpp','void mixReferenceAudio(', '准备好的音频和临时时间对应'),('多音轨媒体','mscore/referenceaudio/mediaproject.cpp','QVariantMap ReferenceMediaProject::start(', '固定缓冲、后台处理与整体播放'),('连续保调','mscore/referenceaudio/audioreader.cpp','bool streamSequence(', '连续片段共用处理器，不在内部对应点反复淡入'),('联合播放','mscore/workflow/referenceworkflow.cpp','QVariantMap ScoreObserver::referencePlan(', '三种时间对应、反复出现和进入前文'),('编辑器对应','mscore/performanceeditor/workflowlanes.cpp','void WorkflowLanes::paintEvent(', '可见音轨、对应与数值对比'),('共同项目','mscore/workflow/workflowcontext.h','class WorkflowContext', '乐谱归属、结果更新和操作反馈')]
p=HOST/'personal/docs/source-map.tsv';text=p.read_text(encoding='utf8');
for topic,path,symbol,role in rows:
 lines=(HOST/path).read_text(encoding='utf8').splitlines();line=next(i+1 for i,value in enumerate(lines) if symbol in value)
 if '\t'+path+'\t'+symbol+'\t' not in text:text+='\t'.join([topic,path,symbol,str(line),role,'mtest/mscore/p1native; Repairs/tests/tst_referenceproject.cpp'])+'\n'
p.write_bytes(text.encode('utf8'))
for source,destination in [('reference-multi-041.png','reference-041.png'),('editor-correspondence-041.png','expression-041.png')]:
 src=ROOT.parent/'P1/out/final-regression'/source
 if not src.exists():raise RuntimeError('缺少实际操作截图：'+str(src))
 shutil.copy2(src,HOST/'personal/docs/images'/destination)
print('用户说明对应的截图、开发日志和源码索引已整理。')
