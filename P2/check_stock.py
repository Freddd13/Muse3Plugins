"""Open and resave the host-generated fixture with the official MuseScore 3.6.2."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,zipfile,argparse
import xml.etree.ElementTree as ET

R=Path(__file__).resolve().parent
work=R/'out/compat-3.6.2'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--score',type=Path,default=R.parent/'P1/out/final-regression/transcription-compat-059.mscz')
parser.add_argument('--metadata',default='kumo.transcription')
parser.add_argument('--label',default='')
args=parser.parse_args()
source=args.score.resolve()
suffix=('-'+args.label) if args.label else ''

program=work/'extracted/layout/MuseScore 3/bin/MuseScore3.exe'
target=work/('roundtrip'+suffix+'.mscz')
assert source.is_file() and program.is_file()
settings=work/'settings';settings.mkdir(exist_ok=True)
env=dict(os.environ,QT_QPA_PLATFORM='windows',QT_QUICK_BACKEND='software',QML_DISABLE_DISK_CACHE='1')
try:
 result=subprocess.run([str(program),'-s','-m','-c',str(settings),'-o',str(target),str(source)],
                       env=env,cwd=work,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=40)
except subprocess.TimeoutExpired as error:
 output=error.stdout or b''
 (work/('roundtrip'+suffix+'.log')).write_bytes(output)
 print(output.decode('utf8',errors='replace')[-4000:])
 raise SystemExit(124)
(work/('roundtrip'+suffix+'.log')).write_bytes(result.stdout)
if result.returncode or not target.exists():
 print(result.stdout.decode('utf8',errors='replace')[-3000:]);raise SystemExit(result.returncode or 1)

def xml(path):
 with zipfile.ZipFile(path) as archive:
  name=next(n for n in archive.namelist() if n.endswith('.mscx'))
  return ET.fromstring(archive.read(name))
before,after=xml(source),xml(target)
def notes(root):
 return [(n.findtext('pitch'),n.findtext('tpc'),n.findtext('veloType'),n.findtext('velocity')) for n in root.findall('.//Staff/Measure/voice/Chord/Note')]
def durations(root):
 return [(element.tag,element.findtext('durationType'),len(element.findall('dots'))) for element in root.findall('.//Staff/Measure/voice/*') if element.tag in ('Chord','Rest')]
def marker(root):
 return root.find('Score/metaTag[@name="'+args.metadata+'"]').text
assert notes(before)==notes(after),(notes(before),notes(after))
assert durations(before)==durations(after)
assert json.loads(marker(before))==json.loads(marker(after))
report={'program':'MuseScore 3.6.2.548021803 (official x64)', 'exit':result.returncode,
        'source':str(source),'saved':str(target),'notes':len(notes(after)),
        'sameNotes':True,'sameDurations':True,'sameTranscriptionData':args.metadata=='kumo.transcription','sameMetadata':args.metadata,
        'binarySha256':hashlib.sha256(program.read_bytes()).hexdigest(),
        'installerSha256':'fa3ca0f8cc5b0e8b0c0bb8ef11e227b9b27b2a5c9da28dab58bafcbb0eb657d0'}
(work/('report'+suffix+'.json')).write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps(report,ensure_ascii=True))
