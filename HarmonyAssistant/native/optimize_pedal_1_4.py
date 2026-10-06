from pathlib import Path
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
stage=Path(__file__).resolve().parent/'next-1.4'
p=stage/'mscore/plugin/api/scoreobserver.cpp';s=p.read_text(encoding='utf-8')
s=s.replace('      for (auto measure = _score->firstMeasure();', '''      std::sort(_pedals.begin(),_pedals.end(),[](const auto& a,const auto& b) {
            return a.firstTrack<b.firstTrack || (a.firstTrack==b.firstTrack && a.start<b.start);
            });
      QVector<PedalWindow> continuous;
      for (const auto& window:_pedals) {
            if (!continuous.isEmpty() && continuous.back().firstTrack==window.firstTrack && window.start<continuous.back().end)
                  continuous.back().end=qMax(continuous.back().end,window.end);
            else continuous.append(window);
            }
      _pedals=continuous;
      for (auto measure = _score->firstMeasure();''',1)
old='''            if (pedal) for (const auto& window : _pedals)
                  if (track >= window.firstTrack && track < window.endTrack && window.start <= tick && tick < window.end) {
                        // Include a note already held when the pedal goes down.
                        start = qMin(start, window.start); heldByPedal = true;
                        }'''
assert old in s
s=s.replace(old,'''            if (pedal) if (const auto window=pedalWindow(tick,track)) {
                  // Include a note already held when the pedal goes down.
                  start=qMin(start,window->start);heldByPedal=true;
                  }''',1)
a=s.index('      for (const auto& window:_pedals) if (window.firstTrack<endTrack');b=s.index('      result.insert("parts",parts);',a)
s=s[:a]+'''      for (const auto part:_score->parts()) if (part->startTrack()<endTrack && part->endTrack()>firstTrack)
            if (const auto window=pedalWindow(tick,part->startTrack()))
                  windows.append(QVariantMap{{"start",window->start},{"end",window->end},{"firstTrack",window->firstTrack},{"endTrack",window->endTrack}});
''' + s[b:]
marker='QVariantList ScoreObserver::contextNotes('
a=s.index(marker)
s=s[:a]+'''const ScoreObserver::PedalWindow* ScoreObserver::pedalWindow(int tick,int track) const
      {
      const int part=_score->staff(track/VOICES)->part()->startTrack();
      const auto after=std::upper_bound(_pedals.cbegin(),_pedals.cend(),std::make_pair(part,tick),
            [](const auto& key,const auto& window) {
                  return key.first<window.firstTrack || (key.first==window.firstTrack && key.second<window.start);
                  });
      if (after==_pedals.cbegin())return nullptr;
      const auto& window=*(after-1);
      return window.firstTrack==part && tick<window.end ? &window : nullptr;
      }

''' + s[a:]
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
p=stage/'mscore/plugin/api/scoreobserver.h';s=p.read_text(encoding='utf-8')
s=s.replace('      QVariantList contextNotes(', '      const PedalWindow* pedalWindow(int tick,int track) const;\n      QVariantList contextNotes(',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
print('Staged logarithmic per-part pedal lookup and bounded frame metadata.')
