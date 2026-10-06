from pathlib import Path
p=Path(r'E:\programming\funcodes\muse3_dev\MuseScore\mtest\mscore\pluginhost\tst_pluginhost.cpp')
s=p.read_text(encoding='utf-8').replace('#include "mscore/preferences.h"','#include "mscore/preferences.h"\n#include "mscore/pianotools.h"')
old='''            observer.clearAllPreviews();QCOMPARE(view->grab().toImage(),original);
            score->selection().setRange'''
new='''            observer.clearAllPreviews();QCOMPARE(view->grab().toImage(),original);
            // Native P keyboard state and palette are independent of the score preview.
            HPiano keyboard;keyboard.resize(600,180);keyboard.show();QTest::qWait(10);
            score->select(note);keyboard.changeSelection(score->selection());
            for(int mode=0;mode<3;++mode) {
                  keyboard.setPlaybackActive(mode==1);
                  if(mode==1)keyboard.pressPlaybackPitch(note->pitch());
                  if(mode==2)keyboard.pressPitch(note->pitch());
                  observer.clearAllPreviews();const auto keys=keyboard.grab().toImage();
                  observer.setNotePreviewColors({d});QCOMPARE(keyboard.grab().toImage(),keys);
                  observer.clearAllPreviews();QCOMPARE(keyboard.grab().toImage(),keys);
                  keyboard.releasePlaybackPitch(note->pitch());keyboard.releasePitch(note->pitch());
                  }
            keyboard.hide();
            score->selection().setRange'''
assert old in s;s=s.replace(old,new,1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
