"""Task ranges, native performance and supplied reference data stay distinct."""
import asyncio
import copy
import pytest
from src.context.service import ContextService, ContextError
from src.context.packet import read_request, overlaps, rendered_performance
from src.tools.connection import score_data_projection

SCOPE={"start":480,"end":1440,"firstTrack":0,"endTrack":8,"firstMeasure":2,"lastMeasure":2}

class Native:
    def __init__(self):
        self.calls=[];self.revision="score:1";self.session="score";self.playback="play:1";self.page_changed=False
        self.information={"assertions":[{"id":"near","target":{"start":480,"end":960},"origin":{"kind":"user"},"value":"旋律在低声部"},
                        {"id":"away","target":{"start":4800,"end":5760},"origin":{"kind":"user"}}],
            "materials":[{"id":"recording","type":"recording","origin":{"kind":"user"}}],
            "alignments":[{"id":"link","from":{"materialId":"recording","start":20,"end":30,"unit":"seconds"},
                           "to":{"snapshotId":"score:1","start":480,"end":1440},"origin":{"kind":"user"}}]}
        self.reference={"schema":2,"tracks":[{"id":"voice","name":"人声","path":"E:/audio/voice.wav", "identity":{"hash":"file-1"},
            "associations":[{"id":"near","start":480,"end":1440,"from":20000,"until":30000,"anchors":[{"tick":960,"ms":24500}]},
                            {"id":"away","start":4800,"end":5760,"from":20000,"until":30000}]}]}
    async def send_command(self,action,params=None):
        params=params or {};self.calls.append((action,copy.deepcopy(params)))
        scope=params.get("scope",SCOPE)
        if action=="arrangementState":
            return {"snapshotId":self.revision,"scoreSessionId":self.session,"playbackRevision":self.playback,"ticksPerQuarter":480,
                "scope":scope,"capabilities":{"renderedPerformance":True},"parts":[{"id":0,"name":"主钢琴"}],
                "information":copy.deepcopy(self.information),"reference":copy.deepcopy(self.reference)}
        if action=="arrangementRange":
            if self.page_changed:self.information["assertions"][0]["value"]="低声部保留主题"
            return {"snapshotId":self.revision,"notes":[{"id":"480:4:0","tick":480,"duration":480,"track":4,"index":0,
                "pitch":48,"writtenPitch":48,"writtenTpc":14,"quarterDuration":{"numerator":1,"denominator":1},"measure":2,
                "velocityType":0,"velocityRaw":0,"logicalId":"480:4:0"}],
                "meters":[{"tick":480,"end":2400,"measure":2}],"keys":[{"tick":480,"track":4,"key":-2}],
                "staves":[{"index":1,"name":"主钢琴 · 2","partId":0}],"done":True,"nextTick":scope["end"]}
        if action=="arrangementPlaybackPrepare":
            return {"snapshotId":self.revision,"playbackRevision":self.playback,"ready":True,
                    "ranges":[{"start":480,"end":1440,"occurrence":1},{"start":2880,"end":3840,"occurrence":2}]}
        if action=="arrangementPlaybackPage":
            rows=[]
            for offset,occ in [(0,1),(2400,2)]:
                for kind,tick in [("on",480),("off",950)]:
                    rows.append({"kind":kind,"ref":{"snapshotId":self.revision,"id":"480:4:0"},"logicalId":"480:4:0",
                        "utick":tick+offset,"nominalTick":480+offset,"occurrence":occ,"partId":0,"channel":0,"velocity":91 if kind=="on" else 0})
                rows.append({"kind":"pedal","value":127,"nominalTick":offset,"utick":offset,"partId":0,"channel":0})
            return {"snapshotId":self.revision,"playbackRevision":self.playback,"events":rows,"done":True,"nextTick":4800}
        return {"ok":True}

def run(fn):return asyncio.run(fn())

def test_analysis_keeps_real_names_keys_sources_and_scoped_audio():
    async def check():
        native=Native();original=copy.deepcopy(native.reference);service=ContextService(native)
        value=await service.capture()
        assert value["scoreSnapshot"]["keys"][0]["key"]==-2
        assert value["scoreSnapshot"]["staves"][0]["name"]=="主钢琴 · 2"
        assert [x["id"] for x in value["information"]["assertions"]]==["near"]
        track=value["reference"]["tracks"][0]
        assert [x["id"] for x in track["associations"]]==["near"]
        assert track["associations"][0]["anchors"]==[{"tick":960,"ms":24500}]
        assert value["information"]["assertions"][0]["origin"]=={"kind":"user"}
        assert native.reference==original
        assert not any("Playback" in name for name,_ in native.calls)
        assert value["coverage"]["performance"]=="notRequested"
    run(check)

def test_engraving_requests_geometry_without_rendering_sound():
    async def check():
        native=Native();value=await ContextService(native).capture({"purpose":"engraving"})
        assert value["fieldsRead"]==["geometry"]
        assert next(args for name,args in native.calls if name=="arrangementRange")["fields"]==["geometry"]
        assert not any("Playback" in name for name,_ in native.calls)
    run(check)

def test_performance_preserves_repeated_notes_and_initial_pedal():
    async def check():
        native=Native();value=await ContextService(native).capture({"purpose":"performance"})
        rows=value["performance"]["events"]
        assert len([x for x in rows if x["kind"]=="on"])==2
        assert [x["velocity"] for x in rows if x["kind"]=="on"]==[91,91]
        assert {x["occurrence"] for x in rows if x["kind"]=="on"}=={1,2}
        assert len([x for x in rows if x.get("contextOnly")])==2
        assert value["coverage"]["performance"]=="renderedNotesAndSustain"
    run(check)

