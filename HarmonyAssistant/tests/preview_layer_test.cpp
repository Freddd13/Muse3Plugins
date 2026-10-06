// GPL-2.0-or-later. Standalone staged-layer regression; never touches a score or user process.
#include <QGuiApplication>
#include <QElapsedTimer>
#include <cstdio>
#include "../native/notepreview-0.5.h.inc"

int main(int argc,char** argv)
      {
      QGuiApplication application(argc,argv);
      using namespace Ms;
      int failures=0;
      auto check=[&](bool ok,const char* message){if(!ok){std::fprintf(stderr,"FAIL: %s\n",message);++failures;}};
      QObject owner,foreground;
      const auto source=reinterpret_cast<const Element*>(quintptr(1));
      NotePreviewLayers layers;
      NotePreviewEntry first;first.chord="C";first.chordTick=0;first.chordUntil=240;
      first.sourceAnchor=source;first.chordBox=QRectF(10,10,50,20);first.bounds=first.chordBox;
      NotePreviewEntry second=first;second.chord="Cm";second.chordTick=240;second.chordUntil=480;
      second.chordBox.translate(70,0);second.bounds=second.chordBox;second.chordMask=false;
      NotePreviewColors colors{{source,{Qt::red,QRectF(10,50,8,8)}}};
      const NotePreviewMarkers markers{first,second};
      check(!layers.replace(&owner,colors,markers).isEmpty(),"initial dirty area");
      int count=0,active=-1;
      auto inspect=[&](){count=0;active=-1;layers.forEachChord([&](const NotePreviewEntry& entry,bool selected){
            ++count;if(selected)active=entry.chordTick;
            if(entry.chordTick==240)check(!entry.chordMask,"mask preference preserved");});};
      layers.setActiveChord(&owner,0);inspect();check(count==2 && active==0,"two markers sharing one sustained source");
      check(layers.setActiveChord(&owner,120).isEmpty(),"no dirty area inside same interval");
      layers.setActiveChord(&owner,240);inspect();check(active==240,"release-only harmonic change");
      check(layers.replace(&owner,colors,markers).isEmpty(),"unchanged base does not rebuild");
      layers.replace(&foreground,{{source,{Qt::blue,QRectF(10,50,8,8)}}});
      inspect();check(count==2 && active==240,"current note layer retains fixed markers");
      check(layers.color(source)==QColor(Qt::blue),"role color priority retained");
      layers.setActiveChord(&owner,480);inspect();check(active==-1,"half-open end clears highlight");
      layers.remove(source);inspect();check(count==0,"destruction removes all source markers without dereferencing");
      check(!layers.color(source).isValid(),"destruction removes note layers");
      layers.clear();
      NotePreviewEntry legacy=first;legacy.chordUntil=480;
      layers.replace(&owner,{{source,legacy}});inspect();check(count==1,"legacy inline descriptors accepted");
      layers.remove(source);inspect();check(count==0,"legacy source cleanup");
      layers.clear();
      NotePreviewColors manyColors;NotePreviewMarkers manyMarkers;
      for(int i=0;i<6000;++i) {
            auto key=reinterpret_cast<const Element*>(quintptr(i+1));
            manyColors.insert(key,{Qt::blue,QRectF(i,50,2,2)});
            if(i%6==0){auto entry=first;entry.sourceAnchor=key;entry.chordTick=i*80;entry.chordUntil=(i+6)*80;manyMarkers.append(entry);}
            }
      layers.replace(&owner,manyColors,manyMarkers);
      QElapsedTimer timer;timer.start();for(int i=0;i<1000;++i)layers.setActiveChord(&owner,i*480);
      std::printf("1000 highlight changes: %.3f ms (6000 notes, 1000 independent markers)\n",double(timer.nsecsElapsed())/1e6);
      std::printf("Layer checks: %s\n",failures ? "FAILED" : "passed");
      return failures ? 1 : 0;
      }
