from pathlib import Path
HOST=Path(r'E:/programming/funcodes/muse3_dev/MuseScore')
ROOT=Path(__file__).resolve().parent
changed=set()
def edit(name,old,new,count=1):
 p=HOST/name;s=p.read_text(encoding='utf-8')
 if new and new in s:
  changed.add(name);return
 assert s.count(old)==count,(name,old[:90],s.count(old));p.write_text(s.replace(old,new),encoding='utf-8',newline='\n');changed.add(name)

ux='mscore/performanceeditor/performanceux.cpp'
edit(ux,'      new PerformancePeekKeys(this);','''      new PerformancePeekKeys(this);
      connect(&_wheelFeedbackTimer,&QTimer::timeout,this,[this]{
            ++_wheelFeedbackTicks;if(_wheelFeedbackTicks>=30){_wheelFeedbackTimer.stop();}
            if(_wheelFeedbackSurface)_wheelFeedbackSurface->update();
            });''')
edit(ux,'      auto actual=new QCheckBox(tr("实际力度＋原力度线"),this);','      auto actual=new QCheckBox(tr("显示记号力度线"),this);')
edit(ux,'      connect(_parameter,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[this,actual](int i){actual->setVisible(i==0);});','''      actual->setChecked(settings.value("performanceEditor/markVelocityLines",true).toBool());
      connect(actual,&QCheckBox::toggled,this,[](bool on){QSettings().setValue("performanceEditor/markVelocityLines",on);});
      auto arrangement=new QComboBox(this);arrangement->setObjectName("performanceVelocityArrangement");arrangement->addItems({tr("力度同图"),tr("按谱表分区")});arrangement->setCurrentIndex(qBound(0,settings.value("performanceEditor/velocityArrangement",0).toInt(),1));_velocityArrangement=arrangement->currentIndex();
      connect(arrangement,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[this](int i){finishWheel();cancelGesture();_velocityArrangement=i;QSettings().setValue("performanceEditor/velocityArrangement",i);invalidateVisual();});add(arrangement);
      auto together=new QComboBox(this);together->setObjectName("performanceGroupVelocity");together->addItems({tr("一起增减百分比"),tr("相同MIDI差值")});_groupRelative=settings.value("performanceEditor/groupRelative",true).toBool();together->setCurrentIndex(_groupRelative?0:1);
      together->setToolTip(tr("百分比方式分别按各音的记号力度换算；例如80和48同时增加10%，得到88和53。"));
      connect(together,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[this](int i){finishWheel();cancelGesture();_groupRelative=i==0;QSettings().setValue("performanceEditor/groupRelative",_groupRelative);});add(together);
      connect(_parameter,QOverload<int>::of(&QComboBox::currentIndexChanged),this,[actual,arrangement,together](int i){actual->setVisible(i==0);arrangement->setVisible(i==0);together->setVisible(i==0);});''')
edit(ux,'      auto text=new QLabel', '      auto text=new QLabel',count=0) if False else None
edit(ux,'auto key=new QKeySequenceEdit(QKeySequence(_peekKey));layout->addWidget(key);','''auto key=new QKeySequenceEdit(QKeySequence(_peekKey));layout->addWidget(key);
            layout->addWidget(new QLabel(tr("谱面最近音滚轮快捷键")));
            auto wheelKey=new QComboBox;wheelKey->addItem("Alt+Shift",int(Qt::AltModifier|Qt::ShiftModifier));wheelKey->addItem("Ctrl+Alt",int(Qt::ControlModifier|Qt::AltModifier));wheelKey->addItem("Ctrl+Shift",int(Qt::ControlModifier|Qt::ShiftModifier));wheelKey->addItem(tr("关闭"),0);wheelKey->setCurrentIndex(qMax(0,wheelKey->findData(QSettings().value("performanceEditor/nearestWheelModifiers",int(Qt::AltModifier|Qt::ShiftModifier)))));layout->addWidget(wheelKey);''')
edit(ux,'if(dialog.exec()==QDialog::Accepted){_peekKey=', 'if(dialog.exec()==QDialog::Accepted){QSettings().setValue("performanceEditor/nearestWheelModifiers",wheelKey->currentData());_peekKey=')
# The chart lane is chosen once per note and shared by drawing and mouse tests.
edit(ux,'const QPointF p(x,yForValue(n.base,rect,onScore));int staff=n.track/VOICES, line=n.track;', 'const auto noteLane=velocityLane(i,rect,onScore);if(noteLane.isEmpty())continue;const QPointF p(x,yForValue(n.base,noteLane,onScore));int staff=n.track/VOICES, line=n.track;')
edit(ux,'QColor color=MScore::selectColor[n.track%VOICES];if(!n.enabled)color.setAlpha(45);','QColor color=_appearance.staves[(n.track/VOICES)%8];if(!n.enabled)color.setAlpha(45);')
edit(ux,'谱表 %1 · 声部 %2 · 原力度 %3','谱表 %1 · 声部 %2 · 记号力度 %3')

