# -*- coding: utf-8 -*-
"""One-time native migration after the 0.4.1 collision fix; do not repeat."""
from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore');here=Path(__file__).resolve().parent
def write(p,s):
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
def edit(name,old,new):
    p=repo/name;s=p.read_text(encoding='utf-8');assert old in s,(name,old);write(p,s.replace(old,new,1))
write(repo/'mscore/notepreview.h',(here/'notepreview-0.5.h.inc').read_text(encoding='utf-8-sig'))
p=repo/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
start=s.index('void ScoreObserver::applyPreview(');end=s.index('void ScoreObserver::setActiveScorePreview(',start)
write(p,s[:start]+(here/'preview-apply-0.5.cpp.inc').read_text(encoding='utf-8')+'\n'+s[end:])
edit('mscore/scoreview.h','void setNotePreviewColors(QObject* owner, const NotePreviewColors& colors);',
     'void setNotePreviewColors(QObject* owner, const NotePreviewColors& colors, const NotePreviewMarkers& markers = {});')
edit('mscore/scoreview.cpp','void ScoreView::setNotePreviewColors(QObject* owner, const NotePreviewColors& colors)',
     'void ScoreView::setNotePreviewColors(QObject* owner, const NotePreviewColors& colors, const NotePreviewMarkers& markers)')
edit('mscore/scoreview.cpp','!_notePreviewOwners.contains(owner) && !colors.isEmpty()',
     '!_notePreviewOwners.contains(owner) && (!colors.isEmpty() || !markers.isEmpty())')
edit('mscore/scoreview.cpp','_notePreviewLayers.replace(owner, colors);','_notePreviewLayers.replace(owner, colors, markers);')
edit('mscore/scoreview.cpp','''                  p.setPen(Qt::NoPen);
                  p.setBrush(active ? entry.highlightBackground : QColor(255,255,255,235));
                  p.drawRoundedRect(QRectF(QPointF(),box.size()),entry.spatium*.18,entry.spatium*.18);''',
'''                  if (entry.chordMask) {
                        p.setPen(Qt::NoPen);
                        p.setBrush(active ? entry.highlightBackground : QColor(255,255,255,235));
                        p.drawRoundedRect(QRectF(QPointF(),box.size()),entry.spatium*.18,entry.spatium*.18);
                        }''')

edit('mscore/plugin/qmlplugin.h','class QDockWidget;','class QDockWidget;\nclass QQuickWindow;')
edit('mscore/plugin/qmlplugin.h','      QPointer<QDockWidget> _panelDock;',
'''      Q_PROPERTY(QQuickItem* detailPanelHost READ detailPanelHost NOTIFY panelDetailChanged)
      Q_PROPERTY(bool detailPanelVisible READ detailPanelVisible NOTIFY panelDetailChanged)
      QPointer<QDockWidget> _panelDock;
      QPointer<QDockWidget> _detailDock;
      QPointer<QQuickWindow> _detailWindow;''')
edit('mscore/plugin/qmlplugin.h','      QString _filePath;',
     '      bool eventFilter(QObject* object, QEvent* event) override;\n      QString _filePath;')
edit('mscore/plugin/qmlplugin.h','      Q_INVOKABLE void focusPanel();',
'''      Q_INVOKABLE void focusPanel();
      QQuickItem* detailPanelHost() const;
      bool detailPanelVisible() const;
      Q_INVOKABLE void showDetailPanel(bool visible);
      Q_INVOKABLE void focusDetailPanel();''')
edit('mscore/plugin/qmlplugin.h','      void panelDockChanged();',
     '      void panelDockChanged();\n      void panelDetailChanged();\n      void panelDetailClosed();')
edit('mscore/plugin/qmlplugin.cpp','#include <QTimer>',
     '#include <QTimer>\n#include <QQuickWindow>\n#include <QApplication>\n#include <QCloseEvent>')
p=repo/'mscore/plugin/qmlplugin.cpp';s=p.read_text(encoding='utf-8')
needle='bool QmlPlugin::panelFloating() const'
addition='''QQuickItem* QmlPlugin::detailPanelHost() const
      { return _detailWindow ? _detailWindow->contentItem() : nullptr; }
bool QmlPlugin::detailPanelVisible() const
      { return _detailDock && _detailDock->isVisible(); }
bool QmlPlugin::eventFilter(QObject* object, QEvent* event)
      {
      if (object==_detailDock && event->type()==QEvent::Close) emit panelDetailClosed();
      return QQuickItem::eventFilter(object,event);
      }
void QmlPlugin::showDetailPanel(bool visible)
      {
      if (!visible) {if (_detailDock) _detailDock->hide();return;}
      if (!_panelDock) return;
      auto main=qobject_cast<QMainWindow*>(_panelDock->parentWidget());if (!main) return;
      if (!_detailDock) {
            QString title=property("detailPanelTitle").toString();
            if (title.isEmpty()) title=_panelDock->windowTitle()+tr(" - Details");
            _detailDock=new QDockWidget(title,main);_detailDock->setObjectName("pluginDetailDock");
            _detailWindow=new QQuickWindow();_detailWindow->setObjectName("pluginDetailWindow");
            const QColor background=property("detailPanelBackground").value<QColor>();
            _detailWindow->setColor(background.isValid() ? background : QApplication::palette().color(QPalette::Window));
            _detailDock->setWidget(QWidget::createWindowContainer(_detailWindow));
            _detailDock->setMinimumWidth(240);_detailDock->resize(360,740);
            _detailDock->installEventFilter(this);
            connect(_detailDock,&QDockWidget::visibilityChanged,this,[this](bool){emit panelDetailChanged();});
            // One shared QML tree, no second plugin / observer / analysis worker.
            // The container owns its QWindow; close the auxiliary surface with the plugin root.
            connect(this,&QObject::destroyed,_detailDock,&QDockWidget::deleteLater);
            main->addDockWidget(Qt::RightDockWidgetArea,_detailDock);
            main->resizeDocks({_detailDock.data()},{360},Qt::Horizontal);
            emit panelDetailChanged();
            }
      _detailDock->show();_detailDock->raise();
      }
void QmlPlugin::focusDetailPanel()
      {
      showDetailPanel(true);if (!_detailDock) return;
      _detailDock->activateWindow();
      if (_detailDock->widget()) _detailDock->widget()->setFocus(Qt::OtherFocusReason);
      }
'''
assert needle in s;write(p,s.replace(needle,addition+needle,1))
edit('mtest/mscore/pluginhost/tst_pluginhost.cpp','root->version()=="1.2.1"','root->version()=="1.3.0"')
print('Independent tick anchors, mask control and generic shared detail dock added.')
