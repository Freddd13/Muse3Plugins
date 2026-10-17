"""Refresh only the P2 source index and documentation copies before applying."""
from pathlib import Path
import csv,io,shutil
R=Path(__file__).resolve().parent
H=R.parent.parent/'muse3_dev/MuseScore'
index=R/'native/personal/docs/source-map.tsv'
rows=list(csv.DictReader(io.StringIO(index.read_text('utf8')),delimiter='\t'))
rows += [
 dict(topic='频谱分段计算',path='mscore/referenceaudio/spectrum.cpp',symbol='SpectrumTile spectrum(',line='1',role='Hann 窗、各声道能量、对数音高、分段读取',tests='mtest/mscore/spectrum/tst_spectrum.cpp'),
 dict(topic='频谱任务与缓存',path='mscore/referenceaudio/spectrumsession.cpp',symbol='void ReferenceSpectrumSession::request(',line='1',role='取消旧任务、有界缓存、独立工作线程',tests='mtest/mscore/spectrum/tst_spectrum.cpp'),
 dict(topic='扒谱交互',path='mscore/performanceeditor/spectrumpane.cpp',symbol='SpectrumPane::SpectrumPane(',line='1',role='原曲片段、取音、音符输入、上下与叠加',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
 dict(topic='扒谱标注保存',path='mscore/performanceeditor/spectrumpane.cpp',symbol='void SpectrumPane::saveMarks(',line='1',role='频率与音名、原生撤销、MSCZ 元数据',tests='mtest/mscore/pluginhost/tst_pluginhost.cpp'),
]
seen=set();result=[]
for row in rows:
 key=(row['path'],row['symbol'])
 if key in seen:continue
 seen.add(key);file=R/'native'/row['path']
 if not file.exists():file=H/row['path']
 if file.exists() and row['symbol']!='-':
  lines=[i+1 for i,s in enumerate(file.read_text('utf8',errors='replace').splitlines()) if row['symbol'] in s]
  if lines:row['line']=str(min(lines,key=lambda n:abs(n-int(row['line']))))
 result.append(row)
out=io.StringIO();writer=csv.DictWriter(out,fieldnames=['topic','path','symbol','line','role','tests'],delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(result);index.write_bytes(out.getvalue().encode('utf8'))
for name in ('transcription-separate-059.png','transcription-overlay-059.png'):
 source=R.parent/'P1/out/final-regression'/name
 if source.exists():
  for folder in (R/'docs/images',R/'native/personal/docs/images'):
   folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,folder/name)
print('Updated',len(result),'source entries and spectrum screenshots')
