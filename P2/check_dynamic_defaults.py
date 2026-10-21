"""Read the dynamics fixture with official MuseScore and compare exported note velocities."""
from pathlib import Path
from fractions import Fraction
import argparse, hashlib, json, os, struct, subprocess, zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def note_events(path):
    data = path.read_bytes()
    assert data[:4] == b'MThd'
    length = int.from_bytes(data[4:8], 'big')
    _, tracks, ppq = struct.unpack_from('>HHH', data, 8)
    assert ppq and not ppq & 0x8000
    position, notes = 8 + length, []
    for _ in range(tracks):
        assert data[position:position+4] == b'MTrk'
        size = int.from_bytes(data[position+4:position+8], 'big')
        track = data[position+8:position+8+size]
        position += 8 + size
        at, tick, running = 0, 0, 0

        def vlq():
            nonlocal at
            value = 0
            while True:
                byte = track[at]; at += 1
                value = (value << 7) | (byte & 127)
                if not byte & 128:
                    return value
        while at < len(track):
            tick += vlq()
            status = track[at]
            if status & 128:
                at += 1
                running = status if status < 0xf0 else 0
            else:
                status = running
                assert status
            if status == 0xff:
                at += 1
                length = vlq()
                at += length
            elif status in (0xf0, 0xf7):
                length = vlq()
                at += length
            else:
                kind, channel = status & 0xf0, status & 15
                assert 0x80 <= kind <= 0xe0
                first = track[at]; at += 1
                if kind not in (0xc0, 0xd0):
                    second = track[at]; at += 1
                    if kind == 0x90 and second:
                        notes.append((Fraction(tick, ppq), channel, first, second))
    return sorted(notes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--score', type=Path, default=ROOT.parent/'P1/out/final-regression/dynamics-defaults-082.mscz')
    parser.add_argument('--program', type=Path, default=ROOT/'out/compat-3.6.2/extracted/layout/MuseScore 3/bin/MuseScore3.exe')
    args = parser.parse_args()
    source, program = args.score.resolve(), args.program.resolve()
    work = ROOT/'out/dynamics-compat-082'; work.mkdir(exist_ok=True)
    settings = work/'settings'; settings.mkdir(exist_ok=True)
    before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    temp = ROOT.parent/'P1/out/final-regression/tmp'; temp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TEMP=str(temp), TMP=str(temp), KUMO_MCP_AUTOSTART='0', QML_DISABLE_DISK_CACHE='1')
    startup = None
    if os.name == 'nt':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
    results = {}
    for suffix in ('mid', 'mscz'):
        target = work/('official-3.6.2.'+suffix)
        assert target.resolve() != source
        result = subprocess.run([str(program), '-s', '-m', '-c', str(settings), '-o', str(target), str(source)],
                                env=env, cwd=work, startupinfo=startup, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        (work/('official-'+suffix+'.log')).write_bytes(result.stdout)
        assert not result.returncode and target.is_file(), result.stdout.decode('utf8', errors='replace')[-2000:]
        results[suffix] = str(target)
    with zipfile.ZipFile(work/'official-3.6.2.mscz') as archive:
        name = next(n for n in archive.namelist() if n.endswith('.mscx'))
        tree = ET.fromstring(archive.read(name))
    marks = [(e.findtext('subtype'), int(e.findtext('velocity', '-1'))) for e in tree.findall('.//Dynamic')]
    assert sorted(marks) == sorted([('mp', 58), ('mp', 43), ('p', 37)])
    native = note_events(source.with_suffix('.mid'))
    official = note_events(work/'official-3.6.2.mid')
    report = {'sourceUnchanged': hashlib.sha256(source.read_bytes()).hexdigest() == before_hash,
              'sameNoteOnEvents': native == official, 'native': [[str(t), ch, key, vel] for t, ch, key, vel in native],
              'official': [[str(t), ch, key, vel] for t, ch, key, vel in official], 'dynamicValues': marks, 'files': results,
              'programSha256': hashlib.sha256(program.read_bytes()).hexdigest()}
    (work/'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    assert report['sourceUnchanged'] and report['sameNoteOnEvents']

if __name__ == '__main__':
    main()
