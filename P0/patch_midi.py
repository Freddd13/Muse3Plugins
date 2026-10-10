from apply_native import replace

def apply():
    from apply_native import HOST
    legacy="event.portamento() || note->chord()->isGrace();"
    if legacy in (HOST/"audio/exports/exportmidi.cpp").read_text(encoding="utf-8"):
        replace("audio/exports/exportmidi.cpp",legacy,"event.portamento() || note->chord()->isGrace() || event.pitch()!=note->ppitch() || note->chord()->tremolo();")
    replace('audio/exports/exports.cmake', '    ${CMAKE_CURRENT_LIST_DIR}/exportmidi.h', '    ${CMAKE_CURRENT_LIST_DIR}/midigatefile.cpp\n    ${CMAKE_CURRENT_LIST_DIR}/midigatefile.h\n    ${CMAKE_CURRENT_LIST_DIR}/midigate.h\n    ${CMAKE_CURRENT_LIST_DIR}/exportmidi.h')
    replace('audio/exports/exportmidi.h', '#include "audio/midi/midifile.h"', '#include "audio/midi/midifile.h"\n#include "midigatefile.h"')
    replace('audio/exports/exportmidi.h', '      MidiFile mf;', '''      MidiFile mf;
      MidiFile gateBaseline;
      bool collectGateData = false;
      MidiGateData gateData;
      QVector<MidiGateNote> gateReport;
      bool write(QIODevice*, bool, bool, const SynthesizerState&, const MidiExportOptions&);''')
    replace('audio/exports/exportmidi.cpp', '''bool ExportMidi::write(QIODevice* device, bool midiExpandRepeats, bool exportRPNs, const SynthesizerState& synthState)
      {
      mf.setDivision''', '''bool ExportMidi::write(QIODevice* device, bool midiExpandRepeats, bool exportRPNs, const SynthesizerState& synthState)
      { return write(device, midiExpandRepeats, exportRPNs, synthState, MidiExportOptions()); }

bool ExportMidi::write(QIODevice* device, bool midiExpandRepeats, bool exportRPNs, const SynthesizerState& synthState, const MidiExportOptions& options)
      {
      QVector<MidiGateSource> sources;
      mf.tracks().clear();
      mf.setDivision''')
    replace('audio/exports/exportmidi.cpp', '#include "libmscore/chordrest.h"', '#include "libmscore/chordrest.h"\n#include "libmscore/chord.h"\n#include "libmscore/note.h"')
    replace('audio/exports/exportmidi.cpp', '''                              if (event.type() == ME_NOTEON) {
                                    // use''', '''                              if (event.type() == ME_NOTEON) {
                                    if ((collectGateData || options.crop) && event.velo() > 0) {
                                          const Note* note = event.noteEventOwner() ? event.noteEventOwner() : event.note();
                                          if (note) {
                                                MidiGateSource tag;
                                                tag.track = staffIdx + 1;
                                                tag.on = pauseMap.addPauseTicks(i->first);
                                                tag.pitch = (!exportRPNs && event.portamento()) ? event.note()->pitch() : event.pitch();
                                                tag.channel = channel; tag.staff = staffIdx; tag.voice = note->chord()->track();
                                                tag.partName = part->instrumentName(note->tick());
                                                tag.piano = part->instrumentId(note->tick()).contains("piano", Qt::CaseInsensitive);
                                                tag.manual = note->chord()->playEventType() == PlayEventType::User || event.discard() || event.portamento() || note->chord()->isGrace() || event.pitch()!=note->ppitch() || note->chord()->tremolo();
                                                sources.append(tag);
                                                }
                                          }
                                    // use''')
    replace('audio/exports/exportmidi.cpp', '''      return !mf.write(device);
      }

bool ExportMidi::write(const QString& name''', '''      if (collectGateData || options.crop) {
            for (auto& source : sources) source.on += preRoll;
            gateData = midiGateSnapshot(mf, sources);
            if (options.crop) {
                  gateBaseline = mf;
                  MidiGateProcessor processor;
                  gateReport = processor.process(gateData, options.gate);
                  applyMidiGate(mf, gateReport);
                  }
            }
      return !mf.write(device);
      }

bool ExportMidi::write(const QString& name''')
    replace('mscore/CMakeLists.txt', '      taptempo/taptempo.h taptempo/taptempo.cpp', '      taptempo/taptempo.h taptempo/taptempo.cpp\n      midicrop/midicroppanel.h midicrop/midicroppanel.cpp')
    replace('mscore/exportdialog.h', 'class ExportDialog :', 'class MidiCropPanel;\n\nclass ExportDialog :')
    replace('mscore/exportdialog.h', '      Score* cs = nullptr;', '      Score* cs = nullptr;\n      MidiCropPanel* midiCrop = nullptr;')
    replace('mscore/exportdialog.cpp', '#include "preferences.h"', '#include "preferences.h"\n#include "midicrop/midicroppanel.h"')
    replace('mscore/exportdialog.cpp', '      setupUi(this);', '''      setupUi(this);
      midiCrop = new MidiCropPanel(midiPage, [this] {
            QList<Score*> scores;
            for (int i=0; i<listWidget->count(); ++i) {
                  auto item=static_cast<ExportScoreItem*>(listWidget->item(i));
                  if(item->isChecked())scores.append(item->score());
                  }
            return scores;
            });
      qobject_cast<QGridLayout*>(midiPage->layout())->addWidget(midiCrop,2,0);''')
    replace('mscore/exportdialog.cpp', '      loadValues();\n      loadScoreAndPartsList();', '      loadValues();\n      midiCrop->clearSessions();\n      loadScoreAndPartsList();')
    replace('mscore/exportdialog.cpp', '                  mscore->saveAs(score, true, definitiveFilename, suffix, &replacePolicy);', '''                  if (saveFormat == "mid" && midiCrop->enabled()) {
                        midiCrop->savePreferences();
                        QString original;
                        if (midiCrop->includeOriginal()) {
                              const QFileInfo info(definitiveFilename);
                              original = info.path()+"/"+info.completeBaseName()+"-original."+info.suffix();
                              if (QFileInfo::exists(original)) {
                                    if(replacePolicy == SaveReplacePolicy::SKIP_ALL)original.clear();
                                    else if(replacePolicy != SaveReplacePolicy::REPLACE_ALL) {
                                          const int response=mscore->askOverwriteAll(original);
                                          if(response==QMessageBox::No || response==QMessageBox::NoToAll)original.clear();
                                          if(response==QMessageBox::NoToAll)replacePolicy=SaveReplacePolicy::SKIP_ALL;
                                          if(response==QMessageBox::YesToAll)replacePolicy=SaveReplacePolicy::REPLACE_ALL;
                                          }
                                    }
                              }
                        if(!midiCrop->write(score,definitiveFilename,original))return;
                        }
                  else {
                        if(saveFormat == "mid")midiCrop->savePreferences();
                        mscore->saveAs(score, true, definitiveFilename, suffix, &replacePolicy);
                        }''')
    replace('mscore/preferences.cpp', '            {PREF_APP_PLAYBACK_FOLLOWSONG,', '''            {"export/midi/cropEnabled", new BoolPreference(false)},
            {"export/midi/cropOriginal", new BoolPreference(false)},
            {"export/midi/cropLength", new DoublePreference(.85)},
            {"export/midi/cropNext", new DoublePreference(.90)},
            {"export/midi/cropMinimumMs", new DoublePreference(120.)},
            {"export/midi/cropJitter", new DoublePreference(.02)},
            {"export/midi/cropSeed", new IntPreference(13013)},
            {PREF_APP_PLAYBACK_FOLLOWSONG,''')

if __name__ == '__main__':
    apply()
