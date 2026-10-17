from pathlib import Path
R=Path(__file__).resolve().parent;H=R.parent.parent/'muse3_dev/MuseScore'
def read(k):
 p=R/'native'/k
 return (p if p.exists() else H/k).read_text(encoding='utf8')
def stage(k,s):
 p=R/'native'/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
stage('mscore/workflow/harmonytypography.h','''// GPL-2.0-or-later. Temporary annotations share a horizontal root/slash/bass layout.
#pragma once
#include "libmscore/score.h"
#include "libmscore/chordlist.h"
namespace Ms {
inline void alignTemporaryHarmonyBass(MasterScore& scratch){
 for(auto& action:scratch.style().chordList()->renderListBase)
  if(action.type==RenderAction::RenderActionType::MOVE)action.movey=0;
}
}
''')
s=read('mscore/workflow/harmonylabel.cpp').replace('#include "libmscore/chordlist.h"','#include "harmonytypography.h"',1).replace('for(auto& action:scratch.style().chordList()->renderListBase)if(action.type==RenderAction::RenderActionType::MOVE)action.movey=0;','alignTemporaryHarmonyBass(scratch);',1);stage('mscore/workflow/harmonylabel.cpp',s)
s=read('mscore/plugin/api/scoreobserver.cpp');s='#include "mscore/workflow/harmonytypography.h"\n'+s
s=s.replace('                              scratch->style().checkChordList();','                              scratch->style().checkChordList();alignTemporaryHarmonyBass(*scratch);',1)
s=s.replace('NotePreviewEntry glyphs;glyphs.renderedChordSize=nativeBox.size();','NotePreviewEntry glyphs;glyphs.renderedChordSize=nativeBox.size();glyphs.chordBaseline=-nativeBox.top();',1)
s=s.replace('entry.renderedChordKey=glyphs.renderedChordKey;','entry.renderedChordKey=glyphs.renderedChordKey;entry.chordBaseline=glyphs.chordBaseline;',1)
s=s.replace('            entry.chordBox=QRectF(QPointF(),layoutPreviewChord(','''            QFont unitDegree(entry.degreeFont);unitDegree.setPixelSize(100);
            const qreal capital=QFontMetricsF(entry.chordFont,MScore::paintDevice()).capHeight();
            entry.degreeFont.setPixelSize(qMax(5,qRound(100*capital/qMax(1.,QFontMetricsF(unitDegree).capHeight()))));
            entry.chordBox=QRectF(QPointF(),layoutPreviewChord(''',1);stage('mscore/plugin/api/scoreobserver.cpp',s)
s=read('mscore/notepreview.h').replace('      QRectF chordBox;', '      QRectF chordBox;\n      qreal chordBaseline=0;',1).replace('&& renderedChordKey == other.renderedChordKey','&& chordBaseline==other.chordBaseline && renderedChordKey == other.renderedChordKey',1)
s=s.replace('      const QSizeF combined(vertical ?', '      const qreal aBase=entry.renderedChordSize.isEmpty()?QFontMetricsF(entry.chordFont).ascent():entry.chordBaseline,bBase=QFontMetricsF(entry.degreeFont).ascent(),ascent=qMax(aBase,bBase),descent=qMax(a.height()-aBase,b.height()-bBase);\n      const QSizeF combined(vertical ?',1)
s=s.replace('vertical ? a.height()+b.height()+gap*.5 : qMax(a.height(),b.height())','vertical ? a.height()+b.height()+gap*.5 : ascent+descent',1)
s=s.replace('padding+(combined.height()-a.height())/2,a.width(),a.height()','padding+ascent-aBase,a.width(),a.height()',1).replace('padding+(combined.height()-b.height())/2,b.width(),b.height()','padding+ascent-bBase,b.width(),b.height()',1);stage('mscore/notepreview.h',s)
