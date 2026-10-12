from pathlib import Path
path=Path(__file__).resolve().parent/'native/mtest/mscore/p0native/tst_p0native.cpp'
s=path.read_text(encoding='utf8')
line='            auto previousView=mscore->currentScoreView();const bool previouslyVisible=mscore->isVisible();\n'
assert s.count(line)==1;s=s.replace(line,'')
start=s.index('            auto sample=mscore->readScore(')
end=s.index('            mscore->setCurrentScoreView(previousView);if(!previouslyVisible)mscore->hide();',start)+len('            mscore->setCurrentScoreView(previousView);if(!previouslyVisible)mscore->hide();\n')
body=line+s[start:end]
s=s[:start]+s[end:]
at=s.rfind('};')
s=s[:at]+'      void notationPictures()\n            {\n'+body+'            }\n'+s[at:]
path.write_bytes(s.encode('utf8'))
