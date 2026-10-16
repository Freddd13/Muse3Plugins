from pathlib import Path
import shutil
HOST=Path(r'E:/programming/funcodes/muse3_dev/MuseScore')
ROOT=Path(__file__).resolve().parent
changed=set()
def edit(name,old,new):
 p=HOST/name;s=p.read_text(encoding='utf-8');assert s.count(old)==1,(name,old[:90],s.count(old));p.write_text(s.replace(old,new),encoding='utf-8',newline='\n');changed.add(name)
for name in ['libmscore/velocitybackup.h','libmscore/velocitybackup.cpp']:
 shutil.copy2(ROOT/'native'/name,HOST/name)
edit('libmscore/CMakeLists.txt','regionalconnections.cpp regionalconnections.h revisions.cpp','regionalconnections.cpp regionalconnections.h velocitybackup.cpp velocitybackup.h revisions.cpp')
edit('libmscore/note.cpp','#include "note.h"','#include "note.h"\n#include "velocitybackup.h"')
edit('libmscore/note.cpp','Note::~Note()\n      {','Note::~Note()\n      {\n      VelocityBackup::forget(this);')
edit('libmscore/note.cpp','      _veloOffset        = n._veloOffset;','      _veloOffset        = n._veloOffset;\n      VelocityBackup::copy(&n,this);')
edit('libmscore/note.cpp','void Note::write(XmlWriter& xml) const\n      {\n      xml.stag(this);','void Note::write(XmlWriter& xml) const\n      {\n      xml.stag(this);\n      VelocityBackup::write(this,xml);')
edit('libmscore/note.cpp','bool Note::readProperties(XmlReader& e)\n      {','bool Note::readProperties(XmlReader& e)\n      {\n      if(VelocityBackup::read(this,e))return true;')
edit('mscore/performanceeditor/parameteredit.cpp','#include "libmscore/undo.h"','#include "libmscore/undo.h"\n#include "libmscore/velocitybackup.h"')
p=HOST/'mscore/performanceeditor/parameteredit.h';s=p.read_text(encoding='utf-8');lines=[x for x in s.splitlines() if 'bool expression(' in x];assert len(lines)==1;old=lines[0];new=old.replace('QString* error = nullptr)', 'QString* error = nullptr,bool saveOriginal = false)');assert old!=new;p.write_text(s.replace(old,new),encoding='utf-8',newline='\n');changed.add('mscore/performanceeditor/parameteredit.h')
edit('mscore/performanceeditor/parameteredit.cpp','bool expression(Score* score,const QMap<Note*,VelocityEdit>& velocities,const QMap<int,double>& bpm,QString* error) {','bool expression(Score* score,const QMap<Note*,VelocityEdit>& velocities,const QMap<int,double>& bpm,QString* error,bool saveOriginal) {')
edit('mscore/performanceeditor/parameteredit.cpp',' score->startCmd();velocitiesImpl(score,velocities,false,false);temposImpl(score,bpm,-1,error,false,false);score->endCmd();return true;',' score->startCmd();if(saveOriginal)for(auto it=velocities.cbegin();it!=velocities.cend();++it)VelocityBackup::remember(score,it.key());velocitiesImpl(score,velocities,false,false);temposImpl(score,bpm,-1,error,false,false);score->endCmd();return true;')
edit('mscore/workflow/workflowexpression.cpp','ParameterEdit::expression(_score,velocities,bpm,&issue)','ParameterEdit::expression(_score,velocities,bpm,&issue,!_workflowApplyingPreview)')
for name in changed:
 dst=ROOT/'native'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((HOST/name).read_bytes())
print('Velocity backup hooks prepared')
