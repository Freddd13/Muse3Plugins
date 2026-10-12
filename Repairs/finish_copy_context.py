from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
HOST=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
text=subprocess.check_output(['git','show','HEAD:mscore/workflow/workflowvariants.cpp'],cwd=HOST).decode('utf8')
text=text.replace('#include "libmscore/part.h"','#include "libmscore/part.h"\n#include "libmscore/instrument.h"\n#include <QRegularExpression>')
needle=' return {{"context",from==0?'
assert text.count(needle)==1
normalization=''' // Saving a score checks whether its MIDI routing can be omitted as a default.
 // Compare the actual routing, rather than that transient serialization choice.
 if(from==0){
  QByteArray routing;bool complete=true;
  for(auto part:_score->parts())for(auto channel:part->instrument()->channel()){
   int index=channel->channel();auto master=_score->masterScore();
   if(index<0||size_t(index)>=master->midiMapping().size()){complete=false;break;}
   routing+=QByteArray::number(master->midiPort(index))+","+QByteArray::number(master->midiChannel(index))+";";
  }
  if(complete){
   QString xml=QString::fromUtf8(context);
   static const QRegularExpression optionalRoute("[ \\t]*<midi(?:Port|Channel)>[0-9]+</midi(?:Port|Channel)>\\\\r?\\\\n");
   xml.remove(optionalRoute);context=xml.toUtf8();context+="\\nActualMidiRouting:"+routing;
  }
 }
'''
text=text.replace(needle,normalization+needle)
(ROOT/'native/mscore/workflow/workflowvariants.cpp').write_bytes(text.encode('utf8'))
test=ROOT/'native/mtest/mscore/p1native/tst_p1native.cpp'
text=test.read_text(encoding='utf8')
begin=text.index('  auto contextBytes=');end=text.index('  auto s=mscore->readScore',begin)
text=text[:begin]+text[end:]
text=text.replace('  const QByteArray beforeContext;\n','')
begin=text.index('  if(duplicate["context"]!=first["context"])');end=text.index('  QCOMPARE(duplicate["context"]',begin)
text=text[:begin]+text[end:]
test.write_bytes(text.encode('utf8'))
