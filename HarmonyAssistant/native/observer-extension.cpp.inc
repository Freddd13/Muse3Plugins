QVariantList ScoreObserver::contextNotes(int tick, int firstTrack, int endTrack, bool pedal, int windowTicks)
      {
      ensureIndex(firstTrack, endTrack);
      auto measure = _score->tick2measure(Fraction::fromTicks(tick));
      const int barStart = measure ? measure->tick().ticks() : 0;
      QMap<int, QVariant> notes; // Retain the most recent spelling/anchor for each MIDI pitch.
      for (int track = firstTrack; track < endTrack; ++track) {
            const auto& voice = _index[track - firstTrack];
            int start = qMax(barStart, tick - qBound(0, windowTicks, 1920));
            bool heldByPedal = false;
            if (pedal) for (const auto& window : _pedals)
                  if (track >= window.firstTrack && track < window.endTrack && window.start <= tick && tick < window.end) {
                        // Include a note already held when the pedal goes down.
                        start = qMin(start, window.start); heldByPedal = true;
                        }
            auto next = std::upper_bound(voice.cbegin(), voice.cend(), tick,
                  [](int value, const Event& event) { return value < event.tick; });
            while (next != voice.cbegin()) {
                  --next;
                  // Explicit rests terminate a non-pedal arpeggio window in this voice.
                  if (!heldByPedal && next->notes.isEmpty() && tick >= next->tick) break;
                  bool eligible = next->tick >= start || next->end > tick || (heldByPedal && next->end > start);
                  for (const auto& note : next->notes) {
                        const auto descriptor = note.toMap();
                        if (!eligible && descriptor.value("end").toInt() <= tick) continue;
                        const int pitch = descriptor.value("pitch").toInt();
                        if (!notes.contains(pitch)) notes.insert(pitch, descriptor);
                        }
                  if (next->tick < start && next->end <= start) break;
                  }
            }
      return notes.values();
      }

QVariantMap ScoreObserver::contextSnapshot(int tick, int firstTrack, int endTrack, bool pedal, int windowTicks, bool sounding)
      {
      auto result = snapshot(tick, firstTrack, endTrack, sounding);
      if (!_score || tick < 0) return result;
      firstTrack = qBound(0, firstTrack, _score->nstaves() * VOICES);
      endTrack = qBound(firstTrack, endTrack, _score->nstaves() * VOICES);
      auto context = contextNotes(tick, firstTrack, endTrack, pedal, windowTicks);
      // Actual playback events take precedence for instruments/transposed playback events.
      if (sounding && playing()) {
            QMap<int, QVariant> merged;
            for (const auto& note : context) merged.insert(note.toMap().value("pitch").toInt(), note);
            for (const auto& note : result.value("notes").toList()) merged.insert(note.toMap().value("pitch").toInt(), note);
            context = merged.values();
            }
      result.insert("analysisNotes", context);
      result.insert("fingerprint", _fingerprint);
      return result;
      }

QVariantMap ScoreObserver::analysisFrames(int fromTick, int limit, int firstTrack, int endTrack, bool pedal, int windowTicks)
      {
      QVariantMap result {{"frames", QVariantList()}, {"nextTick", -1}};
      if (!_score) return result;
      firstTrack = qBound(0, firstTrack, _score->nstaves() * VOICES);
      endTrack = qBound(firstTrack, endTrack, _score->nstaves() * VOICES);
      ensureIndex(firstTrack, endTrack);
      auto it = std::lower_bound(_frameTicks.cbegin(), _frameTicks.cend(), fromTick);
      QVariantList frames;
      for (int count = 0; it != _frameTicks.cend() && count < qBound(1, limit, 128); ++count, ++it)
            frames.append(contextSnapshot(*it, firstTrack, endTrack, pedal, windowTicks));
      result.insert("frames", frames);
      result.insert("nextTick", it == _frameTicks.cend() ? -1 : *it);
      result.insert("fingerprint", _fingerprint);
      return result;
      }

Ms::Note* ScoreObserver::resolve(const QVariantMap& value) const
      {
      const int track = value.value("track", -1).toInt(), index = value.value("index", -1).toInt();
      if (!_score || track < 0 || track >= _score->nstaves()*VOICES || index < 0) return nullptr;
      auto segment = _score->tick2segment(Fraction::fromTicks(value.value("tick", -1).toInt()), false, SegmentType::ChordRest);
      if (!segment) return nullptr;
      auto element = segment->element(track);
      if (!element || !element->isChord()) return nullptr;
      const auto& notes = toChord(element)->notes();
      if (index >= int(notes.size())) return nullptr;
      auto note = notes[index];
      if (note->pitch() != value.value("writtenPitch", value.value("pitch")).toInt() ||
            note->tpc() != value.value("writtenTpc", value.value("tpc")).toInt()) return nullptr;
      return note;
      }

