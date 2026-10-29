"""Read actual A/B MIDI and open the saved main writing in ordinary MuseScore."""
from pathlib import Path
import argparse,configparser,hashlib,importlib.util,json,os,subprocess,xml.etree.ElementTree as ET,zipfile
from fractions import Fraction

R=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('composition_midi',R/'Repairs/tests/check_midi_export_timing.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)

def notation(path):
    with zipfile.ZipFile(path) as archive:
        xml=ET.fromstring(archive.read(next(name for name in archive.namelist() if name.endswith('.mscx'))))
    return [(element.tag,element.findtext('durationType'),element.findtext('duration'),element.findtext('dots'),
             [(n.findtext('pitch'),n.findtext('tpc'),n.findtext('velocity'),n.findtext('veloType')) for n in element.findall('Note')])
            for element in xml.findall('.//Staff/Measure/voice/*') if element.tag in ('Chord','Rest')]

def normalized(data,field):
    return sorted((Fraction(event[0],data['division']),*event[1:]) for event in data[field])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,default=R/'P1/out/final-regression')
    parser.add_argument('--stock-exe',type=Path);args=parser.parse_args()
    output=R/'P2/out/composition-compatibility';output.mkdir(exist_ok=True)
    reports=[]
    for label in ('independent','actual'):
        report=json.loads((args.directory/f'composition-{label}.json').read_text('utf8'))
        archive=Path(report['saved']);before=hashlib.sha256(archive.read_bytes()).hexdigest()
        a,b=reader.read_midi(Path(report['midiA'])),reader.read_midi(Path(report['midi']))
        for choice,data,pitch,velocity in [('A',a,report['originalPitch'],report['velocityA']),('B',b,report['bPitch'],report['velocityB'])]:
            found=[event for event in data['note_events'] if event[2:]==(pitch,velocity)
                   and Fraction(event[0],data['division'])==Fraction(report['tick'],480)]
            assert found,(label,choice,'edited note missing from actual MIDI')
        assert normalized(a,'control_events')==normalized(b,'control_events'),(label,'controller changed between writings')
        assert len(a['notes'])==len(b['notes']) and a['notes'],label
        row={'label':label,'aVelocity':report['velocityA'],'bVelocity':report['velocityB'],
             'notes':len(b['notes']),'pedalEvents':sum(cc==64 for _,cc,_ in a['controllers']),
             'archiveSha256':before,'nativeAandB':True}
        if args.stock_exe:
            settings=output/'stock-settings/MuseScore/MuseScore3.ini';settings.parent.mkdir(parents=True,exist_ok=True)
            config=configparser.ConfigParser(interpolation=None);config.optionxform=str
            if settings.is_file():config.read(settings,encoding='utf8')
            if not config.has_section('io'):config.add_section('io')
            config.set('io',r'midi\exportRPNs','true' if any(event[2]==101 for event in a['control_events']) else 'false')
            config.set('io',r'midi\expandRepeats','true')
            with settings.open('w',encoding='utf8',newline='\n') as stream:config.write(stream)
            def export(source,target):
                (output/'stock-settings').mkdir(exist_ok=True)
                env=dict(os.environ,KUMO_MCP_AUTOSTART='0')
                env.pop('QT_QPA_PLATFORM',None);env.pop('QT_QUICK_BACKEND',None)
                env['TEMP']=env['TMP']=str(R/'P1/out/final-regression/tmp')
                startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
                try:
                    run=subprocess.run([str(args.stock_exe),'-s','-m','-f','-c',str(output/'stock-settings'),'-o',str(target),str(source)],
                        cwd=output,env=env,startupinfo=startup,capture_output=True,timeout=120)
                except subprocess.TimeoutExpired as error:
                    (output/(target.name+'.log')).write_bytes((error.stdout or b'')+(error.stderr or b''))
                    raise
                (output/(target.name+'.log')).write_bytes(run.stdout+run.stderr)
                assert run.returncode==0 and target.is_file(),target
            ordinary=output/f'{label}-ordinary.mscz';export(archive,ordinary)
            assert notation(archive)==notation(ordinary),(label,'ordinary notation differs')
            first,again=output/f'{label}-ordinary.mid',output/f'{label}-resaved.mid'
            export(archive,first);export(ordinary,again)
            for midi in (first,again):
                data=reader.read_midi(midi)
                assert normalized(data,'note_events')==normalized(a,'note_events'),(label,midi.name,'note events differ')
                assert normalized(data,'control_events')==normalized(a,'control_events'),(label,midi.name,'control events differ')
            row['ordinaryNotationAndMidi']=True
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==before
        reports.append(row);print(row,flush=True)
    (output/'report.json').write_bytes(json.dumps(reports,ensure_ascii=False,indent=2).encode('utf8'))
    return 0

if __name__=='__main__':raise SystemExit(main())
