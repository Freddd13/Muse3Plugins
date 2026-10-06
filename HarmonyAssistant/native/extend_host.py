"""Apply the additive 1.1 host changes to personal-v0.2.0 (run once)."""
from pathlib import Path
R = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def edit(name, old, new):
    p=R/name
    s=p.read_text(encoding='utf-8-sig')
    assert old in s, (name,old[:80])
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s.replace(old,new,1))

# Destruction notifications originate in Element::~Element. Never dispatch type() there.
edit('mscore/scoreview.cpp', 'if (e->isNote()) _notePreviewLayers.remove(toNote(e));',
     '// Only compare opaque addresses: derived virtual functions are no longer available.\n      _notePreviewLayers.remove(static_cast<const Note*>(e));')

# QmlPlugin owns only a guarded reference to the existing dock, not another window.
edit('mscore/plugin/qmlplugin.h', 'namespace Ms {', 'class QDockWidget;\n\nnamespace Ms {')
edit('mscore/plugin/qmlplugin.h', '#include "libmscore/mscore.h"', '#include <QPointer>\n#include "libmscore/mscore.h"')
edit('mscore/plugin/qmlplugin.h', '      Q_OBJECT\n', '''      Q_OBJECT
      Q_PROPERTY(QString panelPlacement READ panelPlacement NOTIFY panelDockChanged)
      Q_PROPERTY(bool panelFloating READ panelFloating NOTIFY panelDockChanged)
      QPointer<QDockWidget> _panelDock;
      QString _panelPlacement;
''')
edit('mscore/plugin/qmlplugin.h', '      QmlPlugin(QQuickItem* parent = 0);', '''      QmlPlugin(QQuickItem* parent = 0);
      void attachPanelDock(QDockWidget* dock);
      QString panelPlacement() const { return _panelPlacement; }
      bool panelFloating() const;
      Q_INVOKABLE void setPanelFloating(bool floating);
   signals:
      void panelDockChanged();
   public:''')
edit('mscore/plugin/qmlplugin.cpp', '#include "qmlplugin.h"', '#include "qmlplugin.h"\n#include <QDockWidget>\n#include <QMainWindow>')
edit('mscore/plugin/qmlplugin.cpp', '\n}\n', '''
void QmlPlugin::attachPanelDock(QDockWidget* dock)
      {
      _panelDock = dock;
      auto location = [this](Qt::DockWidgetArea area) {
            _panelPlacement = area == Qt::TopDockWidgetArea ? "top" :
                  area == Qt::BottomDockWidgetArea ? "bottom" :
                  area == Qt::LeftDockWidgetArea ? "left" : "right";
            emit panelDockChanged();
            };
      connect(dock, &QDockWidget::dockLocationChanged, this, location);
      connect(dock, &QDockWidget::topLevelChanged, this, [this](bool) { emit panelDockChanged(); });
      if (auto main = qobject_cast<QMainWindow*>(dock->parentWidget())) location(main->dockWidgetArea(dock));
      }
bool QmlPlugin::panelFloating() const { return _panelDock && _panelDock->isFloating(); }
void QmlPlugin::setPanelFloating(bool floating)
      { if (_panelDock) { _panelDock->setFloating(floating); _panelDock->show(); } }

}
''')
edit('mscore/plugin/mscorePlugins.cpp', '                  addDockWidget(area, dock);',
     '                  addDockWidget(area, dock);\n                  p->attachPanelDock(dock);')

# Avoid repeated recursive traversal when the iterator already visits subdirectories.
edit('mscore/plugin/pluginManager.cpp', '            else\n                  updatePluginList(pluginPathList, path, pluginList);', '')

edit('mscore/notepreview.h', '#include <QHash>', '#include <QHash>\n#include <QFont>\n#include <QString>')
edit('mscore/notepreview.h', '      QRectF bounds;', '''      QRectF bounds;
      QString label;
      QString chord;
      QRectF labelBox;
      QRectF chordBox;
      bool active = false;''')
edit('mscore/notepreview.h', '{ return color == other.color && bounds == other.bounds; }',
     '{ return color == other.color && bounds == other.bounds && label == other.label && chord == other.chord\n                  && labelBox == other.labelBox && chordBox == other.chordBox && active == other.active; }')
