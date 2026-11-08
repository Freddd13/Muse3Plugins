"""Finish the focused workspace repair and tidy the round's instructions."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
H = R.parent / 'muse3_dev/MuseScore'
N = R / 'P2/native'
O = R / 'P2/out/repair-165'
files = json.loads((O / 'files.json').read_text('utf8'))

def edit(name, transform):
    path = N / name
    if name not in files:
        raw = (H / name).read_bytes()
        files[name] = hashlib.sha256(raw).hexdigest()
        path.write_bytes(raw.replace(b'\r\n', b'\n'))
    old = path.read_text('utf8')
    new = transform(old)
    assert new != old, name
    path.write_text(new, encoding='utf8', newline='\n')

def replace(text, old, new):
    assert old in text, old[:100]
    return text.replace(old, new, 1)

edit('mtest/mscore/pluginhost/scorevideo_164_tests.inc', lambda t: replace(t,
'''    QMenu menu(main);
    addScoreVideoAction(&menu);
    auto action = main->findChild<QAction*>("kumo-score-video");
    QVERIFY(action);
    QVERIFY(!action->icon().isNull());''',
'''    // Use the actions created by normal startup. Creating a private menu here
    // hides omissions in the actual menu and toolbar initialization.
    auto action = main->findChild<QAction*>("kumo-score-video");
    QVERIFY(action);
    QVERIFY(!action->icon().isNull());
    auto toolbar = main->findChild<QToolBar*>("kumoPersonalTools");
    QVERIFY(toolbar && toolbar->actions().contains(action));
    auto tools = Workspace::findMenuFromString("menu-tools");
    QVERIFY(tools && main->menuBar()->actions().contains(tools->menuAction()));
    QCOMPARE(tools->actions().count(action), 1);

    QDir().mkpath(dataPath + "/workspaces/global");
    Workspace::writeGlobalMenuBar(main->menuBar());
    QFile saved(dataPath + "/workspaces/global/menubar.xml");
    QVERIFY(saved.open(QIODevice::ReadOnly));
    QByteArray xml = saved.readAll();
    saved.close();
    QVERIFY(xml.contains("<action>kumo-score-video</action>"));
    xml.replace("<action>kumo-score-video</action>", "");
    QVERIFY(saved.open(QIODevice::WriteOnly | QIODevice::Truncate));
    QCOMPARE(saved.write(xml), qint64(xml.size()));
    saved.close();
    XmlReader reader(xml);
    QVERIFY(reader.readNextStartElement());
    Workspace workspace;
    workspace.read(reader);
    main->updateMenus();
    main->updateMenus();
    tools = Workspace::findMenuFromString("menu-tools");
    QVERIFY(tools && main->menuBar()->actions().contains(tools->menuAction()));
    QCOMPARE(tools->actions().count(action), 1);
    QVERIFY(tools->actions().indexOf(action) < tools->actions().indexOf(getAction("transpose")));
    QCOMPARE(main->findChild<QAction*>("kumo-score-video"), action);
    QVERIFY(toolbar->actions().contains(action));'''))

edit('personal/docs/MIDI_TRACKS_160_GUIDE.md', lambda t: replace(t,
    ('![MIDI轨道、卷帘和力度](images/midi-tracks-160.png)\n\n' * 4).rstrip(),
    '![MIDI轨道、卷帘和力度](images/midi-tracks-160.png)'))

edit('personal/docs/SCORE_VIDEO_164_GUIDE.md', lambda t: replace(replace(t,
    '打开乐谱，点击“工具 → 动态乐谱视频…”，或编曲工具栏中的胶片图标。软件进入“后处理”视图，显示预览面板。面板标题写着当前谱名。',
    '打开乐谱，点击“工具 → 动态乐谱视频…”，或编曲工具栏中的胶片图标。软件进入“后处理”视图，显示预览面板。面板标题写着当前谱名。\n\n0.165.0 修复了旧工作区恢复后入口消失的问题，直接打开原来的工作区即可使用。个人工具统一由程序目录的 `kumo.ini` 中 `enable_exp_feature=true` 开启；修改后重启生效。'),
    '本功能见个人版本 0.164.0。', '本功能从个人版本 0.164.0 提供；菜单及工具栏入口在 0.165.0 修正。'))

edit('personal/docs/SCORE_VIDEO_164_CHECKS.md', lambda t: replace(t,
    '当前在既有 E 盘运行与编译目录检查，使用独立测试谱和生成的声音材料。官谱与用户原谱保持原样。',
    '2026-11-08补记：0.164的窗口检查直接创建面板，遗漏了完整程序启动及旧工作区恢复。实际发布程序的“工具”菜单和工具栏缺少入口。0.165补上动作登记、菜单恢复和工具栏创建顺序；本页保留谱行、声音及导出检查的具体结果。当前交付情况见[本轮审视](ROUND_165_REVIEW.md)。\n\n以下为0.164在既有E盘目录完成的检查，使用独立测试谱和生成的声音材料。官谱与用户原谱保持原样。'))

edit('personal/docs/PLAYBACK_159_GUIDE.md', lambda t: replace(t,
    '多轨MIDI、卷帘演奏调整、频谱、原曲关联控件及动态乐谱按本轮已批准计划逐批继续。',
    '本轮后续功能已分别提供：[MIDI轨道](MIDI_TRACKS_160_GUIDE.md)、[卷帘演奏调整](PERFORMANCE_TIMING_161_GUIDE.md)、[频谱](SPECTRUM_162_GUIDE.md)、[原曲关联控件](REFERENCE_CONTROLS_163_GUIDE.md)和[动态乐谱](SCORE_VIDEO_164_GUIDE.md)。'))

edit('personal/docs/source-map.tsv', lambda t: t +
    '动态乐谱入口\tmscore/scorevideo/scorevideopanel.cpp\tQAction* scoreVideoAction(\t942\t共用菜单与工具栏动作、旧工作区恢复及实验开关\tmtest/mscore/pluginhost/scorevideo_164_tests.inc\n')

(O / 'files.json').write_text(json.dumps(files, indent=2), encoding='utf8')
print('Updated the startup workflow check and instructions.')
