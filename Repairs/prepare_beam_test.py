from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
path='mtest/libmscore/beam/tst_beam.cpp';text=(HOST/path).read_text(encoding='utf8')
# Windows GDI also defines a Chord function. Spell the existing music type fully.
text=text.replace('Chord*','Ms::Chord*').replace('Chord *','Ms::Chord *')
target=ROOT/'native'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(text.encode('utf8'))
