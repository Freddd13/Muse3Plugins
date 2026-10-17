from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'staged056/plugins/ReferencePlayer/ReferencePlayer.view.qml';s=p.read_text(encoding='utf8')
s=s.replace('var retired=sessions.slice();','var retired=sessions.slice();if(media&&retired.indexOf(media)<0)retired.push(media);')
s=s.replace('Timer {id:documentTimer;interval:0;','Timer {id:documentTimer;interval:250;')
s=s.replace('onTracksChanged:scheduleDocument()','''onTracksChanged:scheduleDocument()
 onSelectedTrackChanged:scheduleDocument()
 onPlaybackModeChanged:scheduleDocument()
 onJointVolumeChanged:scheduleDocument()''')
s=s.replace('onReleased:{if(!root.usable)return;if(panning){root.sliceBefore=null;wave.requestPaint();return;}','onReleased:{if(!root.usable)return;if(panning){root.sliceBefore=null;root.refreshWaveform();return;}')
s=s.replace('root.viewEnd=root.viewStart+span;wave.requestPaint()}','root.viewEnd=root.viewStart+span;root.refreshWaveform()}')
s=s.replace(' function fitSlice(){',' function refreshWaveform(){wave.requestPaint();if(usable&&typeof media.requestWaveform==="function")media.requestWaveform(viewStart,viewEnd,Math.round(waveHost.width))}\n function fitSlice(){')
p.write_bytes(s.encode())
