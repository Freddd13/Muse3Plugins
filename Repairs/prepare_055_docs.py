from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
stage('personal/VERSION','0.55.0\n')
s=(H/'personal/USER_GUIDE.md').read_text(encoding='utf8').replace('当前个人版本：**0.54.0**','当前个人版本：**0.55.0**');s=s.replace('## 打开功能','## 0.55 的和弦与编配检查\n\n和弦范围和文字位置可用 Ctrl+Z 撤销，并随乐谱保存。编配检查增加问题筛选和直接返回全谱的范围选择，低音排列按各音程的参考音区提示。完整例子见[和弦显示与编配检查](docs/REPAIR_055_GUIDE.md)。\n\n## 打开功能',1);stage('personal/USER_GUIDE.md',s)
s=(H/'personal/CHANGELOG.md').read_text(encoding='utf8').replace('# 个人版本更新日志','# 个人版本更新日志\n\n## 0.55.0 — 2026-10-17\n\n- 和弦根音、斜杠、低音与级数对齐；详情卡片保持稳定高度，实际音高可折叠。手动低音同步更新级数转位。\n- 人工和弦、范围、位置通过原生撤销保存到标准元数据；末端手柄使用上一小节的结束边界。\n- 编配检查提供全谱、选区、保留范围与分类、程度筛选，浮动说明优先避开目标小节。\n- 低音程按好和弦参考表检查，明确大跨度在其它分手尚未确定时仍继续报告；49 项规则检查通过。\n- 操作：personal/docs/REPAIR_055_GUIDE.md；提交定位：personal-v0.55.0。',1);stage('personal/CHANGELOG.md',s)
stage('personal/docs/REPAIR_055_GUIDE.md',(R/'docs/REPAIR_055_GUIDE.md').read_text(encoding='utf8'))
s=(H/'personal/docs/source-map.tsv').read_text(encoding='utf8')+'谱内工作流记录\tmscore/workflow/workflowdocument.cpp\tScoreObserver::setWorkflowData\t14\t标准元数据保存与原生撤销\tnativeWorkflowDocumentAndTypography\n临时和弦排版\tmscore/workflow/harmonytypography.h\talignTemporaryHarmonyBass\t7\t面板和谱面的斜杠低音对齐\tnativeWorkflowDocumentAndTypography\n低音程参考\tshare/plugins/ArrangementAssistant/Rules.js\tlowVoicing\t9\t实际音程与参考低端音\ttest-rules.cjs\n';stage('personal/docs/source-map.tsv',s)
