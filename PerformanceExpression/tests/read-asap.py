"""Convert local ASAP expert alignments to values for evaluate-alignment.cjs.

Usage: python read-asap.py recording.match output.json
The dataset is supplied separately: https://github.com/CPJKU/asap-dataset
Its CC BY-NC-SA 4.0 licence applies to source material and generated fixtures.
The app does not load this script or require the dataset.
"""
from fractions import Fraction
from pathlib import Path
import json
import re
import sys

source = Path(sys.argv[1]).read_text("utf8")
clock = int(re.search(r"info\(midiClockUnits,(\d+)\)", source)[1])
microseconds = int(re.search(r"info\(midiClockRate,(\d+)\)", source)[1])
legacy = bool(re.search(r"info\(matchFileVersion,5\.0\)", source))
signature = re.search(r"info\(timeSignature,\[(\d+)/(\d+)\]\)", source)
denominator = int(signature[2]) if legacy and signature else 4
quarter_scale = 4 / denominator if legacy else 1
score_pattern = re.compile(r"snote\(([^,]+),\[([A-G]),([^\]]+)\],(\d+),(-?\d+):([^,]+),([^,]+),([^,]+),([-\d.]+),([-\d.]+),\[([^\]]*)\]\)")
note_pattern = re.compile(r"\bnote\(([^,]+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)\)")
legacy_pattern = re.compile(r"\bnote\(([^,]+),\[([A-G]),([^\]]+)\],(\d+),(\d+),(\d+),(\d+),(\d+)\)")


def pitch(step, alteration, octave):
    return ((int(octave) + 1) * 12 + {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[step]
            + {"n": 0, "#": 1, "##": 2, "b": -1, "bb": -2}[alteration])


notes, performed, truth = [], [], {}
for line in source.splitlines():
    written, played, old = score_pattern.search(line), note_pattern.search(line), legacy_pattern.search(line)
    if written:
        sid, step, alteration, octave, bar, beat, offset, duration, on, off, attrs = written.groups()
        voice, staff = re.search(r"\bv(\d+)", attrs), re.search(r"\bstaff(\d+)", attrs)
        # Older match files omit voice/staff. Those results test musical matching;
        # native MusicXML tests separately verify host identities and write-back.
        track = (int(staff[1]) - 1) * 4 + (int(voice[1]) - 1) % 4 if staff and voice else 0
        on, off = float(on) * quarter_scale, float(off) * quarter_scale
        notes.append(dict(id=sid, logicalId=sid, pitch=pitch(step, alteration, octave), tick=round(on * 480),
                          end=round(off * 480), grace=on == off, measure=int(bar),
                          beat=float(Fraction(beat)) + denominator * float(Fraction(offset)), track=track, index=0,
                          velocity=80, velocityType=0, velocityRaw=0, velocityBase=80, bpm=120,
                          onSeconds=on * .5, scoreSeconds=on * .5))
    if played:
        mid, midi_pitch, on, off, velocity, _, _ = played.groups()
    elif old:
        mid, step, alteration, octave, on, off, sustain, velocity = old.groups()
        midi_pitch = pitch(step, alteration, octave)
    else:
        continue
    seconds_per_tick = microseconds / 1e6 / clock
    performed.append(dict(id=mid, pitch=int(midi_pitch), seconds=int(on) * seconds_per_tick,
                          duration=(int(off) - int(on)) * seconds_per_tick, velocity=int(velocity)))
    if written:
        truth[sid] = mid
indices = {}
for note in sorted(notes, key=lambda n: (n["tick"], n["track"], n["pitch"])):
    key = note["tick"], note["track"]
    note["index"] = indices.get(key, 0)
    indices[key] = note["index"] + 1
Path(sys.argv[2]).write_text(json.dumps(dict(notes=notes, performance=performed, truth=truth), ensure_ascii=False), encoding="utf8")
print(f"{len(notes)} score notes, {len(performed)} performed notes, {len(truth)} expert pairs")
