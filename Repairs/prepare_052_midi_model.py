from pathlib import Path
R=Path(__file__).resolve().parent/'native'
p=R/'audio/exports/midigate.h';s=p.read_text(encoding='utf8')
s=s.replace('QSet<QString> excluded;','QSet<QString> excluded;\n      QMap<QString,int> releaseOverrides; // Exact exported occurrence, this export only.')
s=s.replace('int sourceTick=-1,sourceMeasure=-1;','int sourceTick=-1,sourceMeasure=-1,sourceUtick=-1;')
s=s.replace('            return result;\n            }\n      };','''            for(auto& note:result){
                  const auto override=option.releaseOverrides.constFind(note.id);if(override==option.releaseOverrides.cend())continue;
                  const int at=override.value();
                  if(at==note.off){note.newOff=note.off;note.reason="manual-original";continue;}
                  if(preserved(note,option).isEmpty()&&at>note.on&&at<note.off&&durationMs(note.on,at)>=qBound(1.,option.minimumMs,5000.)&&releaseWindow(note,at)){
                        note.newOff=at;note.reason="manual-release";note.beforeKeys=note.afterKeys=note.beforeSpan=note.afterSpan=-1;
                        }
                  }
            return result;
            }
      };''')
s=s.replace('      int tickForMilliseconds(double milliseconds)','''      QPair<int,int> releaseBounds(const MidiGateNote& note,const QVector<MidiGatePedal>& pedals,const MidiGateOptions& option) const {
            if(!preserved(note,option).isEmpty())return {-1,-1};
            const int minimum=tickAt(seconds(note.on)+qBound(1.,option.minimumMs,5000.)/1000.);
            for(const auto& pedal:pedals)if(pedal.port==note.port&&pedal.channel==note.channel&&pedal.supported&&note.off<=pedal.up&&note.off>pedal.down){
                  const int first=qMax(qMax(note.on+1,minimum),pedal.down+1);if(first<note.off)return {first,note.off};}
            return {-1,-1};
            }
      int tickForMilliseconds(double milliseconds)''')
p.write_text(s,encoding='utf8',newline='\n')
p=R/'audio/exports/midigatefile.h';s=p.read_text(encoding='utf8').replace('int sourceTick=-1,sourceMeasure=-1;','int sourceTick=-1,sourceMeasure=-1,sourceUtick=-1;');p.write_text(s,encoding='utf8',newline='\n')
p=R/'audio/exports/midigatefile.cpp';s=p.read_text(encoding='utf8').replace('n.sourceTick=s.sourceTick;','n.sourceTick=s.sourceTick;n.sourceUtick=s.sourceUtick;');p.write_text(s,encoding='utf8',newline='\n')
p=R.parent/'apply_native.py';s=p.read_text(encoding='utf8');needle=" patch('mscore/plugin/plugin.cmake'";at=s.index(needle);s=s[:at]+" patch('audio/exports/exportmidi.cpp','tag.sourceTick = note->chord()->tick().ticks();','tag.sourceTick = note->chord()->tick().ticks();\\n                                                tag.sourceUtick = i->first;')\n"+s[at:];p.write_text(s,encoding='utf8',newline='\n')
HOST=R.parent.parent.parent/'muse3_dev/MuseScore'
p=R/'mscore/midicrop/midicroppanel.h';p.parent.mkdir(parents=True,exist_ok=True);s=(HOST/'mscore/midicrop/midicroppanel.h').read_text(encoding='utf8');s=s.replace('QMap<Score*,QSet<QString>> _exclusions;','QMap<Score*,QSet<QString>> _exclusions;\n      QMap<Score*,QMap<QString,int>> _releaseOverrides;');s=s.replace('_exclusions.clear();','_exclusions.clear(); _releaseOverrides.clear();');p.write_text(s,encoding='utf8',newline='\n')
p=R/'mscore/midicrop/midicroppanel.cpp';s=p.read_text(encoding='utf8').replace('result.gate.excluded=_exclusions.value(score);','result.gate.excluded=_exclusions.value(score);result.gate.releaseOverrides=_releaseOverrides.value(score);');s=s.replace('{"pedal-release",MidiCropPanel::tr(', '{"manual-release",MidiCropPanel::tr("已手动调整这次导出的松手位置")},\n            {"manual-original",MidiCropPanel::tr("已手动保留原按键长度")},\n            {"pedal-release",MidiCropPanel::tr(');p.write_text(s,encoding='utf8',newline='\n')
