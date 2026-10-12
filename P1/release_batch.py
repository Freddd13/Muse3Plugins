# coding: utf-8
"""Append release records without staging pre-existing user documentation edits."""
from pathlib import Path
import subprocess,sys
HOST=Path(r"E:\programming\funcodes\muse3_dev\MuseScore")
stage,version=sys.argv[1:3]
details={
"D":("MIDI范围、声部及旋律保护","MIDI导出裁剪设置增加文件顺序小节范围、通用voice选择/保护、最高起音线保护，参数记忆。对比窗口增加本谱具体谱表/voice裁剪/保护，会话内选择独立于通用预设；原谱小节/谱表/voice来源列及保留原因。实际展开导出事件保留物理谱位，重复/暂停/起音偏移仍沿用原转换；来源不确定保留。范围无效报告，不静默裁剪其它小节。仍只移动允许的note-off，默认导出/QML/命令行不隐式启用；固定种子微随机和P0踏板/手工/重触保护保留。修复工作区副本重开绕过可选旧谱样式迁移，保证完整副本配置一致。","P1宿主13/13，含展开反复源位、范围/具体voice/旋律保护、真实设置记忆和对比窗口及6000音完整表达分页。完整原功能回归见本批交付记录。真实演奏/人工声卡听感及大谱长期压力仍待素材，试听为GUI heartbeat停止；其它平台未验证。"),
"C":("多方案试写工作区","启用独立Arrangement Variants插件：选谱段、新建组，完整MSCZ只读基准和可编辑A副本；原生标签页切换、复制/命名、反复次数和同处上下文试听。长度/拍号/段外内容及跨段spanner按小节分页比较，变化取消同条件标识。保存当前方案生成新版本文件后原子更新JSON清单，旧版本保留，其它打开方案须逐个保存；工作区恢复含摘要验证，缺失/修改文件报告。成果另存完整所选副本，无局部合并。基准禁止覆写/应用，原谱隔离。沿用0.29副本、导航及GUI heartbeat停止，保留同步克隆/布局耗时边界。","宿主10/10含基准只读/禁止应用与覆盖、摘要拒绝、克隆指纹一致/编辑变化、真实方案面板新建/保存/复制。纯值段外/拍号/长度/谱表比较，侧顶QML。真实设备听感及大谱压力待实材；未实现同窗口/局部合并。"),
"B2":("表达保护写回、独立副本与Tap写谱","Performance Expression：力度与Rubato分别启用、强度默认50%，设备校准和推算伴奏来源标识。可靠/人工确认对应才写入，保护手工力度/事件/装饰及已有速度记号/曲线。差异和原/候选曲线，完整MSCZ副本试听及返回原谱。停播/渲染结束后旧值预检、一次撤销和读回，异常回滚。Rubato默认保留段长/边界，有限隐藏速度点；无法满足段长拒绝应用。Tap下拉新增写入指定位置，新建可见速度；已有记号必须选中，保留拍单位/文字；相对/a tempo/曲线交原入口。副本含资源/分谱/链接，原子写入且原谱路径/dirty/撤销栈不变；克隆同步并报告耗时。试听含前一小节、入段tie/踏板及反复位置；段末GUI heartbeat停止，非采样精度；无驱动可查看副本并返回。","宿主9/9：一次Undo/Redo、旧值/会话/保护、Tap可见/保护、音频/图片/分谱/事件副本、预览返回及段长拒绝。JS段长/独立播放倍率/6-8细分/三连音；QML侧顶。真实演奏/声卡听感仍待素材。"),
"B1":("演奏 MIDI 容错对应","启用独立 Performance Expression 插件；选谱段后导入 MIDI，按谱／任意音高音序、旋律／voice／声部组选择，演奏起止秒和反复次数。自动对齐保留漏／多／错音；人工连接、取消、锚点，重复音序待确认。工作区保存原始 MIDI 的 SHA256副本、输入范围及人工校正，恢复后重新读取谱面。原生只读分页补力度、速度保护、倚音及反复资料；隔离JSworker分段DP，修改锚点复用未变区间。首版固定band最大384，超出需设锚点。隐藏／改谱取消；缓存64页。B2写回及试听随后交付。","MIDI值6/6，合成真值规则／音序漏敲恢复／同音／tie／反复通过；原生5/5含真实面板启动和悬浮；QML侧顶。真实演奏质量与大曲长期压力待素材验收。修正ReferencePlayer悬浮按钮调用宿主接口；依赖上游Connections旧语法警告保留。"),
}
title,operations,verification=details[stage]
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HOST).decode().strip()
guide="\n## "+version+"："+title+"（P1 "+stage+"）\n\n"+operations+"\n\n验证："+verification+"\n\n提交定位 personal-v"+version+"，Windows x64已验证，其它平台未验证。\n"
p=HOST/"personal/USER_GUIDE.md";s=p.read_text(encoding="utf8")
if "## "+version+"：" not in s:p.write_bytes((s+guide).encode("utf8"))
p=HOST/"personal/CHANGELOG.md";s=p.read_text(encoding="utf8")
entry="## "+version+" — 2026-10-12\n\n- P1 "+stage+"："+title+"。\n- "+operations+"\n- 验证："+verification+"\n- Git父提交 "+head+"；定位personal-v"+version+"；主题P1 "+stage+" 独立提交。品牌统一VERSION，保留并行AGENTS／USER_GUIDE增量。\n\n"
if "## "+version+" —" not in s:
 at=s.index("## ");p.write_bytes((s[:at]+entry+s[at:]).encode("utf8"))
