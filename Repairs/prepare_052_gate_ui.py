from pathlib import Path
R=Path(__file__).resolve().parent/'native'
p=R/'mscore/midicrop/midicroppanel.h';s=p.read_text(encoding='utf8').replace('#include "audio/exports/midigate.h"','#include "audio/exports/midigate.h"\n#include "libmscore/score.h"');s=s.replace('QMap<Score*,QMap<QString,int>> _releaseOverrides;','QMap<Score*,QMap<QString,int>> _releaseOverrides;\n      QMap<Score*,ScoreContentState> _releaseStates;');s=s.replace('_releaseOverrides.clear();','_releaseOverrides.clear(); _releaseStates.clear();');p.write_text(s,encoding='utf8',newline='\n')
p=R/'mscore/midicrop/midicroppanel.cpp';s=p.read_text(encoding='utf8');s=s.replace('#include "midicroppanel.h"','#include "midicroppanel.h"\n#include "gateaudition.h"\n#include "libmscore/playbacktiming.h"\n#include "libmscore/repeatlist.h"\n#include "mscore/performanceeditor/performanceeditor.h"\n#include "mscore/scoreview.h"\n#include "mscore/workflow/workflowcontext.h"\n#include <QCryptographicHash>')
s=s.replace('result.gate.releaseOverrides=_releaseOverrides.value(score);','if(_releaseStates.value(score)==score->masterScore()->state())result.gate.releaseOverrides=_releaseOverrides.value(score);')
s=s.replace('      ExportMidi exporter(score);QBuffer buffer;', '''      if(!_releaseOverrides.value(score).isEmpty()&&_releaseStates.value(score)!=score->masterScore()->state()){QMessageBox::information(this,tr("MIDI松手处理"),tr("乐谱已改变，请打开“查看对比”更新手动松手位置，再导出。"));return false;}
      ExportMidi exporter(score);QBuffer buffer;''',1)
s=s.replace('auto zoom=new QSlider(Qt::Horizontal,&dialog);zoom->setRange(1,40);zoom->setValue(10);bar->addWidget(zoom);layout->addLayout(bar);','auto zoom=new QSlider(Qt::Horizontal,&dialog);zoom->setObjectName("midiCropZoom");zoom->setRange(1,400);zoom->setValue(100);zoom->setToolTip(tr("水平缩放；也可在图上按Ctrl+滚轮，以鼠标位置缩放。Shift+滚轮调整音高行高度。"));bar->addWidget(zoom);layout->addLayout(bar);')
s=s.replace('      auto caption=new QLabel(','''      auto canvasPane=new QWidget(&dialog);canvasPane->setObjectName("midiCropCanvasPane");auto canvasLayout=new QVBoxLayout(canvasPane);canvasLayout->setContentsMargins(0,0,0,0);layout->addWidget(canvasPane,3);
      auto caption=new QLabel(''',1).replace('layout->addWidget(caption);','canvasLayout->addWidget(caption);',1).replace('layout->addWidget(roll,2);','canvasLayout->addWidget(roll,1);',1).replace('detail->setMinimumHeight(48);layout->addWidget(detail);','detail->setMinimumHeight(48);canvasLayout->addWidget(detail);',1)
