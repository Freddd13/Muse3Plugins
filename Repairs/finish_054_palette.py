from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
p=R/'native/mscore/temposymbols.cpp';s=p.read_text(encoding='utf8')
s=s.replace('const bool factory=!cell->custom;', 'const bool factory=!cell->custom||cell->name==QObject::tr("渐慢 rit.（可播放）")||cell->name==QObject::tr("a tempo（恢复渐变前的速度）")||cell->name.startsWith("Kumo rit");',1)
at=s.index('\nbool isPlayableTempoSymbol')
s=s[:at]+'''
void deduplicatePlayableTempoSymbols(PaletteTree* tree){
 if(!tree)return;PalettePanel* preferred=nullptr;for(const auto& p:tree->palettes)if(p->type()==PalettePanel::Type::Tempo){preferred=p.get();break;}
 if(!preferred)return;bool kept[2]={false,false};
 auto clean=[&](PalettePanel* panel){for(int i=0;i<panel->ncells();){auto cell=panel->cell(i);auto e=cell->element.get();
  const bool generated=cell->tag=="kumo-rit"||cell->tag=="kumo-a-tempo"||cell->name==QObject::tr("渐慢 rit.（可播放）")||cell->name==QObject::tr("a tempo（恢复渐变前的速度）");
  if(!e||!isPlayableTempoSymbol(e)||(!generated&&cell->custom)){++i;continue;}
  const int role=e->isTextLine()?0:1;if(kept[role])panel->takeCells(i,1);else{kept[role]=true;++i;}
 }};clean(preferred);for(const auto& p:tree->palettes)if(p.get()!=preferred)clean(p.get());
}
'''+s[at:];p.write_bytes(s.encode())
s=(H/'mscore/temposymbols.h').read_text(encoding='utf8').replace('class PalettePanel;','class PalettePanel;struct PaletteTree;').replace('void appendPlayableTempoSymbols(PalettePanel*);','void appendPlayableTempoSymbols(PalettePanel*);\nvoid deduplicatePlayableTempoSymbols(PaletteTree*);');stage('mscore/temposymbols.h',s)
s=(H/'mscore/palette/palettetree.cpp').read_text(encoding='utf8');at=s.index('bool PaletteTree::read(');where=s.index('      return true;',at);s=s[:where]+'      deduplicatePlayableTempoSymbols(this);\n'+s[where:];stage('mscore/palette/palettetree.cpp',s)
