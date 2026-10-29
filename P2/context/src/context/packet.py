"""Task-sized projections of score information; original entries keep their sources."""
from __future__ import annotations

from bisect import bisect_right
import copy
import hashlib
import json

PURPOSE_FIELDS = {"analysis": set(), "performance": {"performance"}, "engraving": {"geometry"}}


def read_request(request):
    result = copy.deepcopy(request or {})
    purpose = result.get("purpose", "analysis")
    if purpose not in PURPOSE_FIELDS:
        raise ValueError("请选择分析、演奏或净谱用途。")
    fields = set(result.get("fields", [])) | PURPOSE_FIELDS[purpose]
    if not fields <= {"geometry", "performance"}:
        raise ValueError("可读取谱面位置和实际演奏；其它资料随选段一起提供。")
    result["purpose"], result["fields"] = purpose, sorted(fields)
    return result


def overlaps(target, scope):
    """Keep entries without a precise score target; their coverage stays explicit."""
    if not isinstance(target, dict):
        return True
    target = target.get("scope", target)
    if not isinstance(target, dict) or target.get("materialId"):
        return True
    if target.get("unit", target.get("timeUnit", "ticks")) not in {"tick", "ticks", "scoreTicks", "nativeTicks"}:
        return True
    if "start" in target and "end" in target:
        if not all(isinstance(target[key], (int, float)) for key in ("start", "end")):
            return True
        if target["end"] <= scope["start"] or target["start"] >= scope["end"]:
            return False
        return (target.get("endTrack", scope["endTrack"]) > scope["firstTrack"]
                and target.get("firstTrack", scope["firstTrack"]) < scope["endTrack"])
    measures = target.get("measures")
    if measures and isinstance(measures, list) and len(measures) == 2:
        return (measures[1] >= scope.get("firstMeasure", measures[0])
                and measures[0] <= scope.get("lastMeasure", measures[1]))
    if "measure" in target:
        return scope.get("firstMeasure", target["measure"]) <= target["measure"] <= scope.get("lastMeasure", target["measure"])
    if "tick" in target:
        return scope["start"] <= target["tick"] < scope["end"]
    return True


def score_target(row):
    for name in ("target", "scope", "from", "to"):
        target = row.get(name)
        if isinstance(target, dict) and not target.get("materialId"):
            return target
    return {}


def packet_information(state, scope):
    information = copy.deepcopy(state.get("information", {}))
    for name in ("assertions", "alignments", "analysisRuns", "adoptions"):
        if name in information:
            information[name] = [row for row in information[name]
                if overlaps(score_target(row), scope)]
    material_ids = set()
    for row in information.get("alignments", []):
        for side in ("from", "to"):
            value = row.get(side, {})
            if isinstance(value, dict) and value.get("materialId"):
                material_ids.add(value["materialId"])
    if "materials" in information:
        information["materials"] = [row for row in information["materials"]
            if row.get("id") in material_ids or overlaps(row.get("coverage", row.get("target", {})), scope)]
    reference = copy.deepcopy(state.get("reference", {}))
    tracks = []
    for row in reference.get("tracks", []):
        associations = [entry for entry in row.get("associations", []) if overlaps(entry, scope)]
        if associations:
            row["associations"] = associations
            tracks.append(row)
    if "tracks" in reference:
        reference["tracks"] = tracks
    return information, reference


def layer_status(rows, scope, absent="notProvided", freshness="unknown"):
    return {"availability": "available" if rows else absent,
            "coverage": {"scope": copy.deepcopy(scope), "extent": "partial" if rows else "unknown"},
            "processing": "ready", "freshness": freshness}


def enrich_context(result):
    scope = result["scope"]
    information, reference = packet_information(result, scope)
    result["information"], result["reference"] = information, reference
    parts = {row.get("id", row.get("firstTrack")) for row in result.get("parts", [])}
    def local(row):
        return overlaps(row, scope) and (not parts or "part" not in row or row["part"] in parts)
    for name, collections in (("manualHarmony", ("overrides", "positions")), ("harmonyAnalysis", ("regions", "intervals"))):
        if name not in result: continue
        value = copy.deepcopy(result[name])
        for collection in collections:
            if collection in value:
                value[collection] = [row for row in value[collection] if local(row)]
        if name=="manualHarmony" and result.get("purpose")!="engraving":
            value.pop("positions",None)
        result[name] = value
    result["informationRevision"] = hashlib.sha256(json.dumps(
        {"information": information, "reference": reference,
         "manualHarmony": result.get("manualHarmony"), "harmonyAnalysis": result.get("harmonyAnalysis")},
        sort_keys=True, ensure_ascii=False).encode("utf8")).hexdigest()
    optional = {
        "userInterpretation": layer_status(information.get("assertions"), scope),
        "referenceMaterials": layer_status(information.get("materials"), scope),
        "audioAssociations": layer_status(reference.get("tracks"), scope),
        "providedAlignments": layer_status(information.get("alignments"), scope),
    }
    harmony = result.get("harmonyAnalysis", {})
    optional["sharedHarmony"] = layer_status(harmony.get("regions") or harmony.get("intervals"), scope,
        freshness=harmony.get("freshness", "unknown"))
    for field in ("availability", "processing"):
        if field in harmony: optional["sharedHarmony"][field]=harmony[field]
    result["optionalCoverage"] = optional
    result["sources"] = {"notation": {"origin": "nativeNotation", "snapshotId": result["snapshotId"]},
                         "interpretation": {"collections": ["information.assertions", "manualHarmony", "harmonyAnalysis"],
                                            "revision": result["informationRevision"]},
                         "references": {"collections": ["information.materials", "information.alignments", "reference.tracks"],
                                        "audioTimeUnit": "milliseconds"}}
    result["sources"]["notation"]["timing"] = "Written score positions; rendered attacks and releases are in performance.events."
    return result


def rendered_performance(events, controls, ranges, snapshot):
    """Select native note events and the sustain state entering each occurrence."""
    ids = {row.get("ref", {}).get("id", row["id"]) for row in snapshot["notes"]}
    logical = {row.get("logicalId", row["id"]) for row in snapshot["notes"]}
    notes = [row for row in events if row.get("ref", {}).get("id") in ids or row.get("logicalId") in logical]
    ranges = sorted(ranges, key=lambda row: row["start"])
    starts = [row["start"] for row in ranges]
    grouped = {}
    selected = []
    for row in controls:
        tick = row["nominalTick"]
        grouped.setdefault((row["partId"], row["channel"]), []).append(row)
        i = bisect_right(starts, tick) - 1
        if i >= 0 and tick < ranges[i]["end"]:
            selected.append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: row["nominalTick"])
        ticks = [row["nominalTick"] for row in rows]
        for span in ranges:
            i = bisect_right(ticks, span["start"] - 1) - 1
            if i >= 0:
                selected.append({**rows[i], "contextOnly": True,
                                 "contextForStart": span["start"], "contextForOccurrence": span["occurrence"]})
    return sorted(notes + selected, key=lambda row: (row["utick"], row.get("contextForStart", -1)))