edit('mscore/notepreview.h', 'class NotePreviewLayers {', '''inline QFont notePreviewFont(qreal spatium, bool chord)
      {
      QFont font("Arial");
      font.setPixelSize(qMax(5, qRound(spatium * (chord ? 1.35 : 1.0))));
      font.setBold(chord);
      return font;
      }

class NotePreviewLayers {''')
edit('mscore/notepreview.h', '      QColor color(const Note* note) const', '''      const NotePreviewEntry* entry(const Note* note) const
            {
            for (auto layer = _layers.crbegin(); layer != _layers.crend(); ++layer) {
                  auto item = layer->colors.constFind(note);
                  if (item != layer->colors.constEnd()) return &item.value();
                  }
            return nullptr;
            }
      QColor color(const Note* note) const''')
edit('mscore/scoreview.cpp', '''            const QColor preview = !_notePreviewLayers.empty() && e->isNote()
                  && !score()->printing() && !fotoMode()
                  ? _notePreviewLayers.color(toNote(e)) : QColor();''', '''            const auto previewEntry = !_notePreviewLayers.empty() && e->isNote()
                  && !score()->printing() && !fotoMode() ? _notePreviewLayers.entry(toNote(e)) : nullptr;
            const QColor preview = previewEntry ? previewEntry->color : QColor();''')
edit('mscore/scoreview.cpp', '            else e->draw(&painter);\n            painter.translate(-pos);', '''            else e->draw(&painter);
            if (previewEntry && e->visible()) {
                  auto drawLabel = [&](const QString& text, const QRectF& box, bool chord) {
                        if (box.isEmpty()) return;
                        painter.save();
                        painter.setFont(notePreviewFont(e->spatium(), chord));
                        painter.setPen(Qt::NoPen);
                        painter.setBrush(previewEntry->active ? QColor("#d0e2ff") : QColor(255,255,255,238));
                        painter.drawRoundedRect(box, e->spatium()*.18, e->spatium()*.18);
                        painter.setPen(previewEntry->active ? QColor("#0043ce") : QColor("#343a3f"));
                        painter.drawText(box, Qt::AlignCenter, text);
                        painter.restore();
                        };
                  drawLabel(previewEntry->label, previewEntry->labelBox, false);
                  drawLabel(previewEntry->chord, previewEntry->chordBox, true);
                  }
            painter.translate(-pos);''')

edit('mscore/plugin/api/scoreobserver.h', '      struct Event { int tick; int end; QVariantList notes; };', '''      struct Event { int tick; int end; QVariantList notes; };
      struct PedalWindow { int start; int end; int firstTrack; int endTrack; };
      QVector<PedalWindow> _pedals;
      QVector<int> _frameTicks;
      QString _fingerprint;
      QObject _baseOwner;
      void applyPreview(QObject* owner, const QVariantList& notes);
      Ms::Note* resolve(const QVariantMap& value) const;
      void clearPreview(QObject* owner);
      QVariantList contextNotes(int tick, int firstTrack, int endTrack, bool pedal, int windowTicks);
''')
edit('mscore/plugin/api/scoreobserver.h', '      Q_INVOKABLE void clearNotePreviewColors();', '''      Q_INVOKABLE void clearNotePreviewColors();
      Q_INVOKABLE void clearAllPreviews();
      Q_INVOKABLE void setScorePreview(const QVariantList& notes);
      Q_INVOKABLE QVariantMap contextSnapshot(int tick, int firstTrack, int endTrack, bool pedal, int windowTicks, bool sounding = false);
      Q_INVOKABLE QVariantMap analysisFrames(int fromTick, int limit, int firstTrack, int endTrack, bool pedal, int windowTicks);
      Q_INVOKABLE QVariantMap loadConfiguration(const QString& name) const;
      Q_INVOKABLE bool saveConfiguration(const QString& name, const QVariantMap& data) const;
      Q_INVOKABLE QString readTextFile(const QString& path) const;
      Q_INVOKABLE bool writeTextFile(const QString& path, const QString& text) const;''')
edit('mscore/plugin/api/scoreobserver.cpp', '#include <QElapsedTimer>', '''#include "libmscore/tie.h"
#include "libmscore/part.h"
#include "libmscore/spanner.h"
#include "libmscore/spannermap.h"
#include "libmscore/system.h"
#include "libmscore/page.h"
#include <QCryptographicHash>
#include <QDir>
#include <QFontMetricsF>
#include <QJsonDocument>
#include <QSaveFile>
#include <QStandardPaths>
#include <QUrl>
#include <QElapsedTimer>''')
edit('mscore/plugin/api/scoreobserver.cpp', 'ScoreObserver::~ScoreObserver() { clearNotePreviewColors(); }',
     'ScoreObserver::~ScoreObserver() { clearAllPreviews(); }')
