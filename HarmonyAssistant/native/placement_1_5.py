# -*- coding: utf-8 -*-
"""One-time guarded host change; only generic screen layout and regression."""
from pathlib import Path
import shutil,subprocess,json
base=Path(__file__).resolve().parents[1]
repo=Path('E:/programming/funcodes/muse3_dev/MuseScore')
head=subprocess.check_output(['E:/Git/cmd/git.exe','-C',str(repo),'rev-parse','HEAD']).decode().strip()
assert head=='3dc1d38c837875befe292c7a73f4eecd82dd03cb'
names=['mscore/notepreview.h','mscore/plugin/api/scoreobserver.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp','mtest/mscore/pluginhost/tst_pluginhost.cpp','personal/USER_GUIDE.md']
for name in names:
    dest=base/'native/baseline-1.5'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    assert not dest.exists();shutil.copy2(str(repo/name),str(dest))
def write(p,s):
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=repo/'mscore/notepreview.h';s=p.read_text(encoding='utf-8');assert 'findPreviewChordBox' not in s
needle='class NotePreviewLayers {'
s=s.replace(needle,'''// Keep the rhythmic x. Each blocked candidate jumps above the actual obstacle edge.
// This searches the free vertical intervals, rather than sampling six fixed rows.
inline QRectF findPreviewChordBox(QRectF candidate,const QRectF& page,const QVector<QRectF>& obstacles,qreal gap)
      {
      if (candidate.isEmpty() || !page.contains(candidate)) return {};
      for (int step=0;step<=obstacles.size();++step) {
            qreal next=candidate.top();
            for (const auto& obstacle:obstacles)
                  if (obstacle.adjusted(-gap,-gap,gap,gap).intersects(candidate))
                        next=qMin(next,obstacle.top()-gap-candidate.height());
            if (next==candidate.top()) return candidate;
            candidate.moveTop(next);
            if (!page.contains(candidate)) return {};
            }
      return {};
      }

'''+needle);write(p,s)
p=repo/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('int hidden=0;QString fontFallback;','int hidden=0;QVariantList unplaced;QString fontFallback;',1)
start=s.index('                        auto& entry=markers[index];QRectF placed;')
end=s.index('                        entry.chordBox=placed.isEmpty()',start)
s=s[:start]+'''                        auto& entry=markers[index];
                        const QRectF preferred(positions[index].x(),top,entry.chordBox.width(),height);
                        const auto pageBounds=page->bbox();
                        const qreal gap=sp*.12;
                        QVector<QRectF> obstacles=occupied[page];
                        if (owner==this) obstacles+=_baseChordBoxes.value(page);
                        const QRectF corridor(preferred.left()-gap,pageBounds.top(),preferred.width()+2*gap,
                              qMax(qreal(0),preferred.bottom()-pageBounds.top()+gap));
                        for (const auto element:page->items(corridor)) {
                              if (!element->visible() || element->isPage() || element->isSystem() || element->isMeasure()) continue;
                              const auto box=element->pageBoundingRect();
                              if (!box.isEmpty())obstacles.append(box);
                              }
                        const auto placed=findPreviewChordBox(preferred,pageBounds,obstacles,gap);
''' + s[end:]
s=s.replace('if (placed.isEmpty()) ++hidden;','''if (placed.isEmpty()) {
                              ++hidden;
                              unplaced.append(QVariantMap{{"tick",entry.chordTick},{"track",entry.annotationTrack},
                                    {"chord",entry.chord},{"degree",entry.degree}});
                              }''',1)
s=s.replace('QVariantMap{{"hidden",hidden},{"fontFallback",fontFallback}}','QVariantMap{{"hidden",hidden},{"unplaced",unplaced},{"fontFallback",fontFallback}}',1)
write(p,s)
p=repo/'mtest/mscore/scoreobserver/tst_scoreobserver.cpp';s=p.read_text(encoding='utf-8');needle='      void boundedPedalMetadataAndNativeRenderingIsolation()'
s=s.replace(needle,'''      void adaptiveMarkerPlacement()
            {
            const QRectF page(0,0,500,500),preferred(120,300,80,20);
            QVector<QRectF> obstacles;
            for(int row=0;row<6;++row)obstacles.append(QRectF(110,300-row*40,100,2));
            for(int row=0;row<6;++row) {
                  const auto oldCandidate=preferred.translated(0,-row*40);
                  QVERIFY(std::any_of(obstacles.begin(),obstacles.end(),[&](const auto& box){return box.intersects(oldCandidate);}));
                  }
            const auto placed=findPreviewChordBox(preferred,page,obstacles,1);
            QVERIFY(!placed.isEmpty());QCOMPARE(placed.x(),preferred.x());QVERIFY(placed.y()<preferred.y());
            for(const auto box:obstacles)QVERIFY(!box.adjusted(-1,-1,1,1).intersects(placed));
            auto together=obstacles;together.append(placed);
            const auto second=findPreviewChordBox(preferred,page,together,1);
            QVERIFY(!second.isEmpty());QCOMPARE(second.x(),preferred.x());QVERIFY(!second.intersects(placed));
            QVERIFY(findPreviewChordBox(preferred,page,{QRectF(0,0,500,350)},1).isEmpty());
            }

'''+needle,1);write(p,s)
p=repo/'mtest/mscore/pluginhost/tst_pluginhost.cpp';s=p.read_text(encoding='utf-8').replace('QString("1.4.0")','QString("1.5.0")').replace('QLatin1String("1.4.0")','QLatin1String("1.5.0")')
s=s.replace('QCOMPARE(plugin->version(),QString("1.4.0"))','QCOMPARE(plugin->version(),QString("1.5.0"))')
# Existing actual GUI test also verifies explicit metadata for an out-of-page marker.
needle='            main->hide();\n            }\n      };'
assert needle in s
s=s.replace(needle,'''            first["chordScale"]=2.0;first["chord"]=QString(64,QChar('W'));first["degree"]="I";
            observer.setScorePreview({first});
            QCOMPARE(observer.previewStatus().value("hidden").toInt(),1);
            const auto unplaced=observer.previewStatus().value("unplaced").toList();
            QCOMPARE(unplaced.size(),1);QCOMPARE(unplaced.front().toMap().value("tick").toInt(),0);
            main->hide();
            }
      };''',1);write(p,s)
write(repo/'personal/VERSION','0.22.0\n')
for p in base.iterdir():
    if p.suffix in ('.qml','.js') or p.name=='README.md':shutil.copy2(str(p),str(repo/'share/plugins/HarmonyAssistant'/p.name))
print('Applied obstacle-edge layout, explicit overflow metadata and native regressions')
