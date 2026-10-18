"""Compare exports of a read-only score using stock 3.6.2 and the current build."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
HOST = ROOT.parent.parent / 'muse3_dev/MuseScore'
OUT = ROOT / 'out/font-comparison-064'
SOURCE = Path('C:/Users/Fred/OneDrive - yunzd/arr/如果有来生/如果有来生-release5.mscz')


def main():
    from pypdf import PdfReader
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    stock = OUT / 'stock/layout/MuseScore 3/bin/MuseScore3.exe'
    runtime = ROOT.parent / 'P1/out/final-regression/runtime/bin/MuseScore3Evo.exe'
    shutil.copy2(HOST / 'msvc.build_harmony_release_x64/main/Release/MuseScore3Evo.exe', runtime)
    report = {'score': str(SOURCE), 'sha256': source_hash, 'exports': {}}
    for name, program in [('stock', stock), ('current', runtime)]:
        settings = OUT / (name + '-settings')
        settings.mkdir(exist_ok=True)
        pdf = OUT / (name + '.pdf')
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        with (OUT / (name + '-export.log')).open('wb') as log:
            result = subprocess.run([str(program), '-s', '-c', str(settings), '-o', str(pdf), str(SOURCE)],
                cwd=OUT, env=dict(os.environ, KUMO_MCP_AUTOSTART='0'), startupinfo=startup,
                stdout=log, stderr=subprocess.STDOUT, timeout=120)
        if result.returncode or not pdf.exists():
            raise RuntimeError(f'{name} export: {result.returncode}')
        reader = PdfReader(pdf)
        fonts = set()
        for page in reader.pages:
            for font in page['/Resources'].get('/Font', {}).values():
                fonts.add(str(font.get_object().get('/BaseFont')))
        report['exports'][name] = {'pages': len(reader.pages), 'fonts': sorted(fonts)}
        print(name, report['exports'][name], flush=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')


if __name__ == '__main__':
    main()
