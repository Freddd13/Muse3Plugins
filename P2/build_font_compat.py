"""Reproduce the small, renamed metronome font from the official 3.6.2 source."""
from pathlib import Path
from urllib.request import Request, urlopen
import base64
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'out/font-tools'))
from fontTools import subset
from fontTools.ttLib import TTFont


def main():
    source = 'https://raw.githubusercontent.com/musescore/MuseScore/v3.6.2/fonts/leland/'
    def download(name):
        url = 'https://api.github.com/repos/musescore/MuseScore/contents/fonts/leland/' + name + '?ref=v3.6.2'
        with urlopen(Request(url, headers={'User-Agent': 'MuseScore-font-compatibility'}), timeout=30) as response:
            return base64.b64decode(json.load(response)['content'])
    output = ROOT / 'native/fonts/compatmetronome'
    output.mkdir(parents=True, exist_ok=True)
    original = ROOT / 'out/font-comparison-064/LelandText-3.6.2.otf'
    if not original.exists():
        original.write_bytes(download('LelandText.otf'))
    license = download('LICENSE.txt')
    font = TTFont(original, recalcTimestamp=False)
    options = subset.Options()
    options.recalc_timestamp = False
    options.name_IDs = ['*']
    worker = subset.Subsetter(options=options)
    worker.populate(unicodes=[9, 32] + list(range(0xECA0, 0xECB8)))
    worker.subset(font)
    names = {1: 'Metronome Text 3', 2: 'Regular', 3: 'MetronomeText3-Regular-1',
             4: 'Metronome Text 3', 6: 'MetronomeText3-Regular',
             16: 'Metronome Text 3', 17: 'Regular'}
    for record in font['name'].names:
        if record.nameID in names:
            record.string = names[record.nameID].encode(record.getEncoding())
    if 'CFF ' in font:
        font['CFF '].cff.fontNames = ['MetronomeText3-Regular']
        top = font['CFF '].cff.topDictIndex[0]
        top.FamilyName = 'Metronome Text 3'
        top.FullName = 'Metronome Text 3'
    target = output / 'MetronomeText3.otf'
    font.save(target)
    (output / 'LICENSE.txt').write_bytes(b'\n'.join(line.rstrip() for line in license.splitlines()) + b'\n')
    metadata = {'source': source + 'LelandText.otf', 'release': 'v3.6.2',
        'sourceSha256': hashlib.sha256(original.read_bytes()).hexdigest(),
        'outputSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'license': 'SIL Open Font License 1.1', 'fontTools': '4.60.2',
        'changes': 'Metronome glyph subset, renamed to Metronome Text 3. Original copyright and license retained.'}
    (output / 'SOURCES.json').write_text(json.dumps(metadata, indent=2) + '\n', 'utf8')
    print(target, target.stat().st_size)


if __name__ == '__main__':
    main()
