"""Inspect only the exception thread's module addresses in a MuseScore crash dump."""
import mmap,struct,sys,json
from pathlib import Path
path=Path(sys.argv[1])
with path.open('rb') as stream:
 data=mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ)
 count,directory=struct.unpack_from('<II',data,8)
 entries={}
 for index in range(count):
  kind,size,rva=struct.unpack_from('<III',data,directory+index*12);entries[kind]=(size,rva)
 modules=[]
 rva=entries[4][1];length=struct.unpack_from('<I',data,rva)[0]
 for index in range(length):
  pos=rva+4+108*index;base,size=struct.unpack_from('<QI',data,pos);name=struct.unpack_from('<I',data,pos+20)[0]
  chars=struct.unpack_from('<I',data,name)[0];name=data[name+4:name+4+chars].decode('utf-16le')
  modules.append((base,size,name))
 er=entries[6][1];thread=struct.unpack_from('<I',data,er)[0];code=struct.unpack_from('<I',data,er+8)[0]
 context=struct.unpack_from('<I',data,er+164)[0]
 rsp=struct.unpack_from('<Q',data,context+152)[0];rip=struct.unpack_from('<Q',data,context+248)[0]
 def identify(address):
  for base,size,name in modules:
   if base<=address<base+size:return Path(name).name+'+0x'+format(address-base,'x')
  return None
 print(json.dumps({'code':hex(code),'rip':identify(rip),'thread':thread}))
 tr=entries[3][1];length=struct.unpack_from('<I',data,tr)[0]
 for index in range(length):
  pos=tr+4+48*index
  if struct.unpack_from('<I',data,pos)[0]!=thread:continue
  start,size,location=struct.unpack_from('<QII',data,pos+24)
  begin=location+max(0,rsp-start)
  frames=[]
  for offset in range(begin,min(location+size,begin+4096),8):
   address=struct.unpack_from('<Q',data,offset)[0];name=identify(address)
   if name:frames.append(name)
  print(json.dumps(frames[:100],indent=2))
