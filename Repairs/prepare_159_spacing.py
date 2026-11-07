"""Stage the independent grace-spacing properties in the existing native files."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "P2/native"
HOST = ROOT.parent.parent.parent / "muse3_dev/MuseScore"


def edit(path, changes):
    target = ROOT / path
    text = (target if target.exists() else HOST / path).read_text(encoding="utf-8")
    for before, after in changes:
        if before not in text:
            raise RuntimeError(f"Missing expected source in {path}: {before[:65]}")
        text = text.replace(before, after)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


edit("libmscore/property.h", [("      PEDAL_PLAYBACK,\n      END", "      PEDAL_PLAYBACK,\n      GRACE_SPACING,\n      GRACE_MAIN_SPACING,\n      END")])
edit("libmscore/property.cpp", [('      { Pid::END,', '      { Pid::GRACE_SPACING, P_TYPE::REAL, true, "graceSpacing", "extra inter-grace spacing" },\n      { Pid::GRACE_MAIN_SPACING, P_TYPE::REAL, true, "graceMainSpacing", "extra grace-to-main spacing" },\n      { Pid::END,')])
edit("libmscore/chord.h", [("      double _graceDuration = 65.0;", "      double _graceDuration = 65.0;\n      double _graceSpacing = 0.0, _graceMainSpacing = 0.0;")])
edit("libmscore/chord.cpp", [
    ("      _graceDuration = c._graceDuration;", "      _graceDuration = c._graceDuration;\n      _graceSpacing = c._graceSpacing; _graceMainSpacing = c._graceMainSpacing;"),
    ("            writeProperty(xml, Pid::GRACE_DURATION);", "            writeProperty(xml, Pid::GRACE_DURATION);\n            writeProperty(xml, Pid::GRACE_SPACING);\n            writeProperty(xml, Pid::GRACE_MAIN_SPACING);"),
    ('      else if (tag == "graceDuration") readProperty(tag, e, Pid::GRACE_DURATION);', '      else if (tag == "graceDuration") readProperty(tag, e, Pid::GRACE_DURATION);\n      else if (tag == "graceSpacing") readProperty(tag, e, Pid::GRACE_SPACING);\n      else if (tag == "graceMainSpacing") readProperty(tag, e, Pid::GRACE_MAIN_SPACING);'),
    ("pid == Pid::GRACE_DURATION))", "pid == Pid::GRACE_DURATION || pid == Pid::GRACE_SPACING || pid == Pid::GRACE_MAIN_SPACING))"),
    ("propertyId == Pid::GRACE_DURATION))", "propertyId == Pid::GRACE_DURATION || propertyId == Pid::GRACE_SPACING || propertyId == Pid::GRACE_MAIN_SPACING))"),
    ("            case Pid::GRACE_DURATION: return _graceDuration;", "            case Pid::GRACE_DURATION: return _graceDuration;\n            case Pid::GRACE_SPACING: return _graceSpacing;\n            case Pid::GRACE_MAIN_SPACING: return _graceMainSpacing;"),
    ("            case Pid::GRACE_DURATION: return 65.0;", "            case Pid::GRACE_DURATION: return 65.0;\n            case Pid::GRACE_SPACING:\n            case Pid::GRACE_MAIN_SPACING: return 0.0;"),
    ("            case Pid::GRACE_APPEARANCE: {", "            case Pid::GRACE_SPACING:\n            case Pid::GRACE_MAIN_SPACING:\n                  if (!std::isfinite(v.toDouble())) return false;\n                  (propertyId == Pid::GRACE_SPACING ? _graceSpacing : _graceMainSpacing) = qBound(-2.0, v.toDouble(), 8.0); break;\n            case Pid::GRACE_APPEARANCE: {"),
    ("minNoteDist + g->_spaceLw;", "qMax(0.0, minNoteDist + _graceSpacing * spatium()) + g->_spaceLw;"),
    ("qreal xl = -(_spaceLw + minNoteDistance) - chordX;", "qreal xl = -(_spaceLw + qMax(0.0, minNoteDistance + _graceMainSpacing * spatium())) - chordX;"),
    ("xl -= g->_spaceLw + minNoteDistance * graceMag;", "xl -= g->_spaceLw + qMax(0.0, minNoteDistance * graceMag + _graceSpacing * spatium());"),
    ("qreal xr = _spaceRw;", "qreal xr = _spaceRw + _graceMainSpacing * spatium();"),
    ("xr += g->_spaceLw + g->_spaceRw + minNoteDistance * graceMag;", "xr += g->_spaceLw + g->_spaceRw + qMax(0.0, minNoteDistance * graceMag + _graceSpacing * spatium());"),
    ("qreal xl = -(_spaceLw + minNoteDistance);", "qreal xl = -(_spaceLw + qMax(0.0, minNoteDistance + _graceMainSpacing * spatium()));"),
    ("xl -= c->_spaceLw + minNoteDistance * graceMag;", "xl -= c->_spaceLw + qMax(0.0, minNoteDistance * graceMag + _graceSpacing * spatium());"),
    ("qreal xr = fc * (_spaceRw + minNoteDistance);", "qreal xr = fc * (_spaceRw + minNoteDistance) + _graceMainSpacing * spatium();"),
    ("xr += c->_spaceRw + minNoteDistance * graceMag;", "xr += c->_spaceRw + qMax(0.0, minNoteDistance * graceMag + _graceSpacing * spatium());"),
])
edit("mscore/inspector/inspectorNote.cpp", [
    ('      auto preset = new QPushButton(tr("应用快速拍前预设"), _gracePanel);', '      iiList.push_back(scrubProperty(_gracePanel, tr("倚音间额外间距"), Pid::GRACE_SPACING, -2, 8, .1, tr(" 谱间"), 1));\n      iiList.push_back(scrubProperty(_gracePanel, tr("与主音额外间距"), Pid::GRACE_MAIN_SPACING, -2, 8, .1, tr(" 谱间"), 1));\n      auto preset = new QPushButton(tr("应用快速拍前预设"), _gracePanel);'),
])
print("已准备倚音间距、序列化、撤销属性及检视器")
