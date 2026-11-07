"""Record the verified first batch and stage only its own changes."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import wave
import array

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent / "muse3_dev/MuseScore"
NATIVE = ROOT / "P2/native"


def write(path, text):
    with path.open("w", encoding="utf8", newline="\n") as stream:
        stream.write(text)


def replace(path, old, new):
    content = path.read_text("utf8")
    if old in content:
        write(path, content.replace(old, new, 1))
    elif new not in content:
        raise RuntimeError("Cannot find expected text: " + str(path))


replace(NATIVE / "personal/CHANGELOG.md", "2026-11-07（正在检查）", "2026-11-07")
replace(NATIVE / "personal/CHANGELOG.md",
        "真实Kawai SF2初检确认发送量改变输出。",
        "修正SF2发送重复缩小32768倍；普通与独立SF2路径的Kawai三档发送比例、尾音均已核对。")
replace(NATIVE / "personal/CHANGELOG.md", "发布检查及安装仍在进行；", "本批操作、保存、声音数据与已有播放检查通过，程序已编译；")
replace(NATIVE / "personal/docs/REWORK_PROGRESS.md",
        "安装版仍为0.158.1；0.159.0正在检查。当前按已批准顺序处理N1长按／Home／P键盘／倚音、N2混响和N3上游五项修复。Windows首轮交互及真实Kawai发送检查已通过，继续逐乐器效果、保存、已有播放及上游导出回查。",
        "0.159.0已编译，N1日常操作、N2混响与N3上游适配的软件检查已完成，正在更新原程序目录。具体结果见[本批检查](PLAYBACK_159_CHECKS.md)。接着处理N4多轨MIDI，其后依次为N5卷帘、N6频谱、N7关联控件和N8动态乐谱。")
replace(NATIVE / "personal/docs/REWORK_PROGRESS.md", "已编译并完成首轮实际操作及声音数据检查，继续收尾", "长按、Home、P键盘、前后倚音与两条Kawai发送路径已核对")
replace(NATIVE / "personal/docs/REWORK_PROGRESS.md", "已适配五项上游改动，正在编译和回查", "五项改动已适配、编译；MusicXML参考文件一致，原有播放回查通过")
replace(ROOT / "Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md", "正在修复；长按自动重复松键原因已确认", "0.159已编译检查，前后倚音及保存、Windows按键通过")
replace(ROOT / "Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md", "正在修复；发送缓冲没有进入原生混响处理已确认", "0.159已接通路由并修正重复缩小；Kawai两条路径三档输出通过")
replace(ROOT / "Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md", "已读上游补丁，待适配与验证", "五项已适配；实际MusicXML导出一致，57项报告已整理")
replace(ROOT / "Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md", "当前实现已核对，待整理正式说明", "44项工具、数据、保存与流程报告已写入本轮说明")

# Keep objective audio results next to the actual rendered files.
audio = []
for path in sorted((ROOT / "P2/out/repair-159").glob("kawai*.wav")):
    with wave.open(str(path), "rb") as stream:
        values = array.array("h", stream.readframes(stream.getnframes()))
        audio.append(dict(file=path.name, seconds=len(values)/stream.getframerate()/stream.getnchannels(),
                          peak=max(abs(v) for v in values)/32768,
                          clipped=sum(abs(v) >= 32767 for v in values)))
write(ROOT / "P2/out/repair-159/audio-summary.json", json.dumps(audio, indent=2))
print(json.dumps(audio, indent=2))

subprocess.run(["python", str(ROOT / "Repairs/sync_159.py")], check=True)
subprocess.run(["python", str(HOST / "personal/tools/check_guides.py")], check=True)

tree = ast.parse((ROOT / "Repairs/sync_159.py").read_text("utf8"))
files = next(ast.literal_eval(node.value.func.value).split() for node in tree.body
             if isinstance(node, ast.Assign) and any(isinstance(v, ast.Name) and v.id == "FILES" for v in node.targets))

# USER_GUIDE already contained the user's unrelated font research. Stage our
# chapter against committed text and leave that research in the working file.
guide = subprocess.check_output(["git", "show", "HEAD:personal/USER_GUIDE.md"], cwd=HOST).decode("utf8")
chapter = (NATIVE / "personal/USER_GUIDE.md").read_text("utf8").split("\n## 0.159：", 1)[1]
guide = guide.replace("**0.158.1 · Kumo branch / Freddd13**", "**0.159.0 · Kumo branch / Freddd13**", 1)
guide = guide.rstrip() + "\n\n## 0.159：" + chapter
blob = subprocess.check_output(["git", "hash-object", "-w", "--stdin"], input=guide.encode("utf8"), cwd=HOST).decode().strip()
subprocess.run(["git", "add", "--", *files], cwd=HOST, check=True)
subprocess.run(["git", "update-index", "--cacheinfo", "100644," + blob + ",personal/USER_GUIDE.md"], cwd=HOST, check=True)
write(ROOT / "P2/out/repair-159/staged-files.json", json.dumps(files + ["personal/USER_GUIDE.md"], indent=2))
print("Staged native batch; user AGENTS and guide research remain separate.")
