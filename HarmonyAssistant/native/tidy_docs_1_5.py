from pathlib import Path
import csv
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore');base=Path(__file__).resolve().parents[1]
for p in [repo/'personal/USER_GUIDE.md',repo/'personal/docs/10-score-observer.md',base/'native/user-guide-index-1.5.md']:
    p.write_bytes((p.read_text(encoding='utf-8').rstrip()+'\n').encode('utf-8'))
p=repo/'personal/docs/source-map.tsv';lines=p.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines[1:],1):
    cells=line.split('\t')
    if len(cells)==6 and cells[1].startswith('share/plugins/HarmonyAssistant/'):
        source=(repo/cells[1]).read_text(encoding='utf-8').splitlines()
        anchor=next(csv.reader([line],delimiter='\t'))[2]
        hits=[n+1 for n,text in enumerate(source) if anchor in text]
        assert hits,cells;cells[3]=str(hits[0]);lines[i]='\t'.join(cells)
p.write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
(repo/'share/plugins/HarmonyAssistant/README.md').write_bytes((base/'README.md').read_bytes())
print('Task-owned source anchors and trailing whitespace corrected; unrelated guide links preserved')