interaction='mscore/performanceeditor/performanceinteraction.cpp'
edit(interaction,'      rebuildPitchRows();_visibleScoreNotes.clear();','''      _velocityStaves.clear();for(const auto& n:_notes)if(n.enabled&&!_velocityStaves.contains(n.track/VOICES))_velocityStaves.append(n.track/VOICES);std::sort(_velocityStaves.begin(),_velocityStaves.end());
      rebuildPitchRows();_visibleScoreNotes.clear();''')
edit(interaction,'      if (event->type() == QEvent::Show) { scheduleRefresh(); syncTransport(); syncOverlayTracking(); }','''      if(event->type()==QEvent::MouseButtonPress && parameter && static_cast<QMouseEvent*>(event)->button()==Qt::LeftButton && velocityHeaderClick(static_cast<QMouseEvent*>(event)->pos()))return true;
      if (event->type() == QEvent::Show) { scheduleRefresh(); syncTransport(); syncOverlayTracking(); }''')
edit(interaction,'if (noteEditable(*it) && std::abs(xForNote(i, onScore) - point.x()) < 7','if (noteEditable(*it) && !velocityLane(i,lane,onScore).isEmpty() && velocityLane(i,lane,onScore).adjusted(0,-2,0,5).contains(QPointF(qBound(lane.left(),point.x(),lane.right()),point.y())) && std::abs(xForNote(i, onScore) - point.x()) < 7')
for old,new,count in [
 ('yForValue(noteValue(i), lane, onScore)','velocityY(i, lane, onScore)',1),
 ('yForValue(noteValue(a), lane, onScore)','velocityY(a, lane, onScore)',1),
 ('yForValue(noteValue(b), lane, onScore)','velocityY(b, lane, onScore)',1)]:edit(interaction,old,new,count)

painting='mscore/performanceeditor/performancepainting.cpp'
edit(painting,'if (surface == PerformanceSurface::Parameter) {\n            const auto range', 'if (surface == PerformanceSurface::Parameter && !(_velocityArrangement&&_parameter->currentIndex()==0)) {\n            const auto range')
edit(painting,'      if (parameter == 0) {\n            if(_relativeActual)', '      if (parameter == 0) {\n            if(!onScore)paintVelocityHeaders(painter,rect);\n            if(_relativeActual)')
edit(painting,'const bool dense = !onScore && _viewport.pixelsPerQuarter < 8;', 'const bool dense = !onScore && !_velocityArrangement && _viewport.pixelsPerQuarter < 8;')
edit(painting,'const double y = yForValue(noteValue(index), rect, onScore);','''const auto noteLane=velocityLane(index,rect,onScore);if(noteLane.isEmpty())continue;
                  const double y = velocityY(index, rect, onScore);
                  const double noteBaseline=qBound(noteLane.top(),yForValue(rangeKind()==1?0:1,noteLane,onScore),noteLane.bottom());''')
edit(painting,'painter.drawLine(QPointF(x, baseline), QPointF(x, y));','painter.drawLine(QPointF(x, noteBaseline), QPointF(x, y));',3)
edit(painting,'yForValue(range.first,rect,onScore),high=yForValue(range.second,rect,onScore)', 'yForValue(range.first,noteLane,onScore),high=yForValue(range.second,noteLane,onScore)')
edit(painting,'const double x = xForNote(index, onScore), y = yForValue(noteValue(index), rect, onScore);','''const auto noteLane=velocityLane(index,rect,onScore);if(noteLane.isEmpty())continue;
                  const double noteBaseline=qBound(noteLane.top(),yForValue(rangeKind()==1?0:1,noteLane,onScore),noteLane.bottom());
                  const double x = xForNote(index, onScore), y = velocityY(index, rect, onScore);''')

editor='mscore/performanceeditor/performanceeditor.cpp'
for old,new in [('yForValue(noteValue(_pressedCandidates[1]),rect,onScore)','velocityY(_pressedCandidates[1],rect,onScore)'),('yForValue(noteValue(_anchor),rect,onScore)','velocityY(_anchor,rect,onScore)'),('yForValue(noteValue(i), rect, onScore)','velocityY(i, rect, onScore)'),('yForValue(noteValue(i),_gestureLane,_scoreGesture)','velocityY(i,_gestureLane,_scoreGesture)')]:edit(editor,old,new)
edit(editor,'            const double delta = (_noteGesture ?', '''            const auto valueLane=(_anchor>=0&&!_noteGesture)?velocityLane(_anchor,_gestureLane,_scoreGesture):_gestureLane;
            if(valueLane.isEmpty())return;
            const double delta = (_noteGesture ?''')
