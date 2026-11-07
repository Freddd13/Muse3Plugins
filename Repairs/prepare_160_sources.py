"""Add runtime-only, independently playable VST copies for reference MIDI."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];NATIVE=ROOT/'P2/native';HOST=ROOT.parent/'muse3_dev/MuseScore'
def edit(name,old,new):
    path=NATIVE/name
    if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((HOST/name).read_bytes())
    text=path.read_text('utf8')
    if new in text:return
    if text.count(old)!=1:raise RuntimeError((name,text.count(old),old))
    path.write_text(text.replace(old,new),encoding='utf8')
edit('audio/vst/vstsynth.h','  QVariantList pianoInstances;','  QVariantList pianoInstances;\n  QVariantList referenceSources;')
edit('audio/vst/vstsynth.h','  bool setConfiguration(const QVariantMap &);','  bool setConfiguration(const QVariantMap &);\n  bool setReferenceSources(const QVariantList&);')
edit('audio/vst/vstsynth.cpp','const auto instruments = enabled ? _rack.instruments() : value["slots"].toList();','const auto instruments = enabled ? _rack.instruments(true) : value["slots"].toList();')
edit('audio/vst/vstsynth.cpp','if (!c["commonPiano"].toString().isEmpty())\n      continue;','if (!c["commonPiano"].toString().isEmpty() || c.contains("referenceMidi"))\n      continue;')
edit('audio/vst/vstsynth.cpp','if (pianoInstances.isEmpty() && suppressedSlots.isEmpty()) return value;','if (pianoInstances.isEmpty() && suppressedSlots.isEmpty() && referenceSources.isEmpty()) return value;')
edit('audio/vst/vstsynth.cpp','rows.append(pianoInstances); result["slots"]=rows;','rows.append(pianoInstances); rows.append(referenceSources); result["slots"]=rows;')
edit('audio/vst/vstsynth.cpp','QVariantMap VstSynth::configuration(bool snapshot) {','''bool VstSynth::setReferenceSources(const QVariantList& sources) {
  if(VstHost::sameConfiguration({{"slots",referenceSources}},{{"slots",sources}}))return true;
  const auto current=configuration(true);
  referenceSources=sources;
  return setConfiguration(current);
}
QVariantMap VstSynth::configuration(bool snapshot) {''')
edit('audio/vst/rack.h','  QVariantList instruments() const;','  QVariantList instruments(bool includeReference = false) const;')
edit('audio/vst/rack.cpp','QVariantList Rack::instruments() const {','QVariantList Rack::instruments(bool includeReference) const {')
edit('audio/vst/rack.cpp','    auto v = s->config;\n    v["available"]','    if(!includeReference && s->config.contains("referenceMidi"))continue;\n    auto v = s->config;\n    v["available"]')
print('Prepared independent runtime MIDI sources')
