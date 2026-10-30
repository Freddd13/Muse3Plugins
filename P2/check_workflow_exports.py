"""Check the actual saved composition's installed PDF/MIDI exports, without changing its source."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction

from pypdf import PdfReader

R = Path(__file__).resolve().parent.parent
H = R.parent / "muse3_dev/MuseScore"
spec = importlib.util.spec_from_file_location("workflow_midi", R / "Repairs/tests/check_midi_export_timing.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=R / "P1/out/final-regression/workflow-sessions.mscz")
    parser.add_argument("--output", type=Path, default=R / "P2/out/workflow-exports-153")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    with zipfile.ZipFile(source) as archive:
        xml = ET.fromstring(archive.read(next(name for name in archive.namelist() if name.endswith(".mscx"))))
    notes = xml.findall(".//Staff/Measure/voice/Chord/Note")
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_QUICK_BACKEND="software", KUMO_MCP_AUTOSTART="0")
    env["TEMP"] = env["TMP"] = str(R / "P1/out/final-regression/tmp")
    executable = H / "msvc.install_repair_current_x64/bin/MuseScore3Evo.exe"
    for kind in ("pdf", "mid"):
        target = output / ("composition." + kind)
        result = subprocess.run([str(executable), "-s", "-c", str(output / "settings"), "-o", str(target), str(source)],
                                env=env, capture_output=True, timeout=120)
        (output / (kind + ".log")).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0 and target.stat().st_size > 100, kind
    midi = reader.read_midi(output / "composition.mid")
    assert len(midi["notes"]) == len(notes), "saved notes and exported MIDI differ"
    # The normal XML contains the designated main writing; this branch reopens
    # the chosen combination. Compare to MIDI from that actual live composition.
    baseline = reader.read_midi(source.with_name("workflow-sessions-current.mid"))
    for field in ("note_events", "control_events"):
        normalize = lambda data: sorted((Fraction(row[0], data["division"]), *row[1:]) for row in data[field])
        assert normalize(midi) == normalize(baseline), field
    pedal = [row for row in midi["controllers"] if row[1] == 64]
    assert pedal and any(row[2] >= 64 for row in pedal) and any(row[2] < 64 for row in pedal), pedal
    pdf = PdfReader(output / "composition.pdf")
    assert len(pdf.pages) == 2, len(pdf.pages)
    text = "\n".join(page.extract_text() for page in pdf.pages)
    assert all(word not in text for word in ("正在", "Reference", "105", "Left Hand", "Right Hand")), text
    poppler = shutil.which("pdftoppm")
    if not poppler:
        raise RuntimeError("pdftoppm is required for the page check")
    subprocess.run([poppler, "-r", "100", "-png", str(output / "composition.pdf"), str(output / "page")], check=True)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    report = {"source": str(source), "sourceSha256": before, "pages": len(pdf.pages), "notes": len(notes),
              "currentCombinationMidiMatches": True, "pedalEvents": pedal,
              "executableSha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
