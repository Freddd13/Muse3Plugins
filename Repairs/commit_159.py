"""Commit the batch mirror without generated panel changes or unrelated files."""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
files=json.loads((ROOT/"P2/out/repair-159/staged-files.json").read_text("utf8"))
paths=["P2/native/"+name for name in files]
paths += ["Planning/PLAYBACK_MULTITRACK_VIDEO_IMPLEMENTATION.md"]
paths += ["Repairs/"+name for name in (
    "sync_159.py", "run_159_checks.py", "prepare_159_spacing.py", "prepare_159_docs.py",
    "prepare_upstream_159.py", "apply_upstream_159.py", "finalize_159.py", "install_159.py",
    "check_installed_159.py", "commit_159.py")]
subprocess.run(["git","add","--",*paths],cwd=ROOT,check=True)
# Newly mirrored upstream files retain their original whitespace. Check native
# changes against the host's original revision, and verify mirror bytes against
# the committed host, instead of treating every copied legacy line as new code.
subprocess.run(["git","diff","8f81421a5cc965dbb32a81fcecf39d626b5610ff","HEAD","--check"],cwd=HOST,check=True)
for name in files:
    committed=subprocess.check_output(["git","show","HEAD:"+name],cwd=HOST)
    if (ROOT/"P2/native"/name).read_bytes()!=committed:
        raise RuntimeError("Mirror differs from committed host: "+name)
subprocess.run(["git","diff","--cached","--check","--",*[p for p in paths if not p.startswith("P2/native/")]],cwd=ROOT,check=True)
subprocess.run(["git","commit","-m","Deliver 0.159 operation and reverb fixes with upstream and AI reports"],cwd=ROOT,check=True)
