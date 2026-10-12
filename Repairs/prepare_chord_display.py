# coding: utf-8
from pathlib import Path
host=Path('E:/programming/funcodes/muse3_dev/MuseScore');r=Path('Repairs/native')
for name in ['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp']:
 p=r/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_bytes((host/name).read_bytes())
p=r/'mscore/notepreview.h';s=p.read_text(encoding='utf8').replace('      bool chordMask = true;','      bool chordMask = true;\n      bool onTop = false, avoidScoreContent = true;',1).replace('&& highlightBackground == other.highlightBackground && chordMask == other.chordMask','&& highlightBackground == other.highlightBackground && chordMask == other.chordMask\n                  && onTop == other.onTop && avoidScoreContent == other.avoidScoreContent',1)
marker='\nclass NotePreviewLayers {'
fn='''
// Screen annotations keep their exact rhythmic x, even when the preferred row
// cannot fit above a page's title. Never omit an opted-in annotation.
inline QRectF stackVisiblePreviewChord(QRectF preferred,const QRectF& page,const QVector<QRectF>& own,qreal gap)
      {
      auto lift=[&](QRectF candidate,bool up){
            for(int step=0;step<=own.size();++step){qreal next=candidate.top();
                  for(const auto& obstacle:own)if(obstacle.adjusted(-gap,-gap,gap,gap).intersects(candidate))
                        next=up?qMin(next,obstacle.top()-gap-candidate.height()):qMax(next,obstacle.bottom()+gap);
                  if(next==candidate.top())return candidate;candidate.moveTop(next);
                  }
            return candidate;
            };
      auto above=lift(preferred,true);if(above.top()>=page.top())return above;
      auto below=lift(preferred,false);if(below.bottom()<=page.bottom())return below;
      // Extreme density can extend past the page; the score can still be panned.
      // This is a temporary display layer and never changes page layout or PDF.
      return above;
      }
'''
assert s.count(marker)==1;s=s.replace(marker,'\n'+fn+marker);p.write_bytes(s.encode('utf8'))
p=r/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf8').replace('entry.sourceAnchor=note;entry.chordMask=value.value("chordMask",true).toBool();','entry.sourceAnchor=note;entry.chordMask=value.value("chordMask",true).toBool();\n            entry.onTop=value.value("onTop",false).toBool();entry.avoidScoreContent=value.value("avoidScoreContent",true).toBool();',1)
s=s.replace('                        for (const auto element:page->items(corridor)) {','                        if(entry.avoidScoreContent)for (const auto element:page->items(corridor)) {',1)
a='                        const auto placed=findPreviewChordBox(preferred,pageBounds,obstacles,gap);'
b='''                        auto placed=entry.avoidScoreContent?findPreviewChordBox(preferred,pageBounds,obstacles,gap):stackVisiblePreviewChord(preferred,pageBounds,chordBoxes[page],gap);
                        if(placed.isEmpty()&&entry.onTop)placed=stackVisiblePreviewChord(preferred,pageBounds,chordBoxes[page],gap);'''
assert s.count(a)==1;s=s.replace(a,b);p.write_bytes(s.encode('utf8'))
# The normal native draw path remains unchanged for older / third-party layers.
p=Path('Repairs/apply_native.py');s=p.read_text(encoding='utf8');marker=" patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/referencefactory.h'"
# Insert independent drawing source and the two thin ScoreView hooks.
start=s.index(marker)
s=s[:start]+''' patch('mscore/CMakeLists.txt','      scoreview.cpp editharmony.cpp editfiguredbass.cpp events.cpp','      scoreview.cpp workflow/chordoverlay.cpp editharmony.cpp editfiguredbass.cpp events.cpp')
 patch('mscore/scoreview.h','      QRectF previewEditBounds() const;','      QRectF previewEditBounds() const;\\n      void paintTopChordPreview(QPainter&);')
 patch('mscore/scoreview.cpp','      PerformanceEditor::paintForView(this, vp);','      PerformanceEditor::paintForView(this, vp);\\n      paintTopChordPreview(vp);')
 patch('mscore/scoreview.cpp','if (!box.intersects(fr) || box.intersects(protectedArea)) return;','if (entry.onTop || !box.intersects(fr) || box.intersects(protectedArea)) return;')
 patch('mscore/plugin/qmlplugin.cpp','qBound(80,preferred,400)','qBound(40,preferred,400)')
'''+s[start:];p.write_bytes(s.encode('utf8'))
