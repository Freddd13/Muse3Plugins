"""Interval-specific low voicing advice and certain onset span checks."""
from pathlib import Path
R=Path(__file__).resolve().parent; P=R.parent
p=P/'ArrangementAssistant/Rules.js';s=p.read_text(encoding='utf8')
anchor='// Pure ES5 rules.'
table='''// Piano register references transcribed from https://nicechord.com/post/low-interval-limit/
// Keys are actual semitone distance, including compound intervals; values are MIDI low notes.
// Enharmonic intervals with identical sounding pitches use the same acoustic reference.
var lowIntervalLimits={"1":52,"2":51,"3":48,"4":46,"5":46,"6":46,"7":34,"8":43,"9":41,"10":41,"11":41,"13":40,"14":39,"15":36,"16":34};
var lowIntervalNames={"1":"小二度","2":"大二度","3":"小三度","4":"大三度","5":"纯四度","6":"三全音","7":"纯五度","8":"小六度","9":"大六度","10":"小七度","11":"大七度","13":"小九度","14":"大九度","15":"小十度","16":"大十度"};
function pitchLabel(n){return Harmony.spelledName(n.tpc,n.pitch,false)+(Math.floor(n.pitch/12)-1);}
function lowVoicing(s,frame){
    var held=frame.notes.filter(function(n){return !n.grace&&(n.soundingEnd===undefined?n.logicalEnd:n.soundingEnd)>frame.tick;}),notes=[],reasons=[];
    var limits=s.config.lowIntervalLimits||lowIntervalLimits;
    for(var i=0;i<held.length;++i)for(var j=i+1;j<held.length;++j){
        var a=held[i],b=held[j];if(a.partId!==b.partId)continue;
        var distance=Math.abs(a.pitch-b.pitch),limit=limits[String(distance)];
        if(limit===undefined||Math.min(a.pitch,b.pitch)>=limit)continue;
        var pair=a.pitch<b.pitch?[a,b]:[b,a];
        var residual=pair.some(function(n){return n.logicalEnd<=frame.tick;}),arpeggio=pair[0].attackTick!==pair[1].attackTick;
        reasons.push(pitchLabel(pair[0])+"–"+pitchLabel(pair[1])+"（"+lowIntervalNames[String(distance)]+"），低端音低于参考 "+Harmony.sharpNames[limit%12]+(Math.floor(limit/12)-1)+"。"+(residual?"其中有踏板保留的声音。":arpeggio?"两音来自先后起音，目前仍同时发声。":"两音同时按下。"));
        pair.forEach(function(n){if(notes.indexOf(n)<0)notes.push(n);});
    }
    if(notes.length)issue(s,"harmony","low-cluster",frame.tick,notes,"低音排列可能较浑浊",reasons.join("\\n")+"\\n可试听这组音的清晰程度，再考虑拉开排列。参考表可在设置中调整。","提示");
}
function onsetSpans(s,frame){
    var groups={};frame.notes.forEach(function(n){if(n.attackTick!==frame.tick||n.grace||n.piano===false)return;var h=handFor(s,n,frame.tick);if(h.hand!=="left"&&h.hand!=="right")return;var k=(n.partId===undefined?0:n.partId)+":"+h.hand;(groups[k]||(groups[k]={hand:h.hand,notes:[],certain:true})).notes.push(n);groups[k].certain=groups[k].certain&&h.source.indexOf("自动推断")<0;});
    for(var key in groups){var g=groups[key],ns=g.notes,low=Math.min.apply(null,ns.map(function(n){return n.pitch;})),high=Math.max.apply(null,ns.map(function(n){return n.pitch;})),param=s.config[g.hand],maximum=white(low)&&white(high)?param.white:param.maximum;
        if(high-low>maximum)issue(s,"playability","span-"+g.hand,frame.tick,ns,(g.hand==="left"?"左手":"右手")+"这组新音跨度超过个人上限",pitchLabel(ns.filter(function(n){return n.pitch===low;})[0])+" 到 "+pitchLabel(ns.filter(function(n){return n.pitch===high;})[0])+"，跨度 "+(high-low)+" 半音，上限 "+maximum+"。"+(ns.some(function(n){return n.rolled;})?"已标记滚奏，可按展开顺序检查分手。":"这些音同时起音，可考虑调整分手或排列。"),g.certain&&!ns.some(function(n){return n.rolled;})?"需核查":"注意");
    }
}

'''
if 'var lowIntervalLimits=' not in s:s=s.replace(anchor,table+anchor)
s=s.replace('harmony:true,counterpoint:true,playability:true,','harmony:true,counterpoint:true,playability:true,lowIntervalLimits:clone(lowIntervalLimits),')
start=s.index('    // Bass-zone adjacent pitches');end=s.index('    if(!chord ||',start)
s=s[:start]+'    lowVoicing(s,frame);\n    var i;\n'+s[end:]
s=s.replace('source:"自动推断"};\n}', 'source:role && role.hand!=="auto"?"用户指定":"自动推断"};\n}',1)
s=s.replace('    if(report.limited || report.uncertain) {','    if(report.limited || report.uncertain) {\n        onsetSpans(s,frame);')
p.write_bytes(s.encode())
print('Low register and span rules prepared')
