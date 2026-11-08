"""Fix the score-video action's startup and workspace integration."""
from pathlib import Path
import hashlib, json, subprocess

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-165'
O.mkdir(parents=True, exist_ok=True)
names = ['mscore/musescore.cpp', 'mscore/scorevideo/scorevideopanel.cpp',
         'mscore/scorevideo/scorevideopanel.h', 'personal/VERSION',
         'personal/USER_GUIDE.md', 'personal/CHANGELOG.md',
         'personal/docs/REWORK_PROGRESS.md', 'personal/docs/source-map.tsv',
         'personal/docs/SCORE_VIDEO_164_GUIDE.md']
record = {}
for name in names:
    raw = (H / name).read_bytes()
    record[name] = hashlib.sha256(raw).hexdigest()
    # Keep the unrelated guide edits in the host working tree.
    data = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=H) if name == 'personal/USER_GUIDE.md' else raw
    (N / name).write_bytes(data.replace(b'\r\n', b'\n'))
(O / 'files.json').write_text(json.dumps(record, indent=2), encoding='utf8')

p = N / 'mscore/scorevideo/scorevideopanel.cpp'
t = p.read_text('utf8').replace('#include "mscore/musescore.h"', '#include "mscore/musescore.h"\n#include "mscore/workspace.h"', 1)
t = t.replace('void addScoreVideoAction(QMenu* menu)\n{', 'QAction* scoreVideoAction()\n{', 1)
old = '        action->setCheckable(true);\n        markPersonalAction(action);'
new = '''        action->setCheckable(true);
        action->setData("kumo-score-video");
        markPersonalAction(action);
        Workspace::addActionAndString(action, "kumo-score-video");'''
assert old in t
t = t.replace(old, new, 1)
old = '    menu->addAction(action);\n}\n} // namespace Ms'
new = '''    action->setText(QObject::tr("动态乐谱视频…"));
    action->setToolTip(QObject::tr("制作动态乐谱视频：选择谱表、预览换行，导出 MP4 或透明 MOV。"));
    return action;
}
void addScoreVideoAction(QMenu* menu)
{
    if (!menu)
        return;
    auto action = scoreVideoAction();
    if (menu->actions().contains(action))
        return;
    menu->insertAction(getAction("transpose"), action);
}
} // namespace Ms'''
assert old in t
t = t.replace(old, new, 1)
p.write_text(t, encoding='utf8', newline='\n')
p = N / 'mscore/scorevideo/scorevideopanel.h'
t = p.read_text('utf8').replace('class QMenu;', 'class QMenu;\nclass QAction;', 1).replace('void addScoreVideoAction(QMenu*);', 'QAction* scoreVideoAction();\nvoid addScoreVideoAction(QMenu*);', 1)
p.write_text(t, encoding='utf8', newline='\n')
p = N / 'mscore/musescore.cpp'
t = p.read_text('utf8')
old = '            auto action = findChild<QAction*>(name);\n#ifdef SCRIPT_INTERFACE'
new = '''            auto action = QString(name) == "kumo-score-video"
                  ? scoreVideoAction() : findChild<QAction*>(name);
#ifdef SCRIPT_INTERFACE'''
assert old in t
t = t.replace(old, new, 1)
old = '      updateMenu(menuTools,       "menu-tools",        "Tools");\n'
assert old in t
t = t.replace(old, old + '      addScoreVideoAction(menuTools);\n', 1)
p.write_text(t, encoding='utf8', newline='\n')
(N / 'personal/VERSION').write_text('0.165.0\n', encoding='utf8')
print('Prepared action creation, workspace registration and menu restoration.')
