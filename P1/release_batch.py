"""Append release records without staging pre-existing user documentation edits."""
from pathlib import Path
import subprocess,sys
HOST=Path(r"E:\programming\funcodes\muse3_dev\MuseScore")
stage,version=sys.argv[1:3]
details={
"B1":("演奏 MIDI 容错对应","启用独立 Performance Expression 插件；选谱段后导入 MIDI，按谱／任意音高音序、旋律／voice／声部组选择，演奏起止秒和反复次数。自动对齐保留漏／多／错音；人工连接、取消、锚点，重复音序待确认。工作区保存原始 MIDI 的 SHA256副本、输入范围及人工校正，恢复后重新读取谱面。原生只读分页补力度、速度保护、倚音及反复资料；隔离JSworker分段DP，修改锚点复用未变区间。首版固定band最大384，超出需设锚点。隐藏／改谱取消；缓存64页。B2写回及试听随后交付。","MIDI值6/6，合成真值规则／音序漏敲恢复／同音／tie／反复通过；原生5/5含真实面板启动和悬浮；QML侧顶。真实演奏质量与大曲长期压力待素材验收。修正ReferencePlayer悬浮按钮调用宿主接口；依赖上游Connections旧语法警告保留。"),
}
title,operations,verification=details[stage]
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=HOST).decode().strip()
guide="\n## "+version+"："+title+"（P1 "+stage+"）\n\n"+operations+"\n\n验证："+verification+"\n\n提交定位 personal-v"+version+"，Windows x64已验证，其它平台未验证。\n"
p=HOST/"personal/USER_GUIDE.md";s=p.read_text(encoding="utf8")
if "## "+version+"：" not in s:p.write_bytes((s+guide).encode("utf8"))
p=HOST/"personal/CHANGELOG.md";s=p.read_text(encoding="utf8")
entry="## "+version+" — 2026-10-11\n\n- P1 "+stage+"："+title+"。\n- "+operations+"\n- 验证："+verification+"\n- Git父提交 "+head+"；定位personal-v"+version+"；主题feat(expression): add tolerant read-only performance alignment。品牌统一VERSION，保留并行AGENTS／USER_GUIDE增量。\n\n"
if "## "+version+" —" not in s:
 at=s.index("## ");p.write_bytes((s[:at]+entry+s[at:]).encode("utf8"))
(HOST/"personal/VERSION").write_bytes((version+"\n").encode())
p=HOST/"personal/docs/README.md";s=p.read_text(encoding="utf8")
line="\nP1 "+stage+"："+title+"；薄宿主接口在mscore/workflow，纯规则／工作区在share/plugins/PerformanceExpression。测试mtest/mscore/p1native及插件P1/tests。\n"
if line not in s:p.write_bytes((s+line).encode("utf8"))
p=HOST/"personal/docs/source-map.tsv";s=p.read_text(encoding="utf8")
for source,symbol in [("mscore/workflow/midiinput.cpp","QVariantMap readPerformanceMidi"),("mscore/workflow/scoreworkflow.cpp","ScoreObserver::performanceRange"),("mscore/workflow/scoreworkflow.cpp","ScoreObserver::workflowInfo")]:
 rows=s.splitlines();rows=[r for r in rows if not (source+"\t"+symbol in r)];text=(HOST/source).read_text(encoding="utf8")
 line=next(i for i,l in enumerate(text.splitlines(),1) if symbol in l)
 rows.append("演奏表达\t"+source+"\t"+symbol+"\t"+str(line)+"\t只读工作流值桥\tmtest/mscore/p1native")
 s="\n".join(rows)+"\n"
p.write_bytes(s.encode("utf8"))
Path(__file__).with_name("out").joinpath("guide-"+stage+".txt").write_bytes(guide.encode("utf8"))
print(stage,version,"records prepared; no user edits staged.")
