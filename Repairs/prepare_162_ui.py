"""Prepare N6 controls and independently sized settings from current native sources."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];HOST=ROOT.parent/'muse3_dev/MuseScore';NATIVE=ROOT/'P2/native';OUT=ROOT/'P2/out/repair-162';record=OUT/'files.json';files=json.loads(record.read_text('utf8'))
names=['mscore/performanceeditor/spectrumpane.cpp','mscore/performanceeditor/spectrumpane.h','mscore/performanceeditor/spectrumdisplay.cpp','mscore/performanceeditor/spectrumdisplay.h','mscore/performanceeditor/performancepainting.cpp','mscore/performanceeditor/performanceeditor.cmake','mscore/performanceeditor/performanceeditor.cpp','mscore/performanceeditor/performanceinteraction.cpp','mscore/performanceeditor/miditrackpane.h','mscore/performanceeditor/miditrackinteraction.cpp']
for name in names:
    if name in files:continue
    target=NATIVE/name
    if subprocess.check_output(['git','diff','--',str(target)],cwd=ROOT).strip():raise ValueError('Separate edits '+name)
    target.write_bytes((HOST/name).read_bytes());files[name]=hashlib.sha256((HOST/name).read_bytes()).hexdigest()
for name in ['mscore/performanceeditor/spectrumguides.cpp']:
    files.setdefault(name,None)
def edit(name,old,new):
    path=NATIVE/name;text=path.read_text('utf8')
    if new in text:return
    if old not in text:raise ValueError('Expected '+name+' '+old[:60])
    path.write_bytes(text.replace(old,new,1).encode('utf8'))
edit('mscore/performanceeditor/performanceeditor.cmake','${CMAKE_CURRENT_LIST_DIR}/spectrumdisplay.cpp','${CMAKE_CURRENT_LIST_DIR}/spectrumguides.cpp ${CMAKE_CURRENT_LIST_DIR}/spectrumdisplay.cpp')
edit('mscore/performanceeditor/spectrumpane.h','    QSplitter *_marksSplitter = nullptr;','    QSplitter *_marksSplitter = nullptr, *_workspaceSplitter = nullptr;\n    int _hoverKey = -1;\n    bool _hoverOnRoll = false;\n    QVariantMap _coloredStyle;\n    qint64 _coloredRaw = 0;\n    bool _coloredOverlay = false;')
edit('mscore/performanceeditor/spectrumpane.h','    void paintGrid(QPainter &, const QRectF &);','    void paintGrid(QPainter &, const QRectF &);\n    void hoverChanged(QPointF,bool);\n    void clearHover();\n    void paintReferences(QPainter&,const QRectF&,bool);\n    void paintMidi(QPainter&,const QRectF&,bool);\n    bool usesScoreTimeline() const;')
edit('mscore/performanceeditor/spectrumpane.h','    bool showRollNotes() const;','    bool showRollNotes() const;\n    void paintKeyboardHover(QPainter&,QWidget*) const;\n    int timelineEndTick() const;')
edit('mscore/performanceeditor/spectrumpane.cpp','    analysisBox->addWidget(_durationFromMark);','''    analysisBox->addWidget(_durationFromMark);
    auto preload=new QCheckBox(tr("后台准备整条音轨"));preload->setObjectName("spectrumPreloadTrack");
    preload->setChecked(QSettings().value("spectrum/preloadTrack",true).toBool());
    preload->setToolTip(tr("先准备可见部分，再准备相邻位置和整条录音。关闭面板时暂停，重新打开继续复用。"));
    analysisBox->addWidget(preload);
    connect(preload,&QCheckBox::clicked,this,[this](bool on){QSettings().setValue("spectrum/preloadTrack",on);_request.clear();viewChanged();});''')
edit('mscore/performanceeditor/spectrumpane.cpp','    const auto primary = _controls;','''    for(auto page:QList<QWidget*>{_displayControls,_listenControls,_beatControls,analysis}) {
        page->setMaximumWidth(560);
        const int index=options->indexOf(page);const auto title=options->tabText(index);options->removeTab(index);
        auto wrapper=new QWidget;auto row=new QHBoxLayout(wrapper);row->setContentsMargins(0,0,0,0);
        row->addWidget(page,0,Qt::AlignLeft|Qt::AlignTop);row->addStretch(1);options->insertTab(index,wrapper,title);
    }
    options->setCurrentIndex(0);
    const auto primary = _controls;''')
edit('mscore/performanceeditor/spectrumpane.cpp','    _displayPanel->setMaximumHeight(180);','    _displayPanel->setSizePolicy(QSizePolicy::Expanding,QSizePolicy::Ignored);')
edit('mscore/performanceeditor/spectrumpane.cpp','    layout->addWidget(_displayPanel);','''    _workspaceSplitter=new QSplitter(Qt::Vertical);_workspaceSplitter->setObjectName("spectrumWorkspaceSplitter");
    _workspaceSplitter->setChildrenCollapsible(false);_workspaceSplitter->addWidget(_displayPanel);
    layout->addWidget(_workspaceSplitter,1);
    connect(_workspaceSplitter,&QSplitter::splitterMoved,this,[this]{const auto sizes=_workspaceSplitter->sizes();if(_displayPanel->isVisible() && !sizes.isEmpty() && sizes[0]>0)QSettings().setValue("spectrum/settingsHeight",sizes[0]);});
    connect(displayButton,&QToolButton::clicked,this,[this]{if(_displayPanel->isVisible()){const int h=QSettings().value("spectrum/settingsHeight",160).toInt();_workspaceSplitter->setSizes({h,qMax(80,_workspaceSplitter->height()-h)});}});''')
edit('mscore/performanceeditor/spectrumpane.cpp','    layout->addWidget(_marksSplitter, 1);','    _workspaceSplitter->addWidget(_marksSplitter);\n    _workspaceSplitter->setSizes({QSettings().value("spectrum/settingsHeight",160).toInt(),400});')
edit('mscore/performanceeditor/spectrumpane.cpp','{"fundamentalMix", _displayControls->values().value("fundamental", 0.)},','{"fundamentalMix", _displayControls->values().value("fundamental", 0.)},\n                        {"preload",QSettings().value("spectrum/preloadTrack",true)},')
# Add the hover layer after the cached keyboard, before the canvas content clip.
edit('mscore/performanceeditor/performancepainting.cpp','      painter.save(); painter.setClipRect(area, Qt::IntersectClip);','''#ifdef SCRIPT_INTERFACE
      if(surface==PerformanceSurface::Notes && _spectrum)_spectrum->paintKeyboardHover(painter,widget);
#endif
      painter.save(); painter.setClipRect(area, Qt::IntersectClip);''')
record.write_text(json.dumps(files,indent=2),encoding='utf8');print('Prepared spectrum controls and settings splitter')
