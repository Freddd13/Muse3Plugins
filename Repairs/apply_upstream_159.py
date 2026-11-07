"""Apply the checked, approved upstream patch and preserve source snapshots."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
FILES=["libmscore/sig.cpp","libmscore/check.cpp","libmscore/segment.cpp","libmscore/segment.h",
       "libmscore/stafftypelist.cpp","importexport/musicxml/exportxml.cpp","mtest/musicxml/io/tst_mxml_io.cpp",
       "mtest/musicxml/io/testMeasureRepeat.mscx","mtest/musicxml/io/testMeasureRepeat_ref.xml"]
patch=ROOT/"P2/out/upstream-159.patch"
status=subprocess.run(["git","diff","--name-only","--",*FILES],cwd=HOST,capture_output=True,check=True).stdout
if status.strip(): raise RuntimeError("The upstream target files have separate changes: "+status.decode())
subprocess.run(["git","apply","--check",str(patch)],cwd=HOST,check=True)
subprocess.run(["git","apply",str(patch)],cwd=HOST,check=True)
state_path=ROOT/"P2/out/repair-159-applied.json"
state=json.loads(state_path.read_text("utf8"))
for name in FILES:
    target=ROOT/"P2/native"/name
    if target.exists():
        backup=ROOT/"P2/out/upstream-159-originals"/name
        backup.parent.mkdir(parents=True,exist_ok=True)
        if not backup.exists():backup.write_bytes(target.read_bytes())
    target.parent.mkdir(parents=True,exist_ok=True)
    content=(HOST/name).read_bytes();target.write_bytes(content)
    state[name]=hashlib.sha256(content).hexdigest()
state_path.write_text(json.dumps(state,indent=2),encoding="utf8")
print("Applied approved upstream files:",len(FILES))
