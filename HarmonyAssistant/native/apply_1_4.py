from pathlib import Path
import hashlib,json
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
stage=Path(__file__).resolve().parent/'next-1.4'
manifest=json.loads((stage/'baseline.json').read_text(encoding='utf-8'))
for name,expected in manifest.items():
    assert hashlib.sha256((repo/name).read_bytes()).hexdigest()==expected,'Concurrent modification: '+name
for name in manifest:
    (repo/name).write_bytes((stage/name).read_bytes())
print('Five native files applied with unchanged-baseline guards.')
