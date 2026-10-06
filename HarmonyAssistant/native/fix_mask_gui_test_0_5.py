from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8')
needle='            const auto masked=view->grab(fixedArea).toImage();'
assert needle in s;s=s.replace(needle,'            observer.setActiveScorePreview(600); // white inactive mask over white paper is visually identical\n'+needle,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