# All lifecycle clears must include the full-score layer; selection clears keep it.
edit('mscore/plugin/api/scoreobserver.cpp', '      clearNotePreviewColors();\n      for (const auto& connection',
     '      clearAllPreviews();\n      for (const auto& connection')
edit('mscore/plugin/api/scoreobserver.cpp', 'if (!visible) clearNotePreviewColors();','if (!visible) clearAllPreviews();')
edit('mscore/plugin/api/scoreobserver.cpp', 'if (!item->isVisible()) clearNotePreviewColors();','if (!item->isVisible()) clearAllPreviews();')
edit('mscore/plugin/api/scoreobserver.cpp', 'if (!enabled) clearNotePreviewColors();','if (!enabled) clearAllPreviews();')
edit('mscore/plugin/api/scoreobserver.cpp', '                  clearNotePreviewColors();\n                  _score = nullptr;',
     '                  clearAllPreviews();\n                  _score = nullptr;')
edit('mscore/plugin/api/scoreobserver.cpp', '      _index.clear();\n      _index.resize',
     '      _index.clear();\n      _pedals.clear();\n      _frameTicks.clear();\n      QCryptographicHash hash(QCryptographicHash::Sha256);\n      _index.resize')
edit('mscore/plugin/api/scoreobserver.cpp', '''                  if (element->isChord())
                        for (const auto note : toChord(element)->notes())
                              event.notes.append(describe(note, note->pitch()));
                  _index[track - firstTrack].append(event);''', '''                  if (element->isChord())
                        for (const auto note : toChord(element)->notes()) {
                              auto descriptor = describe(note, note->pitch());
                              auto tail = note;
                              QSet<const Ms::Note*> visited;
                              while (tail->tieFor() && tail->tieFor()->endNote() && !visited.contains(tail)) {
                                    visited.insert(tail);
                                    tail = tail->tieFor()->endNote();
                                    }
                              descriptor.insert("end", tail->chord()->endTick().ticks());
                              event.notes.append(descriptor);
                              hash.addData(QByteArray::number(event.tick) + ":" + QByteArray::number(track) + ":"
                                    + QByteArray::number(note->pitch()) + ":" + QByteArray::number(note->tpc()) + ":"
                                    + QByteArray::number(tail->chord()->endTick().ticks()) + ";");
                              }
                  _frameTicks.append(event.tick);
                  _frameTicks.append(event.end);
                  _index[track - firstTrack].append(event);''')
edit('mscore/plugin/api/scoreobserver.cpp', '      _firstTrack = firstTrack;\n      _endTrack = endTrack;', '''      for (const auto& entry : _score->spannerMap().map()) {
            const auto spanner = entry.second;
            if (!spanner->isPedal()) continue;
            // A piano pedal normally spans the whole part, including both staves.
            auto part = _score->staff(spanner->staffIdx())->part();
            PedalWindow window {spanner->tick().ticks(), spanner->tick2().ticks(), part->startTrack(), part->endTrack()};
            _pedals.append(window);
            _frameTicks.append(window.start); _frameTicks.append(window.end);
            hash.addData(QByteArray::number(window.start) + ":pedal:" + QByteArray::number(window.end) + ";");
            }
      for (auto measure = _score->firstMeasure(); measure; measure = measure->nextMeasure())
            _frameTicks.append(measure->tick().ticks());
      std::sort(_frameTicks.begin(), _frameTicks.end());
      _frameTicks.erase(std::unique(_frameTicks.begin(), _frameTicks.end()), _frameTicks.end());
      _fingerprint = QString::fromLatin1(hash.result().toHex());
      _firstTrack = firstTrack;
      _endTrack = endTrack;''')

# Replace the previous preview implementation with a reusable pair of isolated view layers.
p=R/'mscore/plugin/api/scoreobserver.cpp'
s=p.read_text(encoding='utf-8')
start=s.index('void ScoreObserver::setNotePreviewColors(')
extension=Path(__file__).with_name('observer-extension.cpp.inc').read_text(encoding='utf-8')
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s[:start]+extension+'\n}\n}\n')
