"""Add value-based tie/slur connections to the regional writing module."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
HOST = Path('E:/programming/funcodes/muse3_dev/MuseScore')

def change(text, old, new):
    if new in text:
        return text
    if text.count(old) != 1:
        raise RuntimeError('Check the regional module before editing: ' + old[:90])
    return text.replace(old, new, 1)

def apply():
    for name in ['libmscore/regionalconnections.h', 'libmscore/regionalconnections.cpp']:
        src = ROOT/'native'/name
        dst = HOST/name
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            raise RuntimeError('Merge the existing file: ' + name)
        dst.write_bytes(src.read_bytes())
    p = HOST/'libmscore/regionalvariants.cpp'
    s = p.read_text(encoding='utf-8')
    s = change(s, '#include "regionalvariants.h"', '#include "regionalvariants.h"\n#include "regionalconnections.h"')
    s = change(s, 'bool replace(Score *score, const QVariantMap &group, const QByteArray &data, QString *problem) {',
               'bool replace(Score *score, const QVariantMap &group, const QByteArray &data, QString *problem, const QVariantMap &writing = {}) {\n      if(writing.contains("connections") && !RegionalConnections::validate(writing.value("connections").toList(),group,problem))return false;')
    s = change(s, '      QList<Spanner *> remove;', '      RegionalConnections::remove(score,start,end,tracks);\n      QList<Spanner *> remove;')
    s = change(s, '      return true;\n}\nQVariantMap capturedState',
               '      if(writing.contains("connections") && !RegionalConnections::restore(score,writing.value("connections").toList(),problem))return false;\n      return true;\n}\nQVariantMap capturedState')
    s = change(s, '            v["data"] = QString::fromLatin1(packed(bytes));\n            variants[selected] = v;',
               '            v["data"] = QString::fromLatin1(packed(bytes));\n            v["connections"] = RegionalConnections::capture(score,g.value("start").toInt(),g.value("end").toInt(),trackSet(g.value("tracks").toList()),problem);\n            if(!problem->isEmpty())return {};\n            variants[selected] = v;')
    s = change(s, '      data["groups"] = groups;\n      return data;\n}', '      data["groups"] = groups;\n      data["schema"] = 2;\n      return data;\n}')
    start = s.index('                  for (auto note : chord->notes())\n                        for (auto tie : {note->tieBack(), note->tieFor()})', s.index('QVariantMap check('))
    finish = s.index('      return {{"ok", true}, {"start", start}', start)
    s = s[:start] + '''            }
      QString connectionError;
      RegionalConnections::capture(score,start,end,tracks,&connectionError);
      if(!connectionError.isEmpty())return error(connectionError,start,end);
''' + s[finish:]
    s = change(s, '      return document.toByteArray();\n}\nQVariantMap create(',
               '      RegionalConnections::strip(document);\n      return document.toByteArray();\n}\nQVariantMap create(')
    s = change(s, '{"id", variant}, {"name", QObject::tr("原写法")}, {"data", QString::fromLatin1(packed(bytes))}};',
               '{"id", variant}, {"name", QObject::tr("A · 当前写法")}, {"data", QString::fromLatin1(packed(bytes))},\n           {"connections",RegionalConnections::capture(score,start,end,tracks,&problem)}};')
    s = s.replace('data["schema"] = 1;', 'data["schema"] = 2;')
    s = change(s, 'bool ok = replace(score, g, bytes, &problem);', 'bool ok = replace(score, g, bytes, &problem, variants[target].toMap());')
    s = change(s, 'bool ok = replace(copy.get(), g, bytes, &problem);', 'bool ok = replace(copy.get(), g, bytes, &problem, variants[main].toMap());')
    s = change(s, 'bool ok = replace(copy.get(), old, bytes, &problem);', 'bool ok = replace(copy.get(), old, bytes, &problem, v);')
    s = change(s, '            v["data"] = QString::fromLatin1(packed(bytes));\n            versions[i] = v;',
               '            v["data"] = QString::fromLatin1(packed(bytes));\n            v["connections"] = RegionalConnections::capture(copy.get(),start,end,trackSet(old.value("tracks").toList()),&problem);\n            if(!problem.isEmpty())return error(problem);\n            versions[i] = v;')
    s = change(s, 'QVariantMap{{"id", key}, {"name", name.left(80)}, {"data", QString::fromLatin1(packed(bytes))}});',
               'QVariantMap{{"id", key}, {"name", name.left(80)}, {"data", QString::fromLatin1(packed(bytes))},\n                      {"connections",RegionalConnections::capture(source,start,end,trackSet(g.value("tracks").toList()),&problem)}});')
    s = change(s, 'if (data.value("schema").toInt() != 1) {', 'if (data.value("schema").toInt() != 1 && data.value("schema").toInt() != 2) {')
    s = change(s, '                  if (!validateFragment(g, xml, problem))\n                        return false;',
               '                  if (!validateFragment(g, xml, problem))\n                        return false;\n                  if(v.contains("connections") && !RegionalConnections::validate(v.value("connections").toList(),g,problem))return false;')
    s = change(s, '!replace(score, g, fragment, problem)', '!replace(score, g, fragment, problem, variants[current].toMap())')
    p.write_text(s, encoding='utf-8', newline='\n')
    (ROOT/'native/libmscore/regionalvariants.cpp').write_bytes(p.read_bytes())
    p=HOST/'libmscore/CMakeLists.txt';s=p.read_text(encoding='utf-8')
    s=change(s,'regionalvariants.cpp regionalvariants.h revisions.cpp','regionalvariants.cpp regionalvariants.h regionalconnections.cpp regionalconnections.h revisions.cpp')
    s=change(s,'set_source_files_properties(regionalvariants.cpp scorefile.cpp','set_source_files_properties(regionalvariants.cpp regionalconnections.cpp scorefile.cpp')
    p.write_text(s,encoding='utf-8',newline='\n')

if __name__ == '__main__':
    apply()
