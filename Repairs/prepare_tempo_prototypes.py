from pathlib import Path
ROOT=Path(__file__).resolve().parent;HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
def change(path,old,new):
 target=ROOT/'native'/path;target.parent.mkdir(parents=True,exist_ok=True)
 s=target.read_text(encoding='utf8') if target.exists() else (HOST/path).read_text(encoding='utf8')
 assert s.count(old)==1,(path,old,s.count(old));target.write_bytes(s.replace(old,new).encode('utf8'))
change('mscore/performanceeditor/parameteredit.h','class TextLine;','class TextLine;\nclass TempoText;')
change('mscore/performanceeditor/parameteredit.h','bool tempoCurve(Score*, int from, int until, TextLine* target, bool replace, QString* error = nullptr);','bool tempoCurve(Score*, int from, int until, TextLine* target, bool replace, QString* error = nullptr, const TextLine* prototype = nullptr);')
change('mscore/performanceeditor/parameteredit.h','bool restoreTempo(Score*, int tick, QString* error = nullptr);','bool restoreTempo(Score*, int tick, QString* error = nullptr, const TempoText* prototype = nullptr);')
change('mscore/performanceeditor/parameteredit.cpp','bool tempoCurve(Score* input, int from, int until, TextLine* target, bool replace, QString* error)','bool tempoCurve(Score* input, int from, int until, TextLine* target, bool replace, QString* error, const TextLine* prototype)')
change('mscore/performanceeditor/parameteredit.cpp','''            target = new TextLine(score, true); target->setTrack(0); target->setTick(Fraction::fromTicks(from)); target->setTicks(Fraction::fromTicks(until - from));
            target->setBeginText("rit."); target->setContinueText("(rit.)"); target->setBeginFontStyle(FontStyle::Italic); target->setLineStyle(Qt::DashLine);''','''            target = prototype ? prototype->clone() : new TextLine(score, true);
            target->eraseSpannerSegments(); target->setScore(score); target->setParent(nullptr); target->setSystemFlag(true);
            target->setTrack(0); target->setTick(Fraction::fromTicks(from)); target->setTicks(Fraction::fromTicks(until - from));
            if(!prototype){target->setBeginText("rit."); target->setContinueText("(rit.)"); target->setBeginFontStyle(FontStyle::Italic); target->setLineStyle(Qt::DashLine);}''')
change('mscore/performanceeditor/parameteredit.cpp','bool restoreTempo(Score* input, int tick, QString* error)','bool restoreTempo(Score* input, int tick, QString* error, const TempoText* prototype)')
change('mscore/performanceeditor/parameteredit.cpp','      auto text = new TempoText(score); text->setTrack(0); text->setParent(segment); text->setFollowText(false); text->setXmlText("a tempo"); text->setProperty(Pid::TEMPO_RESTORE_MODE, 1);','      auto text = prototype ? prototype->clone() : new TempoText(score); text->setScore(score); text->setTrack(0); text->setParent(segment); text->setFollowText(false); if(!prototype)text->setXmlText("a tempo"); text->setProperty(Pid::TEMPO_RESTORE_MODE, 1);')
