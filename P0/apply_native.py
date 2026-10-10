"""Apply only P0-owned additions and anchored edits to the authorized host repo."""
from pathlib import Path
import shutil

PLUGIN = Path(__file__).resolve().parent
HOST = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')

def replace(path, old, new):
    target = HOST / path
    text = target.read_text(encoding='utf-8')
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError('Anchor not unique: '+path+' '+old[:80])
    target.write_bytes(text.replace(old, new).encode('utf-8'))

def copy_files():
    for source in (PLUGIN/'native').rglob('*'):
        if source.is_file():
            target = HOST/source.relative_to(PLUGIN/'native')
            target.parent.mkdir(parents=True, exist_ok=True)
            payload=source.read_bytes()
            if not target.exists() or target.read_bytes()!=payload:target.write_bytes(payload)

if __name__ == '__main__':
    copy_files()
    if 'taptempo/taptempo.h taptempo/taptempo.cpp' not in (HOST/'mscore/CMakeLists.txt').read_text(encoding='utf-8'):
        replace('mscore/CMakeLists.txt', '      abstractdialog.h accessibletoolbutton.h albummanager.h', '      taptempo/taptempo.h taptempo/taptempo.cpp\n      abstractdialog.h accessibletoolbutton.h albummanager.h')
    replace('mscore/musescore.cpp', '#include "timedialog.h"', '#include "timedialog.h"\n#include "taptempo/taptempo.h"')
    replace('mscore/musescore.cpp', '            "independent-metronome",', '            "independent-metronome",\n            "tap-tempo",')
    replace('mscore/musescore.cpp', '                  else if (QString(s) == "independent-metronome") {', '                  else if (QString(s) == "tap-tempo") {\n                        transportTools->addWidget(TapTempo::instance(this)->createButton(transportTools, getAction("tap-tempo")));\n                        }\n                  else if (QString(s) == "independent-metronome") {')
    replace('mscore/musescore.cpp', '      menuTools->addAction(getAction("transpose"));', '      menuTools->addAction(getAction("tap-tempo"));\n      menuTools->addAction(getAction("transpose"));')
    replace('mscore/musescore.cpp', '      else if (cmd == "independent-metronome")', '      else if (cmd == "tap-tempo")\n            TapTempo::instance(this)->tap();\n      else if (cmd == "independent-metronome")')
    replace('mscore/shortcut.cpp', '         "independent-metronome",', '         "tap-tempo",\n         QT_TRANSLATE_NOOP("action","Tap BPM"),\n         QT_TRANSLATE_NOOP("action","Tap tempo"),\n         QT_TRANSLATE_NOOP("action","Estimate tempo without changing the score")\n         },\n      {\n         MsWidget::MAIN_WINDOW,\n         STATE_DISABLED | STATE_NORMAL | STATE_NOTE_ENTRY | STATE_PLAY | STATE_EDIT,\n         "independent-metronome",')
    for source in (PLUGIN.parent/'ArrangementAssistant').iterdir():
        if source.is_file() and source.suffix in ('.qml','.js','.md'):
            target=HOST/'share/plugins/ArrangementAssistant'/source.name
            target.parent.mkdir(parents=True,exist_ok=True)
            payload=source.read_bytes()
            if not target.exists() or target.read_bytes()!=payload:target.write_bytes(payload)
    print('P0 native additions applied; existing unrelated files preserved.')
    import sys
    sys.path.insert(0, str(PLUGIN))
    import patch_midi
    patch_midi.apply()
    import patch_snapshot
    patch_snapshot.apply()

    import patch_translation
    patch_translation.apply()
    import patch_workspace
    patch_workspace.apply()
