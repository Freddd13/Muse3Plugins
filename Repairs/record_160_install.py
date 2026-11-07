"""Record the checked 0.160 installation without changing unrelated working files."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
record=json.loads((ROOT/"P2/out/repair-160/installation.json").read_text("utf8"))
assert hashlib.sha256(Path(record["program"]).read_bytes()).hexdigest()==record["sha256"]
updates={
"personal/docs/REWORK_PROGRESS.md":[
("正在进行最终程序检查和安装。", "0.160.0已安装到原程序目录，244份随包说明已更新。"),
("当前先完成N4交付，再按N5、N6、N7、N8继续。", "N4交付已完成，接着按N5、N6、N7、N8继续。")],
"personal/docs/MIDI_TRACKS_160_CHECKS.md":[
("当前安装程序、最终检查数量和提交见本文件后续发布记录。", "0.160.0已更新原安装目录，244份说明已发布，个人配置保持。实现提交为4319f7bea077587026a5eb5ea305cd4a8b79b1b7，发布定位personal-v0.160.0。安装程序SHA-256：`"+record["sha256"]+"`。")],
"personal/CHANGELOG.md":[
("发布定位personal-v0.160.0。N5", "实现提交4319f7bea077587026a5eb5ea305cd4a8b79b1b7；0.160已安装并更新244份说明，发布定位personal-v0.160.0。N5")]
}
for name,replacements in updates.items():
    mirror=ROOT/"P2/native"/name
    original=mirror.read_bytes()
    if (HOST/name).read_bytes()!=original:raise ValueError("Separate modification: "+name)
    text=original.decode("utf8")
    for old,new in replacements:
        if old not in text:raise ValueError("Expected text: "+old)
        text=text.replace(old,new,1)
    data=text.encode("utf8")
    mirror.write_bytes(data)
    (HOST/name).write_bytes(data)
plan=ROOT/"Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md"
text=plan.read_text("utf8").replace("正在提交安装", "已安装并更新244份随包说明")
plan.write_bytes(text.encode("utf8"))
subprocess.run(["git","add","--",*updates],cwd=HOST,check=True)
subprocess.run(["git","diff","--cached","--check"],cwd=HOST,check=True)
subprocess.run(["git","commit","-m","Record verified 0.160 installation and continue N5"],cwd=HOST,check=True)
paths=["P2/native/"+name for name in updates]
paths += ["Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md","Repairs/check_160_program.py","Repairs/install_160.py","Repairs/record_160_install.py"]
subprocess.run(["git","add","--",*paths],cwd=ROOT,check=True)
subprocess.run(["git","commit","-m","Record 0.160 installed program and next batch"],cwd=ROOT,check=True)
print("Recorded installed executable",record["sha256"])