edit(editor,'valueForY(point.y(), _gestureLane, _scoreGesture) - valueForY(_press.y(), _gestureLane, _scoreGesture))*_dragSensitivity;', 'valueForY(point.y(), valueLane, _scoreGesture) - valueForY(_press.y(), valueLane, _scoreGesture))*_dragSensitivity;')
edit(editor,'            for (int index : _dragTargets) setNoteValue(index, _dragOriginal.value(index) + delta, false);','''            for (int index : _dragTargets) {
                  const double scale=_groupRelative&&rangeKind()==0&&_dragTargets.size()>1&&_anchor>=0&&_notes[_anchor].base>0&&_notes[index].base>0 ? double(_notes[index].base)/_notes[_anchor].base:1.;
                  setNoteValue(index, _dragOriginal.value(index) + delta*scale, false);
                  }
            if(_groupRelative&&rangeKind()==0&&_dragTargets.size()>1&&_anchor>=0&&_notes[_anchor].base>0)status(tr("一起调整 %1% · 已选%2音").arg(delta*100/_notes[_anchor].base,0,'f',1).arg(_dragTargets.size()));''')
edit(editor,'if (!selected || it->selected) setNoteValue(int(it - _notes.cbegin()), value(it->tick), false);','''if (!selected || it->selected) {
                                    const int index=int(it-_notes.cbegin());const auto lane=velocityLane(index,_gestureLane,false);if(lane.isEmpty())continue;
                                    if(_velocityArrangement){if(!lane.contains(QPointF(qBound(lane.left(),point.x(),lane.right()),point.y())))continue;const double fraction=until==from?1.:double(it->tick-from)/(until-from);setNoteValue(index,valueForY(start.y()+(point.y()-start.y())*fraction,lane,false),false);}
                                    else setNoteValue(index, value(it->tick), false);
                                    }''')
# Compact bodies can be folded independently, with sizes restored on reopening.
edit(editor,'                 ? QSize(260, qMax(240, layout()->minimumSize().height()))','                 ? QSize(260, 240)')
edit(editor,'_splitter->setChildrenCollapsible(false);','_splitter->setChildrenCollapsible(true);')
edit(editor,'      _splitter->restoreState(QSettings().value("performanceEditor/splitter").toByteArray());','')
edit(editor,'if(show)_splitter->setSizes({150,130,180});updateGeometry();','if(show){if(!_splitter->restoreState(QSettings().value("performanceEditor/splitter").toByteArray()))_splitter->setSizes({150,130,180});}updateGeometry();')
edit(editor,'      _status = new QLabel(this);','''      _splitter->restoreState(QSettings().value("performanceEditor/splitter").toByteArray());
      auto areas=new QToolButton(this);areas->setText(tr("区域"));areas->setObjectName("performanceAreaMenu");areas->setPopupMode(QToolButton::InstantPopup);auto areaMenu=new QMenu(areas);areas->setMenu(areaMenu);second->addWidget(areas,second->count()/6,second->count()%6);
      for(auto item:QList<QPair<QString,QWidget*>>{{tr("钢琴卷帘"),noteArea},{tr("力度／速度／踏板"),parameterArea},{tr("音轨／演奏对应"),_workflowPanel}}){auto action=areaMenu->addAction(item.first);action->setCheckable(true);action->setChecked(!item.second->isHidden());connect(action,&QAction::toggled,this,[this,item](bool on){item.second->setVisible(on);if(on){auto sizes=_splitter->sizes();int n=_splitter->indexOf(item.second);if(n>=0&&sizes[n]<40){sizes[n]=140;_splitter->setSizes(sizes);}}updateGeometry();});connect(areaMenu,&QMenu::aboutToShow,action,[item,action]{QSignalBlocker block(action);action->setChecked(!item.second->isHidden());});}
      auto restoreAreas=areaMenu->addAction(tr("恢复区域高度"));connect(restoreAreas,&QAction::triggered,this,[this]{_splitter->setSizes({150,130,180});});
      _status = new QLabel(this);''')
edit('mscore/performanceeditor/performanceview.cpp','else setMinimumHeight(surface == PerformanceSurface::Notes ? 100 : 90);','else setMinimumHeight(32);')
# Export mirrors after all assertions have passed.
for name in changed:
 dst=ROOT/'native'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((HOST/name).read_bytes())
print('Updated',len(changed),'files')
