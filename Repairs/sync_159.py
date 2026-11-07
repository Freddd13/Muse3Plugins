"""Copy only this repair's native files, leaving all other work intact."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT.parent / "muse3_dev/MuseScore"
FILES = """
effects/effect.h
effects/freeverb/freeverb.h
effects/freeverb/freeverb.cpp
effects/zita1/zita.h
effects/zita1/zita.cpp
audio/midi/msynthesizer.h
audio/midi/msynthesizer.cpp
audio/midi/synthesizer.h
audio/midi/fluid/fluid.cpp
audio/midi/fluid/voice.cpp
audio/vst/plugin.h
audio/vst/rack.h
audio/vst/rack.cpp
audio/vst/vstsynth.h
audio/vst/vstsynth.cpp
audio/vst/fluidsource.cpp
mscore/pianotools.h
mscore/pianotools.cpp
mscore/mixer/mixerdetails.cpp
mscore/seq.h
mscore/seq.cpp
mscore/musescore.cpp
mscore/workflow/workflowcontext.h
mscore/workflow/playbackpreview.h
mscore/workflow/playbackpreview.cpp
mscore/workflow/referenceworkflow.cpp
mscore/workflow/scoreworkflow.cpp
mscore/performanceeditor/performanceeditor.h
mscore/performanceeditor/performanceeditor.cpp
mscore/performanceeditor/performanceinteraction.cpp
mscore/performanceeditor/performanceux.cpp
mscore/performanceeditor/editorsettings.cpp
libmscore/property.h
libmscore/property.cpp
libmscore/chord.h
libmscore/chord.cpp
libmscore/rendermidi.cpp
libmscore/sig.cpp
libmscore/check.cpp
libmscore/segment.cpp
libmscore/segment.h
libmscore/stafftypelist.cpp
importexport/musicxml/exportxml.cpp
mtest/musicxml/io/tst_mxml_io.cpp
mtest/musicxml/io/CMakeLists.txt
mtest/musicxml/io/testMeasureRepeat.mscx
mtest/musicxml/io/testMeasureRepeat_ref.xml
personal/VERSION
personal/CHANGELOG.md
personal/docs/source-map.tsv
personal/docs/REWORK_PROGRESS.md
personal/docs/PLAYBACK_159_GUIDE.md
personal/docs/PLAYBACK_159_CHECKS.md
personal/docs/AI_CONNECTION_IMPLEMENTATION_159.md
personal/docs/UPSTREAM_159_REPORT.md
personal/docs/images/peek-settings-159.png
personal/docs/images/grace-spacing-159.png
mscore/inspector/inspectorNote.cpp
mtest/mscore/pluginhost/tst_pluginhost.cpp
mtest/mscore/pluginhost/playback_159_tests.inc
mtest/mscore/performanceeditor/tst_performanceeditor.cpp
mtest/mscore/performanceeditor/interaction_159_tests.inc
""".split()
state_path = ROOT / "P2/out/repair-159-applied.json"
previous = json.loads(state_path.read_text("utf8")) if state_path.exists() else {}
prepared = []
for name in FILES:
    source = ROOT / "P2/native" / name
    target = HOST / name
    desired = source.read_bytes()
    actual = target.read_bytes() if target.exists() else b""
    if actual != desired:
        committed = subprocess.run(["git", "show", "HEAD:" + name], cwd=HOST, capture_output=True)
        if target.exists() and actual != committed.stdout and hashlib.sha256(actual).hexdigest() != previous.get(name):
            raise RuntimeError("Target has separate changes: " + name)
    prepared.append((name, target, desired))
for name, target, desired in prepared:
    if not target.exists() or target.read_bytes() != desired:
        target.write_bytes(desired)
    previous[name] = hashlib.sha256(desired).hexdigest()
state_path.write_text(json.dumps(previous, indent=2), encoding="utf8")
print("Synchronized", len(prepared), "repair files")
