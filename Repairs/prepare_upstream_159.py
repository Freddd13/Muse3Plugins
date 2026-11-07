"""Prepare only the approved musical fixes from the fetched upstream tree."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
FILES=["libmscore/sig.cpp","libmscore/check.cpp",
       "libmscore/segment.cpp","libmscore/segment.h","libmscore/stafftypelist.cpp",
       "importexport/musicxml/exportxml.cpp","mtest/musicxml/io/tst_mxml_io.cpp",
       "mtest/musicxml/io/testMeasureRepeat.mscx","mtest/musicxml/io/testMeasureRepeat_ref.xml"]
diff=subprocess.run(["git","diff","18ac05e6ebc5","564998bd4c8e","--",*FILES],cwd=HOST,capture_output=True,check=True).stdout
patch=ROOT/"P2/out/upstream-159.patch"
patch.write_bytes(diff)
renderer=ROOT/"P2/native/libmscore/rendermidi.cpp"
text=renderer.read_text("utf8")
before="int a = st + tickOffset + (3 - MScore::pedalEventsMinTicks);"
after="int a = qMax(st + tickOffset + (3 - MScore::pedalEventsMinTicks), 0);"
if before in text:
    with renderer.open("w",encoding="utf8",newline="\n") as stream: stream.write(text.replace(before,after))
elif after not in text: raise RuntimeError("The personal pedal rendering path needs review")
result=subprocess.run(["git","apply","--check",str(patch)],cwd=HOST,capture_output=True)
print(result.stdout.decode("utf8",errors="replace"),result.stderr.decode("utf8",errors="replace"))
print("Prepared",patch,"bytes",len(diff),"check",result.returncode)
raise SystemExit(result.returncode)
