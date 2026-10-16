from pathlib import Path
root=Path(__file__).resolve().parent;host=Path('E:/programming/funcodes/muse3_dev/MuseScore')
def patch(name,old,new):
 p=root/'native'/name;s=p.read_text(encoding='utf8');assert s.count(old)==1,(name,old[:80],s.count(old));p.write_text(s.replace(old,new),encoding='utf8',newline='\n');(host/name).write_bytes(p.read_bytes())
patch('mscore/seq.h','      void invalidatePlaybackEvents() { Q_ASSERT(!isPlaying()); playlistChanged=true; }','      void invalidatePlaybackEvents() { Q_ASSERT(!isPlaying()); playlistChanged=true; }\n      void synchronizeStoppedGui();')
patch('mscore/seq.cpp','void Seq::startAtUTick(int utick) {','void Seq::synchronizeStoppedGui() { Q_ASSERT(!isPlaying()); QCoreApplication::sendPostedEvents(this,QEvent::MetaCall); }\n\nvoid Seq::startAtUTick(int utick) {')
patch('mscore/workflow/workflowcontext.h','      QVariantMap _audition;','      QVariantMap _audition;\n      QPointer<QObject> _playbackSession;')
patch('mscore/workflow/workflowcontext.h','      QVariantMap audition()const{return _audition;}','''      QVariantMap audition()const{return _audition;}
      void finishPlaybackSession(){auto old=_playbackSession.data();_playbackSession.clear();delete old;}
      void setPlaybackSession(QObject* session){if(_playbackSession!=session){finishPlaybackSession();_playbackSession=session;}}''')
patch('mscore/workflow/scoreworkflow.cpp','#include "midiinput.h"','#include "midiinput.h"\n#include "workflowcontext.h"\n#include "playbackpreview.h"')
patch('mscore/workflow/scoreworkflow.cpp','QVariantMap ScoreObserver::stopWorkflowPlayback() {\n if(seq&&seq->isPlaying())seq->stopWait();','QVariantMap ScoreObserver::stopWorkflowPlayback() {\n stopPlaybackPreview();workflowContext()->finishPlaybackSession();\n if(seq&&seq->isPlaying())seq->stopWait();\n if(seq&&!seq->isPlaying())seq->synchronizeStoppedGui();')
patch('mscore/workflow/scoreworkflow.cpp','  static QPointer<QObject> active;\n  if(active)delete active;auto session=new QObject(this);active=session;','  workflowContext()->finishPlaybackSession();seq->synchronizeStoppedGui();auto session=new QObject(this);workflowContext()->setPlaybackSession(session);')
patch('mscore/workflow/referenceworkflow.cpp','#include "workflowcontext.h"','#include "workflowcontext.h"\n#include "playbackpreview.h"')
patch('mscore/workflow/referenceworkflow.cpp','QVariantMap ScoreObserver::startReferencePlayback(const QVariantMap& plan){','QVariantMap ScoreObserver::startReferencePlayback(const QVariantMap& plan){\n stopPlaybackPreview();')
patch('mscore/workflow/referenceworkflow.cpp',' static QPointer<QObject> active;if(active)delete active;',' workflowContext()->finishPlaybackSession();seq->synchronizeStoppedGui();')
patch('mscore/workflow/referenceworkflow.cpp','auto session=new QObject(this);active=session;','auto session=new QObject(this);workflowContext()->setPlaybackSession(session);')
patch('mscore/workflow/playbackpreview.cpp','      if(seq->isPlaying())seq->stopWait();if(seq->isPlaying()||!seq->backgroundRenderingIdle())','      workflowContext()->finishPlaybackSession();if(seq->isPlaying())seq->stopWait();if(!seq->isPlaying())seq->synchronizeStoppedGui();if(seq->isPlaying()||!seq->backgroundRenderingIdle())')
patch('mscore/workflow/playbackpreview.cpp','if(s.active){s.position=seq->getCurTick();release();}','if(s.active&&!seq->isPlaying()){s.position=seq->getCurTick();release();}')
patch('mscore/workflow/playbackpreview.cpp','void stopPlaybackPreview(bool finish){auto& s=session();if(s.active&&seq&&seq->isPlaying())seq->stopWait();if(s.active)release();if(finish)s.position=-1;}','void stopPlaybackPreview(bool finish){auto& s=session();if(s.active&&seq){if(seq->isPlaying())seq->stopWait();if(!seq->isPlaying())seq->synchronizeStoppedGui();}if(s.active)release();if(finish)s.position=-1;}')
print('Stopped GUI notifications and previous workflow sessions finish before starting the next preview')
