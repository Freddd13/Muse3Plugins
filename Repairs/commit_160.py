"""Commit this batch's mirror and helpers without other local development files."""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
files=json.loads((ROOT/"P2/out/repair-160/staged-files.json").read_text("utf8"))
for name in files:
    committed=subprocess.check_output(["git","show","HEAD:"+name],cwd=HOST)
    if committed!=(ROOT/"P2/native"/name).read_bytes():raise ValueError("Mirror differs: "+name)
paths=["P2/native/"+name for name in files]
paths += ["Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md","Planning/MIDI_TRACKS_DESIGN.md","P2/check_stock.py"]
paths += ["Repairs/"+name for name in ("sync_160.py","build_160.py","run_160_checks.py","prepare_160_editor.py","prepare_160_sources.py","prepare_160_docs.py","check_160_program.py","finalize_160.py","install_160.py","commit_160.py")]
subprocess.run(["git","add","--",*paths],cwd=ROOT,check=True)
subprocess.run(["git","diff","--cached","--check","--",*[p for p in paths if not p.startswith("P2/native/")]],cwd=ROOT,check=True)
subprocess.run(["git","commit","-m","Deliver 0.160 reference MIDI tracks, recording and notation drafts"],cwd=ROOT,check=True)
