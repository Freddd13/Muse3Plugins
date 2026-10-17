// Copyright (C) 2026 Freddd13 and contributors; GPL version 2.
#include "regionalcomparison.h"
#include "libmscore/chord.h"
#include "libmscore/beam.h"
#include "libmscore/measure.h"
#include "libmscore/note.h"
#include "libmscore/regionalvariants.h"
#include "libmscore/system.h"
#include "libmscore/score.h"
#include "libmscore/segment.h"
#include "mscore/musescore.h"
#include "mscore/scoreview.h"
#include "mscore/seq.h"
#include "mscore/plugin/api/score.h"
#include "mscore/plugin/api/scoreobserver.h"
#include "referencefactory.h"
#include "referencebus.h"
#include "playbackpreview.h"
#include <QWidget>
#include <QPointer>
#include <QPainter>
#include <QEvent>
#include <QSettings>
#include <QSet>
namespace Ms {
namespace {
double tickX(Score* score,int tick){
      auto measure=score->tick2measure(Fraction::fromTicks(tick));if(!measure)return 0;
      double x=measure->canvasPos().x(),until=x+measure->width();int left=measure->tick().ticks(),right=measure->endTick().ticks();
      for(auto seg=measure->first(SegmentType::ChordRest);seg;seg=seg->next(SegmentType::ChordRest)){
            const int at=seg->tick().ticks();if(at==tick)return seg->canvasPos().x();if(at>tick){until=seg->canvasPos().x();right=at;break;}x=seg->canvasPos().x();left=at;
            }
      return x+(until-x)*double(tick-left)/qMax(1,right-left);
      }
class DifferenceLayer final:public QWidget {
      ScoreView* _view;QPointer<Score> _source,_other;ScoreContentState _state;
      struct Item{Element* element;QPointF delta;};QVector<Item> _items;QVector<QRectF> _current;
      bool eventFilter(QObject* object,QEvent* event)override{if(object==_view&&(event->type()==QEvent::Paint||event->type()==QEvent::Resize)){if(geometry()!=_view->rect())setGeometry(_view->rect());update();}return false;}
      void paintEvent(QPaintEvent*)override{
            if(!_source||!_other||_view->score()!=_source||_source->masterScore()->state()!=_state){hide();return;}if(_source->printing()||_view->fotoMode())return;
            QPainter p(this);p.setRenderHint(QPainter::Antialiasing);p.setWorldTransform(_view->matrix());
            const auto accent=palette().color(QPalette::Highlight);p.setPen(QPen(accent,0));p.setBrush(Qt::NoBrush);
            for(const auto& box:_current){if(!_view->matrix().mapRect(box).intersects(rect()))continue;p.drawRoundedRect(box.adjusted(-1,-1,1,1),1,1);}
            p.setOpacity(.4);
            for(const auto& item:_items){auto e=item.element;const auto point=e->canvasPos()+item.delta;if(!_view->matrix().mapRect(e->bbox().translated(point)).intersects(rect()))continue;p.save();p.translate(point);if(e->isNote())toNote(e)->draw(&p,accent);else e->draw(&p);p.restore();}
            }
public:
      explicit DifferenceLayer(ScoreView* view):QWidget(view),_view(view){setObjectName("regionalDifferenceLayer");setAttribute(Qt::WA_TransparentForMouseEvents);setAttribute(Qt::WA_NoSystemBackground);view->installEventFilter(this);hide();}
      void display(Score* other,const QVariantList& changes){
            _source=_view->score();_other=other;_items.clear();_current.clear();if(!other||!_source){hide();return;}_state=_source->masterScore()->state();QSet<Element*> seen;const auto accent=palette().color(QPalette::Highlight);
            for(auto value:changes){const auto row=value.toMap();const int tick=row.value("tick").toInt(),track=row.value("track").toInt();
                  auto target=_source->tick2measure(Fraction::fromTicks(tick));auto origin=other->tick2measure(Fraction::fromTicks(tick));if(!target||!origin||!target->system()||!origin->system())continue;
                  auto a=_source->tick2segment(Fraction::fromTicks(tick),false,SegmentType::ChordRest),b=other->tick2segment(Fraction::fromTicks(tick),false,SegmentType::ChordRest);
                  auto current=a&&a->tick().ticks()==tick?a->element(track):nullptr,alternative=b&&b->tick().ticks()==tick?b->element(track):nullptr;
                  if(current)_current.append(current->canvasBoundingRect());
                  if(!alternative)continue;
                  const int visual=alternative->isChordRest()?toChordRest(alternative)->vStaffIdx():track/VOICES;
                  const double targetY=target->system()->canvasPos().y()+target->system()->staffYpage(visual)-target->system()->pagePos().y();
                  const double originY=origin->system()->canvasPos().y()+origin->system()->staffYpage(visual)-origin->system()->pagePos().y();
                  const QPointF delta(tickX(_source,tick)-b->canvasPos().x(),targetY-originY);
                  QList<Element*> elements;alternative->scanElements(&elements,[](void* list,Element* element){static_cast<QList<Element*>*>(list)->append(element);},false);
                  if(alternative->isChord()&&toChord(alternative)->beam())elements.append(toChord(alternative)->beam());
                  for(auto e:elements)if(e->visible()&&!seen.contains(e)){seen.insert(e);e->setSelected(false);e->setColor(accent);_items.append({e,delta});}
                  }
            setGeometry(_view->rect());setProperty("differenceCount",changes.size());show();raise();update();
            }
};
}
void showRegionalDifference(ScoreView* view,Score* other,const QVariantList& changes){if(!view)return;DifferenceLayer* layer=nullptr;for(auto child:view->children())if((layer=dynamic_cast<DifferenceLayer*>(child)))break;if(!layer&&other)layer=new DifferenceLayer(view);if(layer)layer->display(other,changes);}
bool regionalAuditionEnabled(){return QSettings().value("regionalVariants/auditionCompare",false).toBool();}
void setRegionalAuditionEnabled(bool value){QSettings().setValue("regionalVariants/auditionCompare",value);}
QVariantMap switchRegionalWriting(ScoreView* view,const QString& group,const QString& variant){
      if(!view||!view->score()||!view->score()->isMaster())return {{"error",QObject::tr("请回到可编辑的总谱。")}};
      mscore->setCurrentScoreView(view);stopPlaybackPreview(true);auto media=referenceProject();if(media->property("playing").toBool())QMetaObject::invokeMethod(media,"stop");
      if(seq&&seq->isPlaying())seq->stopWait();if(seq&&!seq->backgroundRenderingIdle())return {{"error",QObject::tr("声音正在准备，请稍后切换。")}};
      setReferenceClock({});setReferenceEndTick(-1);auto score=view->score();auto result=RegionalVariants::select(score,group,variant);if(result.contains("error"))return result;mscore->endCmd();view->update();
      if(regionalAuditionEnabled())for(auto value:RegionalVariants::state(score).value("groups").toList()){
            auto g=value.toMap();if(g.value("id").toString()!=group)continue;
            auto observer=view->findChild<PluginAPI::ScoreObserver*>("regionalAuditionObserver");if(!observer){observer=new PluginAPI::ScoreObserver(view);observer->setObjectName("regionalAuditionObserver");}
            PluginAPI::Score wrapped(score);observer->setScore(&wrapped);const auto play=observer->navigateWorkflow({{"start",g.value("start")},{"end",g.value("end")},{"firstTrack",g.value("tracks").toList().front()},{"occurrence",1}},true);
            if(play.contains("error"))result["playbackError"]=play.value("error");break;
            }
      return result;
      }
}
