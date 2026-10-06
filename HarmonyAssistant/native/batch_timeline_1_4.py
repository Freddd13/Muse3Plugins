from pathlib import Path
p=Path(__file__).resolve().parents[1]/'Timeline.js';s=p.read_text(encoding='utf-8')
a=s.index('function build(');b=s.index('function overlay(',a)
s=s[:a]+'''function createBuilder(frames, config, fallbackPart) {
    return {frames:frames,config:clone(config),fallbackPart:fallbackPart,byPart:{},keys:[],
        evidence:{},pedalResults:{},regions:[],phase:0,frameIndex:0,partIndex:0,rowIndex:0,previous:null,current:null};
}
function ingest(state, frame, end) {
    var parts=partsFor(frame,state.fallbackPart);
    if(end<=frame.tick)return;
    for(var p=0;p<parts.length;++p) {
        var part=parts[p].startTrack,notes=frame.notes.filter(function(n){return n.track>=part && n.track<parts[p].endTrack;});
        var rows=state.byPart[part]||(state.byPart[part]=[]),window=state.config.pedal?pedalAt(frame,part):null;
        rows.push({frame:frame,notes:notes,start:frame.tick,end:end,pedal:window});
        if(window && state.config.pedalMode===0) {
            var key=part+":"+window.start+":"+window.end;
            var evidence=state.evidence[key]||(state.evidence[key]={weights:{},all:[],seen:{},representative:[]});
            var width=Math.max(1,Math.min(end,window.end)-Math.max(frame.tick,window.start));
            for(var n=0;n<notes.length;++n) {
                var note=notes[n],pc=Harmony.mod12(note.pitch),held=note.end===undefined||note.end>frame.tick;
                evidence.weights[pc]=(evidence.weights[pc]||0)+width*(held?1:.18);
                var noteKey=note.track+":"+(note.attackTick===undefined?note.tick:note.attackTick)+":"+note.pitch;
                if(!evidence.seen[noteKey]){evidence.seen[noteKey]=true;evidence.all.push(note);}
            }
            if(!evidence.representative.length && notes.length>=3)evidence.representative=notes;
        }
    }
}
function evaluate(state, row, key) {
    var config=state.config,tonic=tonicAt(row.frame,config),window=row.pedal,result;
    var pedalKey=window?key+":"+window.start+":"+window.end:"";
    if(config.auto===false)result={root:Harmony.rootPcs[config.root],definition:config.quality,kind:"手动指定"};
    else if(window && config.pedalMode===0) {
        if(!state.pedalResults[pedalKey]) {
            var evidence=state.evidence[pedalKey];
            result=Harmony.detectWeighted(evidence.all,evidence.weights,null,tonic,config.keyMode===1,row.start);
            state.pedalResults[pedalKey]=describe(result,evidence.representative.length?evidence.representative:evidence.all,row.start,tonic,config.keyMode===1);
            state.pedalResults[pedalKey].kind="踏板区间 · "+(result.kind||"综合识别");
        }
        result=state.pedalResults[pedalKey];
    } else {
        var weights={},heldNotes=row.notes.filter(function(n){return n.end===undefined||n.end>row.start;});
        var attacks=heldNotes.filter(function(n){return (n.attackTick===undefined?n.tick:n.attackTick)===row.start;});
        var freshBass=attacks.length?bass(attacks,row.start):null;
        var strongAttack=attacks.length>=3 || (freshBass && heldNotes.some(function(n){return n.pitch>freshBass.pitch+12;}));
        for(var n=0;n<row.notes.length;++n) {
            var note=row.notes[n],pc=Harmony.mod12(note.pitch),active=note.end===undefined||note.end>row.start;
            var oldAttack=(note.attackTick===undefined?note.tick:note.attackTick)<row.start;
            var weight=active?(strongAttack && attacks.length>=3 && oldAttack?.3:1):(strongAttack?.12:.3);
            weights[pc]=Math.max(weights[pc]||0,weight);
        }
        result=Harmony.detectWeighted(row.notes,weights,strongAttack?null:state.previous,tonic,config.keyMode===1,row.start);
    }
    if(result.chord===undefined)result=describe(result,row.notes,row.start,tonic,config.keyMode===1);
    if(!row.notes.length){state.current=null;state.previous=null;return;}
    if(row.frame.imported)result=describe(row.frame,row.notes,row.start,tonic,config.keyMode===1);
    if(result.root<0){state.current=null;return;}
    var current=state.current;
    var same=current && current.end===row.start && signature(current)===signature(result);
    if(window && config.pedalMode===0 && current && current.pedalStart===window.start)same=true;
    if(same)current.end=row.end;
    else {
        current=clone(result);current.start=row.start;current.end=row.end;current.part=Number(key);
        current.id=key+":"+row.start;current.source=row.frame.imported?"imported":"auto";
        current.notes=clone(row.notes);current.bar=row.frame.bar;current.beat=row.frame.beat;
        current.pedalStart=window?window.start:-1;state.regions.push(current);state.current=current;
    }
    state.previous=result;
}
function step(state, limit) {
    for(var count=0;count<limit;++count) {
        if(state.phase===0) {
            if(state.frameIndex<state.frames.length) {
                var i=state.frameIndex++,frame=state.frames[i];
                ingest(state,frame,i+1<state.frames.length?state.frames[i+1].tick:(frame.scoreEnd||frame.tick+480));
                continue;
            }
            for(var key in state.byPart)state.keys.push(key);
            state.phase=1;
        }
        if(state.partIndex>=state.keys.length) {
            state.regions.sort(function(a,b){return a.start-b.start||a.part-b.part;});state.phase=2;return true;
        }
        key=state.keys[state.partIndex];var rows=state.byPart[key];
        if(state.rowIndex>=rows.length){state.partIndex++;state.rowIndex=0;state.previous=null;state.current=null;--count;continue;}
        evaluate(state,rows[state.rowIndex++],key);
    }
    return state.phase===2;
}
function build(frames, config, fallbackPart, overrides) {
    var state=createBuilder(frames,config,fallbackPart);
    while(!step(state,128)){}
    return overlay(state.regions,overrides||[]);
}
''' + s[b:]
s=s.replace('    var out=clone(regions);','    if(!overrides.length)return regions.slice();\n    var out=clone(regions);',1)
with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
