from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
stage('personal/VERSION','0.54.0\n')
s=(H/'personal/USER_GUIDE.md').read_text(encoding='utf8').replace('当前个人版本：**0.53.0**','当前个人版本：**0.54.0**')
s=s.replace('## 打开功能','## 0.54 的记谱操作\n\n自由圆滑线可分别选择两端位置；分手折线的文字可独立拖动和设置字体。速度面板会合并本项目重复生成的入口。操作例子见[圆滑线、渐慢线与分手记号](docs/REPAIR_054_GUIDE.md)。\n\n## 打开功能',1);stage('personal/USER_GUIDE.md',s)
s=(H/'personal/CHANGELOG.md').read_text(encoding='utf8').replace('# 个人版本更新日志','# 个人版本更新日志\n\n## 0.54.0 — 2026-10-17\n\n- 自由圆滑线增加独立的起点与终点方向；跨谱表收集实际谱表的障碍，显示控制点与可见曲线相符。\n- 渐慢线在小节结束和谱行末尾正确取得上一小节边界；重复生成的速度入口在工作区载入时合并。\n- 四方向分手折线共用新默认长度，结束记号置于音后。手部文字跟随表情文字，提供独立拖动、字体、字号与自动放置。\n- 操作：personal/docs/REPAIR_054_GUIDE.md；提交定位：personal-v0.54.0。',1);stage('personal/CHANGELOG.md',s)
stage('personal/docs/REPAIR_054_GUIDE.md',(R/'docs/REPAIR_054_GUIDE.md').read_text(encoding='utf8'))
s=(H/'personal/docs/source-map.tsv').read_text(encoding='utf8')+'自由圆滑线端点\tlibmscore/freeslur.cpp\tSlurSegment::computeFreeBezier\t175\t独立端点与跨谱表障碍\trepair054EndpointSidesAndHandText\n分手文字\tlibmscore/symbol.cpp\tSymbol::handFont\t100\t表情文字样式与第四拖动点\trepair054EndpointSidesAndHandText\n';stage('personal/docs/source-map.tsv',s)