s=s.replace('      MidiGateData data;QVector<MidiGateNote> rows;bool loading=false,queued=false;', '''      auto transport=new QHBoxLayout;canvasLayout->addLayout(transport);
      auto originalPlay=new QPushButton(tr("听原长度"),canvasPane),proposedPlay=new QPushButton(tr("听新长度"),canvasPane),stopPlay=new QPushButton(tr("停止"),canvasPane),fit=new QPushButton(tr("匹配内容"),canvasPane),editorMode=new QPushButton(tr("在演奏编辑器调整…"),canvasPane);
      originalPlay->setObjectName("midiCropOriginalPlay");proposedPlay->setObjectName("midiCropProposedPlay");stopPlay->setObjectName("midiCropStop");fit->setObjectName("midiCropFit");editorMode->setObjectName("midiCropEditorMode");
      for(auto button:{originalPlay,proposedPlay,stopPlay,fit,editorMode})transport->addWidget(button);
      auto playStatus=new QLabel(tr("选择一个音，可以拖实心条的尾端调整松手；右键可恢复自动计算。"),canvasPane);playStatus->setObjectName("midiCropPlaybackStatus");playStatus->setWordWrap(true);canvasLayout->addWidget(playStatus);
      MidiGateData data;QVector<MidiGateNote> rows;bool loading=false,queued=false;QString auditionKey;bool proposedMode=false;
      QPointer<Score> targetScore=scores.front();
      std::function<void(bool)> audition;
''')
old='auto present=[&] {model->setRows(rows,data,part->currentData().toInt(),filter->currentIndex());roll->notes.clear();for(int i:model->visible)roll->notes.append(rows[i]);roll->pedals=data.pedals;roll->selected=-1;roll->indexNotes();roll->refresh();};'
new='''auto present=[&] {const QString selected=roll->selected>=0&&roll->selected<roll->notes.size()?roll->notes[roll->selected].id:QString();model->setRows(rows,data,part->currentData().toInt(),filter->currentIndex());roll->notes.clear();for(int i:model->visible)roll->notes.append(rows[i]);roll->pedals=data.pedals;roll->selected=-1;roll->editingOptions=options(targetScore).gate;roll->indexNotes();for(int i=0;i<roll->notes.size();++i)if(roll->notes[i].id==selected){roll->selected=i;table->selectRow(i);break;}roll->refresh();};'''
assert old in s;s=s.replace(old,new)
s=s.replace('if(loading) {queued=true;return;}const auto snapshot=data;','if(loading) {queued=true;return;}if(!targetScore)return;stopPlaybackPreview();auditionKey.clear();const auto snapshot=data;')
s=s.replace('loading=true;\n            caption->setText','loading=true;originalPlay->setEnabled(false);proposedPlay->setEnabled(false);editorMode->setEnabled(false);\n            caption->setText',1)
s=s.replace('rows=watcher.result();loading=false;exclude->setEnabled(true);','rows=watcher.result();loading=false;originalPlay->setEnabled(true);proposedPlay->setEnabled(true);editorMode->setEnabled(true);exclude->setEnabled(true);',1)
s=s.replace('      auto load=[&] {\n            ExportMidi exporter', '''      auto load=[&] {
            targetScore=scores[scoreBox->currentIndex()];if(!targetScore)return;
            if(_releaseStates.value(targetScore)!=targetScore->masterScore()->state())_releaseOverrides[targetScore].clear();
            _releaseStates[targetScore]=targetScore->masterScore()->state();
            ExportMidi exporter''')
