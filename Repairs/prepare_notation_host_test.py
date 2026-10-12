from pathlib import Path
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
dst=ROOT/'native/mtest/mscore/p0native/tst_p0native.cpp';dst.parent.mkdir(parents=True,exist_ok=True)
s=(HOST/'mtest/mscore/p0native/tst_p0native.cpp').read_text(encoding='utf8')
s=s.replace('#include "mscore/preferences.h"','#include "mscore/preferences.h"\n#include "mscore/inputrhythmpreference.h"\n#include "libmscore/inputnotation.h"')
needle='      void tapUsesSharedActionAndFixedGeometry()'
assert s.count(needle)==1
test='''      void notationMenusAndPreference()
            {
            auto join=mscore->findChild<QAction*>("auto-tie-beams");auto stems=mscore->findChild<QAction*>("coherent-tie-stems");
            QVERIFY(join);QVERIFY(stems);QVERIFY(!join->isChecked());QVERIFY(stems->isChecked());
            auto menu=Workspace::findMenuFromString("menu-tools");QVERIFY(menu);QVERIFY(menu->actions().contains(join));
            menu->popup(QPoint(20,20));QTest::qWait(30);menu->setActiveAction(join);QTest::qWait(20);
            QTest::mouseClick(menu,Qt::LeftButton,Qt::NoModifier,menu->actionGeometry(join).center());
            QTRY_VERIFY(join->isChecked());QVERIFY(InputNotation::tiedBeams());QVERIFY(preferences.getBool(PREF_SCORE_TIED_BEAMS));
            join->trigger();QVERIFY(!InputNotation::tiedBeams());QVERIFY(!preferences.getBool(PREF_SCORE_TIED_BEAMS));
            stems->trigger();QVERIFY(!InputNotation::coherentStems());QVERIFY(!preferences.getBool(PREF_SCORE_COHERENT_TIE_STEMS));
            stems->trigger();QVERIFY(InputNotation::coherentStems());QVERIFY(preferences.getBool(PREF_SCORE_COHERENT_TIE_STEMS));
            }
'''
dst.write_bytes(s.replace(needle,test+needle).encode('utf8'))
