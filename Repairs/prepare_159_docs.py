"""Maintain this batch's guides and progress without replacing user additions."""
from pathlib import Path
import csv
import io
import json
import subprocess
import shutil

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/"P2/native"
HOST=ROOT.parent/"muse3_dev/MuseScore"

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf8",newline="\n") as stream:stream.write(text)

guide="""
## 0.159：长按力度、Home、倚音间距与混响

按住你设置的力度快捷键（例如Alt+Q）可持续查看数值；在演奏编辑器“操作设置…”中可设置松开后的保留时间。普通播放Home回全谱开头，选段试听回本段开头。

选中倚音后，在检视器调整“倚音间额外间距”和“与主音额外间距”，保存、撤销及多选继续使用原生操作。

混音器的“混响”控制乐器发送量。按F11，在效果A或B选择Zita1，再调整发送量和整体混合比例。混响滑块右键可打开设置。

完整操作、AI连接和上游报告：

- [本轮操作说明](docs/PLAYBACK_159_GUIDE.md)
- [AI连接的全部44项工具及实际流程](docs/AI_CONNECTION_IMPLEMENTATION_159.md)
- [个人开发以来的57项上游更新](docs/UPSTREAM_159_REPORT.md)
"""
for path in (NATIVE/"personal/USER_GUIDE.md",HOST/"personal/USER_GUIDE.md"):
    text=path.read_text("utf8")
    text=text.replace("**0.158.1 · Kumo branch / Freddd13**","**0.159.0 · Kumo branch / Freddd13**",1)
    if "personal-v0.159.0" not in text:
        text=text.rstrip()+"\n\n本轮提交定位：`personal-v0.159.0`。\n"
    if "## 0.159：长按力度" not in text:write(path,text.rstrip()+"\n"+guide+"\n")
    else:write(path,text)

path=NATIVE/"personal/CHANGELOG.md"
text=path.read_text("utf8")
entry="""## 0.159.0 — 2026-11-07（正在检查）

- N1：长按力度忽略自动重复松键，支持松开后延时恢复；快捷键和显示默认保持。钢琴播放音高改由无锁数值状态交给GUI刷新，鼠标按键失焦时归还。
- N1：普通、选段、联合播放Home按所属会话定位，重建选段试听事件；修正记谱tick与展开反复tick的混用。
- N1：倚音间距与主音距离使用独立属性，旧谱默认0；支持原生撤销、链接及保存。
- N2：接通SF2 CC91发送、Zita1与主输出；逐乐器SF2效果路由携带发送及延迟补偿。未启用混响时提示F11入口，混音器尺寸保持。
- N2：绝对SF2路径优先读取指定文件，原名称查找继续保留。真实Kawai SF2初检确认发送量改变输出。
- N3：适配上游130b54342447、5ee61659924d、e1383fb989da、fceb31067e97与564998bd4c8e的音乐／稳定性修复，保留个人踏板解释。
- 说明见PLAYBACK_159_GUIDE.md，AI完整报告与57项上游报告一并维护。后续N4—N8多轨、卷帘、频谱、关联及视频按固定清单继续。
- 发布检查及安装仍在进行；开始提交8f81421a5cc965dbb32a81fcecf39d626b5610ff，提交定位personal-v0.159.0。

"""
if "## 0.159.0" not in text:write(path,text.replace("# 个人版本更新日志\n\n","# 个人版本更新日志\n\n"+entry,1))

