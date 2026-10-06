"""Apply final native test/lifecycle refinements; run only in the named repository."""
from pathlib import Path

repo = Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def replace(path, before, after):
    file = repo / path
    text = file.read_text(encoding='utf-8')
    assert before in text, path
    with file.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(text.replace(before, after, 1))

replace('mscore/plugin/api/scoreobserver.h',
        '      Q_PROPERTY(bool enabled READ enabled WRITE setEnabled NOTIFY enabledChanged)',
        '      Q_PROPERTY(bool enabled READ enabled WRITE setEnabled NOTIFY enabledChanged)\n'
        '      Q_PROPERTY(bool surfaceVisible READ surfaceVisible NOTIFY surfaceVisibleChanged)')
replace('mscore/plugin/api/scoreobserver.h',
        '      bool enabled() const { return _enabled; }',
        '      bool enabled() const { return _enabled; }\n      bool surfaceVisible() const { return _surfaceVisible; }')
replace('mscore/plugin/api/scoreobserver.cpp',
        '#include "../qmlpluginengine.h"\n#include "mscore/musescore.h"\n', '')
replace('mtest/libmscore/note/tst_note.cpp', '#ifdef __MINGW32__ // apparently defined for 64bit too.',
        '#if defined(__MINGW32__) || defined(_MSC_VER) // Windows builds, including 64bit.')
replace('mtest/mscore/scoreobserver/tst_scoreobserver.cpp', '#include <QImage>', '#include <QImage>\n#include <QDomDocument>\n#include <QElapsedTimer>')
replace('mtest/mscore/scoreobserver/tst_scoreobserver.cpp', '      void cachedSnapshotBenchmark()', '''      void longScorePerformance()
            {
            QFile fixture(root + "/mscore/scoreobserver/piano.mscx");
            QVERIFY(fixture.open(QIODevice::ReadOnly));
            QDomDocument document;
            QVERIFY(document.setContent(fixture.readAll()));
            const auto scoreElement = document.documentElement().firstChildElement("Score");
            for (auto staff = scoreElement.firstChildElement("Staff"); !staff.isNull(); staff = staff.nextSiblingElement("Staff")) {
                  const auto measure = staff.firstChildElement("Measure");
                  for (int bar = 2; bar <= 1000; ++bar) {
                        auto next = measure.cloneNode(true).toElement();
                        next.setAttribute("number", bar);
                        auto voice = next.firstChildElement("voice");
                        voice.removeChild(voice.firstChildElement("Clef"));
                        voice.removeChild(voice.firstChildElement("TimeSig"));
                        staff.appendChild(next);
                        }
                  }
            QTemporaryDir directory;
            QFile longScore(directory.filePath("long.mscx"));
            QVERIFY(longScore.open(QIODevice::WriteOnly));
            longScore.write(document.toByteArray());
            longScore.close();
            std::unique_ptr<MasterScore> score(readCreatedScore(longScore.fileName()));
            QVERIFY(score);
            PluginAPI::Score wrapped(score.get());
            PluginAPI::ScoreObserver observer;
            observer.setScore(&wrapped);
            QCOMPARE(observer.snapshot(480, 0, 8).value("notes").toList().size(), 6);
            QElapsedTimer timer;
            timer.start();
            for (int bar = 0; bar < 1000; ++bar)
                  QCOMPARE(observer.snapshot(bar * 1920 + 480, 0, 8).value("notes").toList().size(), 6);
            qInfo("1000 bars / 6000 notes: index %.3f ms; 1000 cached snapshots %.3f ms",
                  observer.indexBuildMilliseconds(), double(timer.nsecsElapsed()) / 1000000.0);
            QCOMPARE(observer.indexBuildCount(), 1);
            }
      void cachedSnapshotBenchmark()''')

license_header = '''//=============================================================================
//  MuseScore
//  Music Composition & Notation
//
//  Copyright (C) 2026 Freddd13 and contributors
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License version 2
//  as published by the Free Software Foundation and appearing in
//  the file LICENCE.GPL
//=============================================================================

'''
for path in ['mscore/notepreview.h','mscore/plugin/api/scoreobserver.h','mscore/plugin/api/scoreobserver.cpp','mtest/mscore/scoreobserver/tst_scoreobserver.cpp']:
    file = repo / path
    text = license_header + file.read_text(encoding='utf-8')
    with file.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
print('Native lifecycle, long-score test and Windows note-test refinement applied')