void ScoreObserver::applyPreview(QObject* owner, const QVariantList& descriptors)
      {
      if (!_score || !_enabled || !_surfaceVisible) { clearPreview(owner); return; }
      NotePreviewColors colors;
      QHash<const Page*, QVector<QRectF>> occupied;
      for (const auto& descriptor : descriptors) {
            const auto value = descriptor.toMap();
            auto note = resolve(value);
            if (!note || !note->visible()) continue;
            const qreal sp = note->spatium();
            auto system = note->chord()->measure()->system();
            if (!system) continue;
            auto page = system->page();
            if (!page) continue;
            NotePreviewEntry entry {QColor(value.value("color").toString()), note->canvasBoundingRect().adjusted(-sp, -sp, sp, sp)};
            entry.label = value.value("label").toString().left(24);
            entry.chord = value.value("chord").toString().left(64);
            entry.active = value.value("active").toBool();
            const QFont font = notePreviewFont(sp, false);
            const QFont chordFont = notePreviewFont(sp, true);
            const QPointF anchor = note->pagePos();
            // Use the page's spatial index once when the layer changes, never on each repaint.
            auto place = [&](const QString& text, const QFont& f, bool chord) {
                  if (text.isEmpty()) return QRectF();
                  QFontMetricsF metrics(f);
                  const QSizeF size(metrics.horizontalAdvance(text) + sp*0.5, metrics.height() + sp*0.2);
                  const qreal top = system->staffYpage(note->chord()->vStaffIdx());
                  for (int lane = 0; lane < 24; ++lane) {
                        const qreal y = chord ? qMin(top-sp*2, anchor.y()-sp*2) - lane*sp*1.3 :
                              anchor.y()-size.height()/2 + (lane == 0 ? 0 : ((lane+1)/2)*(lane%2 ? -1 : 1)*sp*1.2);
                        QRectF candidate(chord ? anchor.x() : anchor.x()+note->bbox().right()+sp*0.45, y, size.width(), size.height());
                        if (!page->bbox().contains(candidate)) continue;
                        bool collision = false;
                        for (const auto& box : occupied[page]) if (box.adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) { collision=true; break; }
                        if (collision) continue;
                        for (const auto element : page->items(candidate)) {
                              if (!element->visible() || element->isStaffLines() || element->isPage() || element->isSystem() || element->isMeasure()) continue;
                              if (element->pageBoundingRect().adjusted(-sp*.12,-sp*.12,sp*.12,sp*.12).intersects(candidate)) { collision=true; break; }
                              }
                        if (collision) continue;
                        occupied[page].append(candidate);
                        return candidate.translated(-anchor);
                        }
                  // In a fully occupied margin, omit rather than cover notation.
                  return QRectF();
                  };
            entry.labelBox = place(entry.label, font, false);
            entry.chordBox = place(entry.chord, chordFont, true);
            entry.bounds |= entry.labelBox.translated(note->canvasPos());
            entry.bounds |= entry.chordBox.translated(note->canvasPos());
            colors.insert(note, entry);
            }
      for (auto viewer : _score->getViewer()) {
            auto view = dynamic_cast<Ms::ScoreView*>(viewer);
            if (!view) continue;
            view->setNotePreviewColors(owner, colors);
            if (!_previewViews.contains(view)) _previewViews.append(view);
            }
      }

void ScoreObserver::setNotePreviewColors(const QVariantList& notes) { applyPreview(this, notes); }
void ScoreObserver::setScorePreview(const QVariantList& notes) { applyPreview(&_baseOwner, notes); }
void ScoreObserver::clearPreview(QObject* owner)
      { for (auto& view : _previewViews) if (view) view->setNotePreviewColors(owner, {}); }
void ScoreObserver::clearNotePreviewColors() { clearPreview(this); }
void ScoreObserver::clearAllPreviews()
      { clearPreview(this); clearPreview(&_baseOwner); _previewViews.clear(); }

static QString localPath(const QString& path)
      { const QUrl url(path); return url.isLocalFile() ? url.toLocalFile() : path; }
QString ScoreObserver::readTextFile(const QString& path) const
      {
      QFile file(localPath(path));
      if (!file.open(QIODevice::ReadOnly) || file.size() > 16*1024*1024) return QString();
      return QString::fromUtf8(file.readAll());
      }
bool ScoreObserver::writeTextFile(const QString& path, const QString& text) const
      {
      QSaveFile file(localPath(path));
      if (!file.open(QIODevice::WriteOnly)) return false;
      const auto bytes = text.toUtf8();
      return file.write(bytes) == bytes.size() && file.commit();
      }
static QString configurationPath(const QString& name)
      {
      if (name.isEmpty() || name.contains('/') || name.contains('\\') || name.contains("..")) return QString();
      const auto directory = QStandardPaths::writableLocation(QStandardPaths::AppConfigLocation) + "/plugin-settings";
      if (!QDir().mkpath(directory)) return QString();
      return directory + "/" + name + ".json";
      }
QVariantMap ScoreObserver::loadConfiguration(const QString& name) const
      { return QJsonDocument::fromJson(readTextFile(configurationPath(name)).toUtf8()).toVariant().toMap(); }
bool ScoreObserver::saveConfiguration(const QString& name, const QVariantMap& data) const
      { return writeTextFile(configurationPath(name), QString::fromUtf8(QJsonDocument::fromVariant(data).toJson())); }