def test_mixer_change_during_read_keeps_previous_context():
    class Changing(Native):
        async def send_command(self,action,params=None):
            result=await super().send_command(action,params)
            if action=="arrangementPlaybackPage":self.playback="play:2"
            return result
    async def check():
        service=ContextService(Changing());old=await service.capture()
        with pytest.raises(ContextError,match="演奏设置"):
            await service.capture({"purpose":"performance"})
        assert list(service.contexts)==[old["contextId"]]
    run(check)

def test_refresh_retains_range_and_goal_while_selection_and_music_change():
    async def check():
        native=Native();service=ContextService(native)
        old=await service.capture({"taskBrief":{"goal":"左手稀疏","preserveTracks":[0]}})
        native.revision="score:2";native.calls.clear()
        new=await service.refresh(old["contextId"],{"style":"流行"})
        assert new["snapshotId"]=="score:2" and new["scope"]==old["scope"]
        assert new["taskBrief"]=={"goal":"左手稀疏","preserveTracks":[0],"style":"流行"}
        assert service.context_result(new["contextId"])["previousContextId"]==old["contextId"]
        assert all(args["scope"]==SCOPE for name,args in native.calls if name=="arrangementRange")
    run(check)

def test_refresh_on_another_score_does_not_read_its_notes():
    async def check():
        native=Native();service=ContextService(native);old=await service.capture()
        native.session="another";native.revision="another:1";native.calls.clear()
        with pytest.raises(ContextError,match="另一份"):
            await service.refresh(old["contextId"])
        assert [name for name,_ in native.calls]==["arrangementState"]
    run(check)

def test_information_updated_during_read_uses_final_source_data():
    async def check():
        native=Native();service=ContextService(native);old=await service.capture();native.page_changed=True
        now=await service.capture()
        assert now["information"]["assertions"][0]["value"]=="低声部保留主题"
        assert now["informationRevision"]!=old["informationRevision"]
    run(check)

def test_missing_materials_are_reported_for_this_range():
    async def check():
        native=Native();native.information={};native.reference={}
        result=await ContextService(native).capture()
        assert result["optionalCoverage"]["referenceMaterials"]["availability"]=="notProvided"
        assert result["read"]["notes"]==1
    run(check)

def test_audio_seconds_are_not_treated_as_score_ticks():
    assert overlaps({"start":20,"end":30,"unit":"seconds"},SCOPE)
    assert overlaps({"materialId":"audio","start":20,"end":30},SCOPE)
    assert overlaps({"start":"verse","end":"chorus"},SCOPE)
    assert not overlaps({"start":2400,"end":2880},SCOPE)

def test_legacy_data_uses_notated_pitch_and_omits_context_only_attacks():
    async def check():
        value=await ContextService(Native()).capture()
        row=value["scoreSnapshot"]["notes"][0];row.update(notatedPitch=50,notatedTpc=16)
        context=copy.deepcopy(row);context.update(id="0:4:0",tick=0,measure=1,contextOnly=True)
        value["scoreSnapshot"]["notes"].append(context)
        result=score_data_projection(value)
        assert result["staves"][1]["name"]=="主钢琴 · 2"
        notes=result["measures"][0]["elements"]["staff1"][0]["notes"]
        assert len(notes)==1 and notes[0]["pitchMidi"]==50 and notes[0]["tpc"]==16
    run(check)

def test_invalid_purpose_has_a_direct_explanation():
    with pytest.raises(ValueError,match="分析、演奏或净谱"):
        read_request({"purpose":"audioGuess"})

def test_refresh_keeps_track_protection_and_flags_a_changed_explicit_note():
    class Changed(Native):
        pitch=48
        async def send_command(self,action,params=None):
            result=await super().send_command(action,params)
            if action=="arrangementRange":result["notes"][0]["writtenPitch"]=self.pitch
            return result
    async def check():
        native=Changed();service=ContextService(native)
        old=await service.capture({"taskBrief":{"preserveTracks":[0],"preserveNotes":["480:4:0"]}})
        native.revision="score:2";native.pitch=50
        new=await service.refresh(old["contextId"])
        assert new["taskBrief"]["preserveTracks"]==[0]
        assert new["taskContinuity"]["changedProtectedNotes"]==["480:4:0"]
        with pytest.raises(ContextError,match="保留的音"):
            await service.submit_options(new["contextId"],[{"title":"A"}])
    run(check)

def test_shared_harmony_keeps_source_state_and_only_relevant_regions():
    class Harmony(Native):
        async def send_command(self,action,params=None):
            value=await super().send_command(action,params)
            if action=="arrangementState":
                value["manualHarmony"]={"overrides":[{"start":480,"end":960,"part":0,"symbol":"Cm"},{"start":4800,"end":5760,"part":0,"symbol":"F"}],"positions":[{"start":480,"end":960}]}
                value["harmonyAnalysis"]={"availability":"notProvided","processing":"notRequested","freshness":"unknown"}
            return value
    async def check():
        value=await ContextService(Harmony()).capture()
        assert len(value["manualHarmony"]["overrides"])==1
        assert "positions" not in value["manualHarmony"]
        assert value["optionalCoverage"]["sharedHarmony"]["processing"]=="notRequested"
    run(check)
