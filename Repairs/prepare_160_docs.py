"""Maintain the guide, progress and source index for the MIDI track delivery."""
from pathlib import Path
import shutil
import csv
import io

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "P2/native"


def write(path, text):
    with path.open("w", encoding="utf8", newline="\n") as stream:
        stream.write(text)


def replace_once(path, old, new):
    text = path.read_text("utf8")
    if old in text:
        write(path, text.replace(old, new, 1))
    elif new not in text:
        raise ValueError(str(path) + ": expected previous text")


guide = NATIVE / "personal/USER_GUIDE.md"
replace_once(guide, "**0.159.0 · Kumo branch / Freddd13**",
             "**0.160.0 · Kumo branch / Freddd13**")
row = "| 对照外部MIDI、临时画音、录制并放入写谱草稿 | [MIDI轨道完整操作](docs/MIDI_TRACKS_160_GUIDE.md) |\n"
text = guide.read_text("utf8")
if row not in text:
    text = text.replace("|---|---|\n", "|---|---|\n" + row, 1)
chapter = """## 0.160：外部MIDI与临时写作

从“视图 → MIDI轨道”打开。导入后先对齐，再取消静音试听；临时轨可以画音、拖动、改音长、调力度和录制。选择“写谱草稿…”后检查记谱，再用“使用草稿”写入。

原始MIDI、编辑结果和对齐资料随MSCZ保存。删除可恢复，每次编辑可撤销。完整步骤见[MIDI轨道](docs/MIDI_TRACKS_160_GUIDE.md)，检查结果见[本批记录](docs/MIDI_TRACKS_160_CHECKS.md)。接着实施谱面轨的演奏起止调整，随后继续频谱、关联控件和动态乐谱。发布定位：`personal-v0.160.0`。
"""
if "\n## 0.160：" not in text:
    text = text.rstrip() + "\n\n" + chapter
elif "personal-v0.160.0" not in text:
    text=text.rstrip()+"\n\n发布定位：`personal-v0.160.0`。\n"
write(guide, text)
write(NATIVE / "personal/VERSION", "0.160.0\n")

changelog = NATIVE / "personal/CHANGELOG.md"
text = changelog.read_text("utf8")
if "## 0.160.0" not in text:
    entry = """## 0.160.0 — 2026-11-07

- N4：原生MIDI轨道列表接入现有卷帘，支持标准MIDI导入、新建、复制、改名、显隐、静音、独听、音量、音源、删除与恢复。
- 独立轨支持画音、移动、双端音长、力度、键盘微调及复制粘贴。录制停止后直接加入当前轨，可找回原始录制。
- 原曲绑定、偏移和内部对齐点统一映射，原曲关联改变后更新卷帘；原始MIDI及差量编辑随MSCZ保存。可按MIDI时间或原曲对齐时间导出当前轨。
- SF2与VST参考轨使用独立通道及声音实例；播放与原生Seq共用输出，支持独立和随谱播放、停止、重播、Home和反复定位。
- MIDI采用复用量化草稿，补齐新音拼写、原力度及细微演奏时间。一次采用一次撤销，原轨保留。
- 辅助MIDI修改保持乐谱音乐版本，原生撤销与保存继续跟踪；音乐版本采用常数时间读取，避免引起和弦及表达重复分析。
- 操作及实际检查见MIDI_TRACKS_160_GUIDE.md、MIDI_TRACKS_160_CHECKS.md；发布定位personal-v0.160.0。N5谱面轨演奏调整及N6—N8按完整计划继续。

"""
    text = text.replace("\n## 0.159.0", "\n" + entry + "## 0.159.0", 1)
    write(changelog, text)

source_map = NATIVE / "personal/docs/source-map.tsv"
text = source_map.read_text("utf8")
items = [
    ("MIDI读取", "mscore/workflow/midiinput.cpp", "QVariantMap readPerformanceMidiData", "SMF与真实时间读取", "midiTracksPersistence160"),
    ("MIDI轨道保存", "mscore/workflow/miditracks.cpp", "bool MidiTrackDocument::write", "原始资料、差量保存与原生撤销", "midiTracksPersistence160;midiTracksUndoState160"),
    ("MIDI声音时序", "mscore/workflow/miditransport.cpp", "void processMidiTrackPlayback", "独立与随谱输出、定位和实时监听", "midiTracksClock160;midiTracksPlayback160"),
    ("MIDI独立音源", "mscore/workflow/midisources.cpp", "MidiTrackSounds prepareMidiTrackSounds", "SF2及VST副本与通道隔离", "midiTracksIndependentSounds160"),
    ("MIDI轨道界面", "mscore/performanceeditor/miditrackpane.cpp", "MidiTrackPane::MidiTrackPane", "轨道管理与公共卷帘入口", "midiTracksEditor160"),
    ("MIDI轨道编辑", "mscore/performanceeditor/miditrackinteraction.cpp", "bool MidiTrackPane::finishGesture", "固定目标、画音与一次撤销", "midiTracksEditor160"),
    ("MIDI轨道对齐", "mscore/performanceeditor/miditrackalignment.cpp", "void MidiTrackPane::alignTrack", "原曲绑定、偏移、内部对齐", "midiTracksAlignment160"),
    ("MIDI录制与播放", "mscore/performanceeditor/miditrackplayback.cpp", "void MidiTrackPane::toggleRecording", "录制、监听及播放会话", "midiTracksEditor160;midiTracksPlayback160"),
]
for topic, name, symbol, role, tests in items:
    if topic + "\t" in text:
        continue
    lines = (NATIVE / name).read_text("utf8").splitlines()
    line = next(i + 1 for i, value in enumerate(lines) if symbol in value)
    text += "\t".join([topic, name, symbol, str(line), role, tests]) + "\n"
rows=[]
for values in csv.reader(io.StringIO(text),delimiter="\t"):
    if len(values)==6 and values[0]!="topic":
        if values[0] in {item[0] for item in items}:
            values[5]="mtest/mscore/pluginhost/miditracks_160_tests.inc"
        local=ROOT.parent/"muse3_dev/MuseScore"/values[1]
        if not local.is_file():local=NATIVE/values[1]
        lines=local.read_text("utf8").splitlines()
        matches=[i+1 for i,value in enumerate(lines) if values[2] in value]
        if not matches:raise ValueError("Source symbol missing: "+values[1]+" "+values[2])
        values[3]=str(min(matches,key=lambda line:abs(line-int(values[3]))))
    rows.append(values)
buffer=io.StringIO(newline="")
csv.writer(buffer,delimiter="\t",lineterminator="\n").writerows(rows)
write(source_map,buffer.getvalue())

image = ROOT / "P2/out/repair-160/midi-tracks-editor-160.png"
if image.is_file():
    shutil.copy2(str(image), str(NATIVE / "personal/docs/images/midi-tracks-160.png"))
    target = NATIVE / "personal/docs/MIDI_TRACKS_160_GUIDE.md"
    replace_once(target, "## 对齐录音、MIDI 和谱子",
                 "![MIDI轨道、卷帘和力度](images/midi-tracks-160.png)\n\n## 对齐录音、MIDI 和谱子")
print("Updated 0.160 guide, version, change log, source index and screenshot")
