from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'native/mscore/temposymbols.cpp';s=p.read_text(encoding='utf8')
a='const bool oldRit=cell->tag=="kumo-rit"||(factory&&(plain=="rit."||plain=="ritardando")),oldRestore=cell->tag=="kumo-a-tempo"||(factory&&plain=="a tempo");'
b='''const bool oldRit=cell->tag=="kumo-rit"||(factory&&(plain=="rit."||plain=="ritardando")&&(!e->isTextLine()||!toTextLine(e)->ritPlay()));
            const bool oldRestore=cell->tag=="kumo-a-tempo"||(factory&&plain=="a tempo"&&(!e->isTempoText()||toTempoText(e)->restoreMode()!=1));'''
assert a in s;s=s.replace(a,b,1).replace('(cell->custom&&!oldRit&&!oldRestore)','(cell->custom&&!factory&&!oldRit&&!oldRestore)',1);p.write_bytes(s.encode())
p=R/'native/mtest/mscore/performanceeditor/notation_051_tests.inc';s=p.read_text(encoding='utf8')
a='      auto restored=PalettePanel::readMimeData(tempo.mimeData());'
b='''      Element* liveRit=nullptr;Element* liveRestore=nullptr;for(int i=0;i<tempo.ncells();++i){auto e=tempo.cell(i)->element.get();if(!tempo.cell(i)->custom&&isPlayableTempoSymbol(e)){if(e->isTextLine())liveRit=e;else liveRestore=e;}}
      for(int pass=0;pass<3;++pass){appendPlayableTempoSymbols(&tempo);bool sameRit=false,sameRestore=false;for(int i=0;i<tempo.ncells();++i){sameRit|=tempo.cell(i)->element.get()==liveRit;sameRestore|=tempo.cell(i)->element.get()==liveRestore;}QVERIFY(sameRit);QVERIFY(sameRestore);}
      auto restored=PalettePanel::readMimeData(tempo.mimeData());'''
assert a in s;s=s.replace(a,b,1);p.write_bytes(s.encode())
