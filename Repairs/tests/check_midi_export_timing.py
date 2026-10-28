"""Independently check the SMFs written by the native MIDI timing tests.

Run TestP0Native's repeat/header, pause/lyrics and anticipation cases first.
This reader uses Python's standard library and does not import MuseScore code.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
from pathlib import Path
import struct


def read_midi(path: Path) -> dict:
    raw = path.read_bytes()
    assert raw[:4] == b"MThd", path
    header_size, _, track_count, division = struct.unpack(">IHHH", raw[4:14])
    assert division > 0 and not division & 0x8000, "This fixture uses PPQ timing"
    offset = 8 + header_size
    notes, metadata, controls, tempos = [], [], [], {0: 500_000}
    for _ in range(track_count):
        assert raw[offset:offset + 4] == b"MTrk"
        size = int.from_bytes(raw[offset + 4:offset + 8], "big")
        track = raw[offset + 8:offset + 8 + size]
        assert len(track) == size
        offset += 8 + size
        at = tick = running = 0

        def take(count: int) -> bytes:
            nonlocal at
            value = track[at:at + count]
            assert len(value) == count, "Truncated MIDI event"
            at += count
            return value

        def variable_length() -> int:
            value = 0
            for _ in range(4):
                byte = take(1)[0]
                value = (value << 7) | (byte & 0x7f)
                if byte < 0x80:
                    return value
            raise AssertionError("Invalid variable length")

        while at < len(track):
            tick += variable_length()
            status = track[at]
            if status >= 0x80:
                at += 1
            else:
                status = running
            if status == 0xff:
                kind = take(1)[0]
                payload = take(variable_length())
                metadata.append((tick, kind, payload))
                running = 0
                if kind == 0x51:
                    assert len(payload) == 3
                    tempos[tick] = int.from_bytes(payload, "big")
                if kind == 0x2f:
                    assert at == len(track)
                    break
            elif status in (0xf0, 0xf7):
                take(variable_length())
                running = 0
            else:
                assert 0x80 <= status < 0xf0, "Invalid running status"
                running = status
                kind = status & 0xf0
                payload = take(1 if kind in (0xc0, 0xd0) else 2)
                if kind == 0x90 and payload[1] > 0:
                    notes.append((tick, payload[0]))
                elif kind == 0xb0:
                    controls.append((tick, payload[0], payload[1]))
    assert offset == len(raw)
    ticks = sorted(tempos)
    times = [0.0]
    for before, after in zip(ticks, ticks[1:]):
        times.append(times[-1] + (after - before) * tempos[before] / division / 1_000_000)

    def seconds(tick: int) -> float:
        index = bisect.bisect_right(ticks, tick) - 1
        return times[index] + (tick - ticks[index]) * tempos[ticks[index]] / division / 1_000_000

    return {
        "notes": [(seconds(t), pitch) for t, pitch in notes],
        "meta": [(seconds(t), kind, data) for t, kind, data in metadata],
        "controllers": [(seconds(t), cc, value) for t, cc, value in controls],
    }


def verify(directory: Path) -> list[dict]:
    results = []
    for repeat in (0, 1):
        for written in (0, 1):
            name = f"repeat-policy-{repeat}-{written}.mid"
            data = read_midi(directory / name)
            roots = sorted(t for t, pitch in data["notes"] if pitch == 36)
            upper = sorted(t for t, pitch in data["notes"] if pitch == 59)
            signatures = [t for t, kind, _ in data["meta"] if kind == 0x58]
            expected_roots = [0.0, 2.583333333333] if repeat else [0.0]
            expected_upper = [0.75, 3.333333333333] if repeat else [0.75]
            assert len(data["notes"]) == 6 * (repeat + 1), name
            assert len(signatures) == repeat + 1, name
            for actual, expected in ((roots, expected_roots), (upper, expected_upper)):
                assert len(actual) == len(expected), name
                assert all(math.isclose(a, b, abs_tol=.002) for a, b in zip(actual, expected)), (name, actual)
            results.append({"file": name, "notes": len(data["notes"]), "rootSeconds": roots, "upperSeconds": upper})

    name = "anticipation-metadata-134.mid"
    data = read_midi(directory / name)
    first = [t for t, kind, text in data["meta"] if kind == 6 and text == b"Kumo: score first beat"]
    lyrics = [t for t, kind, _ in data["meta"] if kind == 5]
    marks = [t for t, kind, text in data["meta"] if kind == 6 and text == b"A"]
    assert first == lyrics == marks == [.2], (name, first, lyrics, marks)
    assert any(t == 0 and pitch == 36 for t, pitch in data["notes"])
    pedals = [t for t, cc, value in data["controllers"] if cc == 64 and value >= 64]
    assert len(pedals) == 1 and math.isclose(pedals[0], .2 + 2 / 960, abs_tol=.00001)
    results.append({"file": name, "firstBeatSeconds": first, "lyricsSeconds": lyrics, "pedalSeconds": pedals})

    name = "pause-metadata-134.mid"
    data = read_midi(directory / name)
    upper = sorted(t for t, pitch in data["notes"] if pitch == 59)
    lyrics = sorted(t for t, kind, _ in data["meta"] if kind == 5)
    marks = sorted(t for t, kind, text in data["meta"] if kind == 6 and text == b"A")
    assert upper == lyrics == marks == [.75, 3.0], (name, upper, lyrics, marks)
    results.append({"file": name, "upperSeconds": upper, "lyricsSeconds": lyrics, "markersSeconds": marks})
    return results


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=root / "P1/out/final-regression")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = verify(args.artifacts)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf8")
    print(text)