(HOST/"personal/VERSION").write_bytes((version+"\n").encode())
p=HOST/"personal/docs/README.md";s=p.read_text(encoding="utf8")
line="\nP1 "+stage+"："+title+"；薄宿主接口在mscore/workflow，纯规则／工作区在share/plugins/PerformanceExpression。测试mtest/mscore/p1native及插件P1/tests。\n"
if line not in s:p.write_bytes((s+line).encode("utf8"))
p=HOST/"personal/docs/source-map.tsv";s=p.read_text(encoding="utf8")
sources=[("mscore/workflow/midiinput.cpp","QVariantMap readPerformanceMidi"),("mscore/workflow/scoreworkflow.cpp","ScoreObserver::performanceRange"),("mscore/workflow/scoreworkflow.cpp","ScoreObserver::workflowInfo")]
if stage!="B1":sources += [("mscore/workflow/workflowexpression.cpp","ScoreObserver::applyExpression"),("mscore/workflow/workflowexpression.cpp","ScoreObserver::copyWorkflowScore"),("mscore/workflow/tapwrite.cpp","showTapWriteDialog")]
if stage in ("C","D"):sources += [("mscore/workflow/workflowvariants.cpp","ScoreObserver::workflowFingerprint")]
if stage=="D":sources += [("audio/exports/midigate.h","QVector<MidiGateNote> process"),("mscore/midicrop/midicroppanel.cpp","MidiCropPanel::voiceSelection"),("mscore/workflow/scoreworkflow.cpp","ScoreObserver::workflowStatus")]
for source,symbol in sources:
 rows=s.splitlines();rows=[r for r in rows if not (source+"\t"+symbol in r)];text=(HOST/source).read_text(encoding="utf8")
 line=next(i for i,l in enumerate(text.splitlines(),1) if symbol in l)
 category="MIDI导出" if "midigate" in source or "midicrop" in source else "工作流"
 description="范围／声部／旋律保护的导出副本" if category=="MIDI导出" else "只读范围与值数据" if any(k in symbol for k in ("performanceRange","workflowInfo","workflowStatus","Fingerprint","readPerformanceMidi")) else "隔离副本／受保护写入"
 rows.append(category+"\t"+source+"\t"+symbol+"\t"+str(line)+"\t"+description+"\tmtest/mscore/p1native")
 s="\n".join(rows)+"\n"
p.write_bytes(s.encode("utf8"))
Path(__file__).with_name("out").joinpath("guide-"+stage+".txt").write_bytes(guide.encode("utf8"))
print(stage,version,"records prepared; no user edits staged.")
