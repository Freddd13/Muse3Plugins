import asyncio
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from context.service import ContextError, ContextService, quarter_time


class Score:
    def __init__(self):
        self.calls = []
        self.revision = "session:1"
        self.change_after_page = False
        self.block = None

    async def send_command(self, action, params=None):
        params = params or {}
        self.calls.append((action, copy.deepcopy(params)))
        if action == "arrangementState":
            return {"status": "success", "result": {
                "snapshotId": self.revision, "ticksPerQuarter": 480,
                "scope": params.get("scope", {"start": 0, "end": 960, "firstTrack": 0, "endTrack": 8}),
                "scoreSessionId": "session",
            }}
        if action == "arrangementRange":
            if self.block is not None:
                await self.block.wait()
            if params["snapshotId"] != self.revision:
                return {"error": "乐谱已经更新，请重新读取。"}
            tick = params["fromTick"]
            result = {"snapshotId": self.revision,
                      "notes": [{"id": f"{tick}:0:0", "tick": tick, "duration": 480,
                                 "track": 0, "pitch": 60}],
                      "meters": [{"tick": 0, "measure": 1}],
                      "nextTick": tick + 480, "done": tick >= 480}
            if self.change_after_page:
                self.revision = "session:2"
            return {"status": "success", "result": result}
        return {"status": "success", "result": {"ok": True}}


class ServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_host_pages_keep_version_and_exact_range(self):
        score = Score()
        service = ContextService(score)
        result = await service.capture({"taskBrief": {"goal": "伴奏更轻"}})
        self.assertEqual(result["read"], {"pages": 2, "notes": 2, "status": "ready"})
        notes = result["scoreSnapshot"]["notes"]
        self.assertEqual([n["tick"] for n in notes], [0, 480])
        self.assertEqual(notes[1]["quarterTime"], {"numerator": 1, "denominator": 1})
        self.assertEqual(notes[0]["ref"], {"snapshotId": "session:1", "id": "0:0:0"})
        self.assertEqual(len(result["scoreSnapshot"]["meters"]), 1)
        self.assertTrue(all(p["scope"]["end"] == 960 for name, p in score.calls if name == "arrangementRange"))
        notes[0]["pitch"] = 99
        self.assertEqual(service.contexts[result["contextId"]]["scoreSnapshot"]["notes"][0]["pitch"], 60)

    async def test_playback_reuses_matching_read_and_requests_pause_for_new_fields(self):
        class Playing(Score):
            playing = False
            async def send_command(self, action, params=None):
                value = await super().send_command(action, params)
                if action == "arrangementState":
                    value["result"]["playing"] = self.playing
                return value
        score = Playing()
        service = ContextService(score)
        original = await service.capture()
        score.playing = True
        score.calls.clear()
        cached = await service.capture()
        self.assertEqual(cached["read"]["pages"], 0)
        self.assertEqual(cached["scoreSnapshot"], original["scoreSnapshot"])
        self.assertFalse(any(name == "arrangementRange" for name, _ in score.calls))
        with self.assertRaises(ContextError):
            await service.capture({"fields": ["geometry"]})

    async def test_edit_during_read_discards_partial_context(self):
        score = Score()
        score.change_after_page = True
        service = ContextService(score)
        with self.assertRaises(ContextError):
            await service.capture()
        self.assertEqual(service.contexts, {})

    async def test_cancel_finishes_task_and_keeps_other_results(self):
        score = Score()
        service = ContextService(score)
        context = await service.capture()
        score.block = asyncio.Event()
        started = service.start_capture()
        await asyncio.sleep(0)
        service.task_state(started["taskId"], cancel=True)
        await asyncio.sleep(0)
        self.assertEqual(service.task_state(started["taskId"])["status"], "cancelled")
        self.assertIn(context["contextId"], service.contexts)

    async def test_options_need_context_and_keep_three_choices(self):
        service = ContextService(Score())
        with self.assertRaises(ContextError):
            await service.submit_options("missing", [{"title": "A"}])
        await service.capture()
        with self.assertRaises(ContextError):
            await service.submit_options("session:1", [{}] * 4)
        result = await service.submit_options("session:1", [{"title": "A", "summary": "左手低音提前松开"}])
        self.assertTrue(result["ok"])

    def test_musical_quarter_units_reduce_exactly(self):
        self.assertEqual(quarter_time(160, 480), {"numerator": 1, "denominator": 3})
        self.assertEqual(quarter_time(0, 480), {"numerator": 0, "denominator": 1})

    async def test_exact_tuplet_time_survives_integer_tick_projection(self):
        class TupletScore(Score):
            async def send_command(self, action, params=None):
                value = await super().send_command(action, params)
                if action == "arrangementRange":
                    value["result"]["notes"][0]["quarterDuration"] = {"numerator": 1, "denominator": 7}
                return value
        result = await ContextService(TupletScore()).capture()
        self.assertEqual(result["scoreSnapshot"]["notes"][0]["quarterDuration"], {"numerator": 1, "denominator": 7})

    async def test_lost_write_response_retains_operation_for_result_lookup(self):
        class Lost(Score):
            async def send_command(self, action, params=None):
                if action == "storeArrangementInfo":
                    self.operation = params["operationId"]
                    return {"error": "connection closed", "outcomeUnknown": True}
                if action == "arrangementOperationStatus":
                    return {"ok": True, "operationId": params["operationId"]}
                return await super().send_command(action, params)
        score = Lost()
        service = ContextService(score)
        outcome = await service.store_information("session:1", {"materials": []})
        self.assertTrue(outcome["outcomeUnknown"])
        self.assertEqual(outcome["operationId"], score.operation)
        self.assertEqual((await service.operation_status(score.operation))["operationId"], score.operation)

    async def test_unexpected_failure_finishes_task(self):
        class Broken(Score):
            async def send_command(self, action, params=None):
                raise RuntimeError("backend stopped")
        service = ContextService(Broken())
        with self.assertLogs("MuseScoreMCP.Context", "ERROR"):
            task = service.start_capture()
            await asyncio.sleep(0)
        self.assertEqual(service.task_state(task["taskId"])["status"], "failed")

    async def test_two_tasks_on_one_version_keep_their_scope_and_requirements(self):
        score = Score()
        service = ContextService(score)
        first = await service.capture({"taskBrief": {"goal": "保留旋律"}})
        second = await service.capture({"scope": {"start": 0, "end": 480, "firstTrack": 0, "endTrack": 4},
                                        "taskBrief": {"goal": "另一段"}})
        self.assertEqual(first["snapshotId"], second["snapshotId"])
        self.assertNotEqual(first["contextId"], second["contextId"])
        await service.capture(retain=False)
        self.assertEqual(len(service.contexts), 2)
        await service.submit_options(first["contextId"], [{"title": "A"}])
        action, request = score.calls[-1]
        self.assertEqual(action, "submitArrangementOptions")
        self.assertEqual(request["options"][0]["scope"]["end"], 960)
        self.assertEqual(request["taskBrief"]["goal"], "保留旋律")
        with self.assertRaises(ContextError):
            service.context_result(first["snapshotId"])
        with self.assertRaises(ContextError):
            await service.submit_options(second["contextId"], [{"scope": first["scope"]}])


if __name__ == "__main__":
    unittest.main()