s=s.replace('roll->scale=i*.015;roll->refresh();','roll->setScale(i*.0015,roll->viewport()->width()/2.);')
s=s.replace('      roll->selectRow=[table](int row){table->selectRow(row);};','''      roll->selectRow=[table](int row){table->selectRow(row);};
      roll->scaleChanged=[zoom](double value){QSignalBlocker block(zoom);zoom->setValue(qBound(1,qRound(value/.0015),400));};
      roll->editRelease=[&](const QString& id,int at){if(!targetScore||loading)return;stopPlaybackPreview();auto& values=_releaseOverrides[targetScore];if(at<0)values.remove(id);else values[id]=at;_releaseStates[targetScore]=targetScore->masterScore()->state();playStatus->setText(tr("已调整这一次出现的音；最终MIDI采用图中的松手位置。"));calculate();};
      connect(fit,&QPushButton::clicked,&dialog,[&]{roll->fitContent();});
      audition=[&](bool proposed){
            if(!targetScore||loading)return;if(mscore->currentScore()!=targetScore){playStatus->setText(tr("请先在乐谱标签页打开%1，再试听这份谱。").arg(targetScore->title()));return;}
            if(_releaseStates.value(targetScore)!=targetScore->masterScore()->state()){playStatus->setText(tr("乐谱已改变，请返回对比并重新计算。"));return;}
            if(auditionKey.isEmpty()||!playbackPreviewPrepared(targetScore,auditionKey)){
                  playStatus->setText(tr("正在准备原长度与新长度的声音…"));auto prepared=prepareGateAudition(targetScore,data,rows);
                  if(prepared.unmatched){playStatus->setText(tr("%1个导出音还需要核对演奏对应。可先导出前后MIDI听这一段。").arg(prepared.unmatched));return;}
                  auditionKey="midi-gate-"+QString::number(quintptr(targetScore.data()))+"-"+QString::number(QDateTime::currentMSecsSinceEpoch());preparePlaybackPreview(targetScore,auditionKey,std::move(prepared.original),std::move(prepared.proposed));
                  }
            int start=0,occurrence=1;if(roll->selected>=0&&roll->selected<roll->notes.size()){
                  const auto& note=roll->notes[roll->selected];start=qMax(0,note.sourceTick);int seen=0;for(auto repeat:targetScore->masterScore()->repeatList())if(start>=repeat->tick&&start<repeat->tick+repeat->len()){++seen;if(note.sourceUtick>=repeat->utick&&note.sourceUtick<repeat->utick+repeat->len()){occurrence=seen;break;}}
                  }
            auto result=startPlaybackPreview(targetScore,proposed,{{"start",start},{"end",targetScore->lastMeasure()->endTick().ticks()},{"occurrence",occurrence}});
            if(result.contains("error")){playStatus->setText(result.value("error").toString());return;}proposedMode=proposed;playStatus->setText(proposed?tr("正在听：新长度 · 可直接切换到原长度，从当前拍位继续。"):tr("正在听：原长度 · 可直接切换到新长度，从当前拍位继续。"));
            };
      connect(originalPlay,&QPushButton::clicked,&dialog,[&]{audition(false);});connect(proposedPlay,&QPushButton::clicked,&dialog,[&]{audition(true);});connect(stopPlay,&QPushButton::clicked,&dialog,[&]{stopPlaybackPreview();playStatus->setText(tr("已停止，切换原长度／新长度可从这里继续。"));});
      QTimer playhead;playhead.setInterval(40);connect(&playhead,&QTimer::timeout,&dialog,[&]{
            if(!targetScore||!seq||!seq->isPlaying()||!playbackPreviewActive(targetScore,proposedMode))return;
            for(const auto& n:data.notes)if(n.sourceUtick>=0){roll->setPlayhead(roll->clock.durationMs(0,n.on)+(PlaybackTiming::time(targetScore,seq->getCurTick())-PlaybackTiming::time(targetScore,n.sourceUtick))*1000.);break;}
            });playhead.start();
      connect(editorMode,&QPushButton::clicked,&dialog,[&]{
            if(loading||!targetScore)return;auto editor=mscore->performanceEditor();auto oldParent=editor->parentWidget();auto oldDock=qobject_cast<QDockWidget*>(oldParent);const bool oldVisible=editor->isVisible(),dockVisible=oldDock&&oldDock->isVisible();
            QList<QPointer<QWidget>> visible;for(auto child:editor->findChildren<QWidget*>(QString(),Qt::FindDirectChildrenOnly))if(!child->isHidden()){visible.append(child);child->hide();}
            QDialog mode(mscore);mode.setObjectName("midiCropEditorWindow");mode.setWindowTitle(tr("演奏编辑器 · 导出音长"));mode.resize(1180,760);auto box=new QVBoxLayout(&mode);
            auto header=new QLabel(tr("导出音长 · %1\\n虚线框：原长度；实心条：新长度；灰色：保持原样。Ctrl+滚轮缩放时间，Shift+滚轮调整行高，中键拖动浏览。尾端只改变这次导出。 ").arg(targetScore->title()),&mode);header->setWordWrap(true);box->addWidget(header);
            if(oldDock)oldDock->hide();dialog.hide();editor->setParent(&mode);box->addWidget(editor,1);editor->layout()->addWidget(canvasPane);canvasPane->show();editor->show();editorMode->hide();
            auto back=new QPushButton(tr("完成调整，返回导出"),&mode);back->setObjectName("midiCropEditorReturn");box->addWidget(back);connect(back,&QPushButton::clicked,&mode,&QDialog::accept);
            mode.exec();editor->layout()->removeWidget(canvasPane);canvasPane->setParent(&dialog);layout->insertWidget(2,canvasPane,3);canvasPane->show();editorMode->show();
            editor->setParent(oldParent);if(oldDock)oldDock->setWidget(editor);for(auto child:visible)if(child)child->show();editor->setVisible(oldVisible);if(oldDock)oldDock->setVisible(dockVisible);dialog.show();dialog.raise();
            });''')
s=s.replace('detail->setText(explanation);roll->horizontalScrollBar()->setValue(qMax(0,int(roll->clock.durationMs(0,note.on)*roll->scale)-20));','detail->setText(explanation);roll->revealSelected();')
s=s.replace('_exclusions[scores[scoreBox->currentIndex()]].clear();_staves','_exclusions[scores[scoreBox->currentIndex()]].clear();_releaseOverrides[scores[scoreBox->currentIndex()]].clear();_staves')
s=s.replace('      canceled->store(true);watcher.disconnect();watcher.cancel();','      stopPlaybackPreview(true);playhead.stop();canceled->store(true);watcher.disconnect();watcher.cancel();')
p.write_text(s,encoding='utf8',newline='\n')
