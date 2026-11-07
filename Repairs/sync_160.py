"""Sync the in-progress MIDI batch using explicit files and content checks."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT.parent/"muse3_dev/MuseScore"
FILES=["mscore/workflow/miditracks.h","mscore/workflow/miditracks.cpp",
       "libmscore/undo.h","libmscore/undo.cpp","libmscore/score.cpp","mscore/workflow/workflowcontext.h",
       "mscore/workflow/miditransport.h","mscore/workflow/miditransport.cpp",
       "mscore/workflow/midisources.h","mscore/workflow/midisources.cpp",
       "audio/vst/vstsynth.h","audio/vst/vstsynth.cpp","audio/vst/rack.h","audio/vst/rack.cpp",
       "mscore/workflow/midiinput.h","mscore/workflow/midiinput.cpp","mscore/plugin/plugin.cmake",
       "mscore/workflow/midicapture.h","mscore/workflow/midicapture.cpp",
       "mscore/seq.cpp",
       "mtest/mscore/pluginhost/tst_pluginhost.cpp","mtest/mscore/pluginhost/miditracks_160_tests.inc",
       "mscore/performanceeditor/miditrackpane.h","mscore/performanceeditor/miditrackpane.cpp",
       "mscore/performanceeditor/miditrackinteraction.cpp","mscore/performanceeditor/miditrackplayback.cpp","mscore/performanceeditor/miditrackalignment.cpp",
       "mscore/performanceeditor/performanceeditor.h","mscore/performanceeditor/performanceeditor.cpp",
       "mscore/performanceeditor/performancepainting.cpp","mscore/performanceeditor/performanceinteraction.cpp","mscore/performanceeditor/performanceux.cpp",
       "mscore/performanceeditor/performanceeditor.cmake","mscore/musescore.cpp",
       "mscore/performanceeditor/rollwriting.h","mscore/performanceeditor/rollwritingmodel.cpp",
       "personal/VERSION","personal/USER_GUIDE.md","personal/CHANGELOG.md",
       "personal/docs/source-map.tsv","personal/docs/REWORK_PROGRESS.md","personal/docs/MIDI_TRACKS_160_GUIDE.md",
       "personal/docs/MIDI_TRACKS_160_CHECKS.md","personal/docs/images/midi-tracks-160.png"]
record=ROOT/"P2/out/repair-160-applied.json"
hashes=json.loads(record.read_text("utf8")) if record.exists() else {}
batch=[]
for name in FILES:
    source=ROOT/"P2/native"/name;target=HOST/name;data=source.read_bytes()
    if source.suffix in (".cpp",".h",".cmake",".md",".tsv") or name=="personal/VERSION":
        normalized=data.replace(b"\r\n",b"\n")
        if normalized!=data:source.write_bytes(normalized);data=normalized
    actual=target.read_bytes() if target.exists() else b""
    if name=="personal/USER_GUIDE.md" and actual!=data:
        # The host guide contains the user's separate font-study additions.
        # Merge our new chapter into that working file without publishing those
        # additions as part of the MIDI commit.
        directory=ROOT/"P2/out/repair-160"
        directory.mkdir(exist_ok=True)
        previous=directory/"guide-last-native.md"
        committed=previous.read_bytes() if previous.is_file() else subprocess.check_output(["git","show","HEAD:"+name],cwd=HOST)
        paths=[directory/("guide-"+label+".md") for label in ("current","base","midi")]
        for path,content in zip(paths,(actual,committed,data)):path.write_bytes(content)
        merged=subprocess.run(["git","merge-file","-p",*[str(path) for path in paths]],capture_output=True)
        if merged.returncode:
            marker="\n## 0.160："
            current=actual.decode("utf8");incoming=data.decode("utf8")
            currentHead,found,currentChapter=current.partition(marker)
            _,incomingFound,incomingChapter=incoming.partition(marker)
            tag="发布定位：`personal-v0.160.0`。"
            if not found or not incomingFound or currentChapter.replace(tag,"").strip()!=incomingChapter.replace(tag,"").strip():
                raise RuntimeError("Guide merge needs review")
            data=(currentHead+marker+incomingChapter).encode("utf8")
        else:data=merged.stdout
        previous.write_bytes(source.read_bytes())
        batch.append((name,target,data))
        continue
    if actual!=data and target.exists():
        committed=subprocess.run(["git","show","HEAD:"+name],cwd=HOST,capture_output=True).stdout
        if actual!=committed and hashlib.sha256(actual).hexdigest()!=hashes.get(name):raise RuntimeError("Separate edits: "+name)
    batch.append((name,target,data))
for name,target,data in batch:
    if not target.exists() or target.read_bytes()!=data:target.write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest()
record.write_text(json.dumps(hashes,indent=2),encoding="utf8")
print("Synced",len(batch),"MIDI batch files")