path=NATIVE/"personal/docs/REWORK_PROGRESS.md"
text=path.read_text("utf8")
entry="""## 2026-11-07：本轮操作、混响、多轨与视频

安装版仍为0.158.1；0.159.0正在检查。当前按已批准顺序处理N1长按／Home／P键盘／倚音、N2混响和N3上游五项修复。Windows首轮交互及真实Kawai发送检查已通过，继续逐乐器效果、保存、已有播放及上游导出回查。

| 顺序 | 当前工作 |
|---|---|
| N1/N2 | 已编译并完成首轮实际操作及声音数据检查，继续收尾 |
| N3 | 已适配五项上游改动，正在编译和回查 |
| N4 | 接着实现MIDI轨道、随谱保存、导入删除及原曲对齐 |
| N5 | 卷帘演奏起止、临时MIDI、采用到谱 |
| N6 | 频谱键盘／谐波、设置及固定块缓存 |
| N7 | 原曲范围、分体播放、可移动谱面控件 |
| N8 | 动态乐谱预览、时间调整、MP4与透明MOV |
| N9 | [当前AI连接实现与44项工具](AI_CONNECTION_IMPLEMENTATION_159.md)已整理；后续结构另行讨论 |

[本轮操作](PLAYBACK_159_GUIDE.md) · [上游完整报告](UPSTREAM_159_REPORT.md)。原有实体键盘与真实音乐连续听感仍保留在后续检查中。以下历史记录继续保留。

"""
if "## 2026-11-07：本轮操作" not in text:write(path,text.replace("# 当前进度与后续完整计划\n\n","# 当前进度与后续完整计划\n\n"+entry,1))

path=NATIVE/"personal/docs/source-map.tsv"
if not path.exists():write(path,(HOST/"personal/docs/source-map.tsv").read_text("utf8"))
committed=subprocess.run(["git","show","HEAD:personal/docs/source-map.tsv"],cwd=HOST,capture_output=True,check=True).stdout.decode("utf8")
rows=list(csv.DictReader(io.StringIO(committed),delimiter="\t"))
additions=[
    ("混响发送","effects/zita1/zita.cpp","void ZitaReverb::processWithSend","分别处理干声和逐乐器发送","nativeReverbSend159"),
    ("混响发送","audio/midi/msynthesizer.cpp","void MasterSynthesizer::process","保留发送缓冲并执行原生效果","kawaiReverbSend159"),
    ("键盘播放","mscore/seq.cpp","void Seq::clearKeyboardPitches","无锁音高状态和界面线程刷新","keyboardPointer159"),
    ("长按力度","mscore/performanceeditor/performanceux.cpp","bool PerformanceEditor::peekKeyEvent","物理松键及延后恢复","velocityPeekHold159"),
    ("试听定位","mscore/workflow/playbackpreview.cpp","bool rewindPlaybackPreview","按选段重建试听起点","homePreview159"),
    ("倚音间距","libmscore/chord.cpp","bool Chord::setProperty","倚音间距及主音距离保存和布局","graceSpacing159"),
]
for topic,name,symbol,role,tests in additions:
    tests="mtest/mscore/performanceeditor/interaction_159_tests.inc" if tests=="homePreview159" else "mtest/mscore/pluginhost/playback_159_tests.inc"
    if not any(row["path"]==name and row["symbol"]==symbol for row in rows):
        rows.append(dict(topic=topic,path=name,symbol=symbol,line="1",role=role,tests=tests))
    else:
        for row in rows:
            if row["path"]==name and row["symbol"]==symbol:row["tests"]=tests
affected=set(json.loads((ROOT/"P2/out/repair-159-applied.json").read_text("utf8")))|{item[1] for item in additions}
for row in rows:
    if row["path"] not in affected:continue
    source=NATIVE/row["path"]
    if not source.exists():source=HOST/row["path"]
    if not source.is_file():continue
    lines=source.read_text("utf8",errors="replace").splitlines()
    matches=[i+1 for i,line in enumerate(lines) if row["symbol"] in line]
    if matches:row["line"]=str(min(matches,key=lambda n:abs(n-int(row.get("line") or 1))))
output=io.StringIO(newline="")
writer=csv.DictWriter(output,fieldnames=["topic","path","symbol","line","role","tests"],delimiter="\t",lineterminator="\n")
writer.writeheader();writer.writerows(rows);write(path,output.getvalue())
print("Updated guides, progress and source map")
picture=ROOT/"P2/out/repair-159/peek-settings-159.png"
if picture.exists():
    destination=NATIVE/"personal/docs/images/peek-settings-159.png"
    destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(str(picture),str(destination))
