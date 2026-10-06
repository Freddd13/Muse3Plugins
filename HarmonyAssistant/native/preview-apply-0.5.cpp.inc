// A tick without a written onset still has a stable horizontal location in its measure.
// Prefer actual segment positions; interpolate only between neighboring rhythmic positions.
static qreal previewTickX(const Ms::Measure* measure, int tick, const Ms::Segment** exact)
      {
      qreal left=0,right=measure->width();
      int leftTick=measure->tick().ticks(),rightTick=measure->endTick().ticks();
      *exact=nullptr;
      for (auto segment=measure->first(SegmentType::ChordRest);segment;segment=segment->next(SegmentType::ChordRest)) {
            if (!segment->enabled()) continue;
            const int position=segment->tick().ticks();
            if (position==tick) {*exact=segment;return segment->pagePos().x();}
            if (position>tick) {right=segment->x();rightTick=position;break;}
            left=segment->x();leftTick=position;
            }
      const qreal amount=rightTick>leftTick ? qBound(qreal(0),qreal(tick-leftTick)/(rightTick-leftTick),qreal(1)) : 0;
      return measure->pagePos().x()+left+(right-left)*amount;
      }

void ScoreObserver::applyPreview(QObject* owner, const QVariantList& descriptors)
      {
      if (!_score || !_enabled || !_surfaceVisible) { clearPreview(owner); return; }
      NotePreviewColors colors;
      NotePreviewMarkers markers;
      QVector<QPointF> positions;
      QHash<int,Ms::Segment*> segments;
      QMap<int,Ms::Measure*> measures;
      if (descriptors.size()>64) {
            for (auto segment=_score->firstSegment(SegmentType::ChordRest);segment;segment=segment->next1(SegmentType::ChordRest))
                  segments.insert(segment->tick().ticks(),segment);
            for (auto measure=_score->firstMeasure();measure;measure=measure->nextMeasure())
                  measures.insert(measure->tick().ticks(),measure);
            }
      QHash<const Page*,QVector<QRectF>> occupied,chordBoxes;
      QHash<const System*,QMap<int,QVector<int>>> groups;
      for (const auto& descriptor : descriptors) {
            const auto value=descriptor.toMap();
            auto note=resolve(value,descriptors.size()>64 ? &segments : nullptr);
            if (!note || !note->visible()) continue;
            const qreal sp=note->spatium();
            auto system=note->chord()->measure()->system();
            auto page=system ? system->page() : nullptr;
            if (!page) continue;
            NotePreviewEntry entry {QColor(value.value("color").toString()),note->canvasBoundingRect().adjusted(-sp,-sp,sp,sp)};
            entry.label=value.value("label").toString().left(24);
            entry.active=value.value("active").toBool();
            entry.anchor=note->canvasPos();entry.spatium=sp;
            const QPointF anchor=note->pagePos();
            auto collides=[&](const QRectF& candidate) {
                  if (!page->bbox().contains(candidate)) return true;
                  if (owner==this) for (const auto& box : _baseChordBoxes.value(page))
                        if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) return true;
                  for (const auto& box : occupied[page])
                        if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) return true;
                  for (const auto element : page->items(candidate)) {
                        if (!element->visible() || element->isStaffLines() || element->isPage() || element->isSystem() || element->isMeasure()) continue;
                        if (element->pageBoundingRect().adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) return true;
                        }
                  return false;
                  };
            const auto base=_baseColors.constFind(note);
            if (!entry.label.isEmpty()) {
                  if (owner==this && base!=_baseColors.constEnd() && base->anchor==entry.anchor && base->spatium==sp && base->label==entry.label)
                        entry.labelBox=base->labelBox;
                  else {
                        QFontMetricsF metrics(notePreviewFont(sp,false));
                        const QSizeF size(metrics.horizontalAdvance(entry.label)+sp*.5,metrics.height()+sp*.2);
                        for (int lane=0;lane<7;++lane) {
                              const qreal y=anchor.y()-size.height()/2+(lane==0 ? 0 : ((lane+1)/2)*(lane%2 ? -1 : 1)*sp*1.2);
                              const QRectF candidate(anchor.x()+note->bbox().right()+sp*.45,y,size.width(),size.height());
                              if (collides(candidate)) continue;
                              occupied[page].append(candidate);entry.labelBox=candidate.translated(-anchor);break;
                              }
                        }
                  }
            entry.bounds |= entry.labelBox.translated(entry.anchor);
            if (entry.color.isValid() || !entry.label.isEmpty() || entry.active) colors.insert(note,entry);
            entry.chord=value.value("chord").toString().left(64);entry.degree=value.value("degree").toString().left(24);
            if (entry.chord.isEmpty() && entry.degree.isEmpty()) continue;
            entry.chordTick=qMax(0,value.value("chordTick",note->chord()->tick().ticks()).toInt());
            entry.chordUntil=qMax(entry.chordTick,value.value("chordUntil",INT_MAX).toInt());
            Ms::Measure* measure=nullptr;
            if (descriptors.size()>64) {
                  auto it=measures.upperBound(entry.chordTick);
                  if (it!=measures.begin()) measure=*--it;
                  }
            else measure=_score->tick2measure(Fraction::fromTicks(entry.chordTick));
            if (!measure || entry.chordTick>=measure->endTick().ticks() || !measure->system()) continue;
            system=measure->system();page=system->page();if (!page) continue;
            const Ms::Segment* exact=nullptr;
            const qreal x=previewTickX(measure,entry.chordTick,&exact);
            if (exact && value.value("preferExistingHarmony").toBool())
                  for (const auto annotation : exact->annotations()) {
                        if (!annotation->visible() || !annotation->isHarmony() || !annotation->staff()
                              || annotation->staff()->part()!=note->staff()->part()) continue;
                        const auto harmony=toHarmony(annotation);
                        if (harmony->harmonyName().trimmed().isEmpty()) continue;
                        if (harmony->harmonyType()==HarmonyType::ROMAN) entry.degree.clear();else entry.chord.clear();
                        }
            if (entry.chord.isEmpty() && entry.degree.isEmpty()) continue;
            entry.annotationTrack=note->staff()->part()->startTrack();entry.activationTarget=this;
            entry.sourceAnchor=note;entry.chordMask=value.value("chordMask",true).toBool();
            entry.label.clear();entry.labelBox={};entry.color={};entry.active=false;entry.bounds={};
            // This anchor belongs to the change's system, even if its sustained source note is on a prior line.
            const QPointF position(x,system->staffYpage(entry.annotationTrack/VOICES));
            entry.anchor=position+page->pos();
            QString family=value.value("chordFont").toString().left(64);
            if (family.isEmpty()) family=_score->styleSt(Sid::chordSymbolAFontFace);
            qreal scale=value.value("chordScale",1.0).toDouble();
            if (!qIsFinite(scale) || scale<.6 || scale>2.) scale=1.;
            entry.chordFont=QFont(family);entry.chordFont.setPixelSize(qMax(5,qRound(sp*1.65*scale)));
            entry.chordFont.setLetterSpacing(QFont::AbsoluteSpacing,-sp*.02);
            entry.degreeFont=QFont("Arial");entry.degreeFont.setPixelSize(qMax(5,qRound(sp*1.45*scale)));
            auto readColor=[&](const char* key,const QColor& fallback) {
                  const QColor color(value.value(key).toString());return color.isValid() ? color : fallback;
                  };
            entry.chordColor=readColor("chordColor",entry.chordColor);
            entry.highlightColor=readColor("highlightColor",entry.highlightColor);
            entry.highlightBackground=readColor("highlightBackground",entry.highlightBackground);
            entry.chordBox=QRectF(QPointF(),layoutPreviewChord(entry,qBound(0,value.value("chordOrder").toInt(),3)));
            groups[system][entry.annotationTrack].append(markers.size());markers.append(entry);positions.append(position);
            }
      // One shared row per system/part. No horizontal nudging: x remains the harmonic change's tick.
      for (auto systemIt=groups.cbegin();systemIt!=groups.cend();++systemIt) {
            const auto system=systemIt.key();const auto page=system->page();
            for (auto groupIt=systemIt->cbegin();groupIt!=systemIt->cend();++groupIt) {
                  auto group=groupIt.value();
                  std::sort(group.begin(),group.end(),[&](int a,int b){return markers[a].chordTick<markers[b].chordTick;});
                  const qreal sp=markers[group.front()].spatium;
                  qreal height=0;for (int index:group) height=qMax(height,markers[index].chordBox.height());
                  const qreal top=system->staffYpage(groupIt.key()/VOICES)-sp*1.5-height;
                  QVector<QRectF> best;int bestCount=-1;
                  for (int lane=0;lane<4;++lane) {
                        QVector<QRectF> boxes;int count=0;
                        for (int index:group) {
                              const auto& entry=markers[index];
                              const QRectF candidate(positions[index].x(),top-lane*sp*1.3,entry.chordBox.width(),height);
                              bool collision=!page->bbox().contains(candidate);
                              if (owner==this) for (const auto& box:_baseChordBoxes.value(page))
                                    if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)){collision=true;break;}
                              for (const auto& box:boxes) if (!box.isEmpty() && box.adjusted(-sp*.2,0,sp*.2,0).intersects(candidate)){collision=true;break;}
                              if (!collision) for (const auto& box:occupied[page])
                                    if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)){collision=true;break;}
                              if (!collision) for (const auto element:page->items(candidate)) {
                                    if (!element->visible() || element->isStaffLines() || element->isPage() || element->isSystem() || element->isMeasure()) continue;
                                    if (element->pageBoundingRect().adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)){collision=true;break;}
                                    }
                              boxes.append(collision ? QRectF() : candidate);if (!collision)++count;
                              }
                        if (count>bestCount){bestCount=count;best=boxes;}
                        if (count==group.size()) break;
                        }
                  for (int i=0;i<group.size();++i) {
                        auto& entry=markers[group[i]];
                        entry.chordBox=best[i].isEmpty() ? QRectF() : best[i].translated(-positions[group[i]]);
                        if (!best[i].isEmpty()){occupied[page].append(best[i]);chordBoxes[page].append(best[i]);}
                        entry.bounds=entry.chordBox.isEmpty() ? QRectF() : entry.chordBox.translated(entry.anchor);
                        }
                  }
            }
      if (owner==&_baseOwner){_baseColors=colors;_baseChordBoxes=chordBoxes;}
      for (auto viewer:_score->getViewer()) {
            auto view=dynamic_cast<Ms::ScoreView*>(viewer);if (!view) continue;
            view->setNotePreviewColors(owner,colors,markers);
            if (owner==&_baseOwner) view->setActiveNotePreview(owner,_activePreviewTick);
            if (!_previewViews.contains(view)) _previewViews.append(view);
            }
      }

