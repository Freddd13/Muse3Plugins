from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-161'
record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
def edit(name,old,new):
    path=NATIVE/name
    if not path.is_file():path.write_bytes((HOST/name).read_bytes())
    if name not in files:files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest()
    text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError(name+' missing section')
    path.write_bytes(text.replace(old,new,1).encode('utf8'))
edit('libmscore/rendermidi.h','      int minChunkSize = 0;','      int minChunkSize = 0;\n      int _timingLookahead = 0;')
edit('libmscore/rendermidi.h','      Chunk getChunkAt(int utick);','      Chunk getChunkAt(int utick);\n      int timingLookahead() { updateState(); return _timingLookahead; }')
edit('libmscore/rendermidi.cpp','      chunks.clear();','      chunks.clear();\n      _timingLookahead = PerformanceTiming::lookahead(score);')
edit('mscore/seq.cpp','unrenderedUtick - utick < minUtickBufferSize)', 'unrenderedUtick - utick < minUtickBufferSize + midi.timingLookahead())')
# Both initial preparation and the running background renderer use the same horizon.
edit('mscore/seq.cpp','if (unrenderedUtick - utick < minUtickBufferSize)', 'if (unrenderedUtick - utick < minUtickBufferSize + midi.timingLookahead())')
record.write_text(json.dumps(files,indent=2),encoding='utf8')
print('Prepared timing lookahead for continuous playback')
