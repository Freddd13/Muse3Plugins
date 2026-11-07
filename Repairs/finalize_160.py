"""Stage only the verified MIDI batch, leaving unrelated working changes intact."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
OUT=ROOT/"P2/out/repair-160"
tree=ast.parse((ROOT/"Repairs/sync_160.py").read_text("utf8"))
files=next(ast.literal_eval(item.value) for item in tree.body if isinstance(item,ast.Assign) and any(isinstance(target,ast.Name) and target.id=="FILES" for target in item.targets))

for name in ("pluginhost-midiTracksAlignment160.txt","pluginhost-existingEditorProfileFirstOpen.txt","performanceeditor-wheelSelectionCommit158.txt"):
    text=(OUT/name).read_text("utf8",errors="replace")
    if not re.search(r"Totals: \d+ passed, 0 failed, 0 skipped",text):raise ValueError("Incomplete checks: "+name)
program=HOST/"msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe"
checked=json.loads((OUT/"program-checks.json").read_text("utf8"))
if hashlib.sha256(program.read_bytes()).hexdigest()!=checked["sha256"]:raise ValueError("Program changed after export checks")
subprocess.run(["python",str(HOST/"personal/tools/check_guides.py")],check=True)

subprocess.run(["git","add","--",*[name for name in files if name!="personal/USER_GUIDE.md"]],cwd=HOST,check=True)
# The mirror guide contains only this task's chapter. The host working guide
# keeps the user's separate font-study chapters, which remain unstaged.
guide=(ROOT/"P2/native/personal/USER_GUIDE.md").read_bytes()
blob=subprocess.check_output(["git","hash-object","-w","--stdin"],input=guide,cwd=HOST).decode().strip()
subprocess.run(["git","update-index","--cacheinfo","100644,"+blob+",personal/USER_GUIDE.md"],cwd=HOST,check=True)
staged=subprocess.check_output(["git","diff","--cached","--name-only"],cwd=HOST,text=True).splitlines()
if set(staged)!=set(files):raise ValueError("Unexpected staged native files: "+str(set(staged)^set(files)))
subprocess.run(["git","diff","--cached","--check"],cwd=HOST,check=True)
(OUT/"staged-files.json").write_text(json.dumps(files,indent=2),encoding="utf8")
print("Staged",len(files),"native files; separate AGENTS and font-study edits retained.")
