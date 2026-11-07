from pathlib import Path
import hashlib,json,shutil,array,subprocess
R=Path(__file__).resolve().parents[1];O=R/'P2/out/repair-164';ffmpeg=shutil.which('ffmpeg');probe=shutil.which('ffprobe');assert ffmpeg and probe
report={}
for name,length,fps in [('native-score-164.mp4',8,10),('native-alpha-164.mov',8,10),('native-sound-164.mp4',8,10),('reference-sound-164.mp4',15.5,10),('ten-minutes-164.mp4',600,1),('default-1080-164.mp4',8,30),('frozen-source-closed-164.mp4',8,10)]:
    file=O/name;data=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-of','json',str(file)]));video=next(s for s in data['streams'] if s['codec_type']=='video');assert (video['width'],video['height'])==((1920,1080) if name=='default-1080-164.mp4' else (320,180));assert video['r_frame_rate']==str(fps)+'/1';assert abs(float(video['duration'])-length)<.0001;assert int(video['nb_frames'])==int(length*fps)
    if file.suffix=='.mov':
        assert video['codec_name']=='prores' and '4444' in video['profile'] and 'yuva' in video['pix_fmt']
        raw=subprocess.check_output([ffmpeg,'-v','error','-i',str(file),'-frames:v','1','-f','rawvideo','-pix_fmt','rgba','pipe:1']);alpha=raw[3::4];assert min(alpha)==0 and max(alpha)==255 and any(0<a<255 for a in alpha)
        subprocess.run([ffmpeg,'-v','error','-y','-i',str(file),'-frames:v','1',str(O/'encoded-alpha-164.png')],check=True)
    else:assert video['codec_name']=='h264'
    audio=[s for s in data['streams'] if s['codec_type']=='audio']
    if 'sound' in name or name in ('ten-minutes-164.mp4','frozen-source-closed-164.mp4'):
        assert len(audio)==1 and abs(float(audio[0]['duration'])-length)<.03
        raw=subprocess.check_output([ffmpeg,'-v','error','-i',str(file),'-map','0:a:0','-f','f32le','-ac','1','-ar','8000','pipe:1']);samples=array.array('f');samples.frombytes(raw);assert max(map(abs,samples))>.001
    else:assert not audio
    report[name]={'video':video,'audio':audio,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
(O/'video-files.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({name:{'videoSeconds':v['video']['duration'],'frames':v['video']['nb_frames'],'audioSeconds':[a['duration'] for a in v['audio']]} for name,v in report.items()},indent=2))
