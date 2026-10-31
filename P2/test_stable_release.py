"""A new program folder must stay complete without copying obsolete MCP copies."""
from pathlib import Path
import json
import tempfile
import unittest
import zipfile

from package_stable_release import archive_program, digest, stage_program, write_manifest


class StableReleaseTests(unittest.TestCase):
    def source(self, root):
        source = root / "原安装"
        contents = {"bin/MuseScore3Evo.exe": b"old application", "bin/kumo.ini": b"[features]\nenable_exp_feature=true\n",
                    "bin/tools/mcp/current.json": b'{"directory":"2.7.2"}',
                    "bin/tools/mcp/2.7.2/MuseScoreMCP.exe": b"active MCP",
                    "bin/tools/mcp/2.7.2/_internal/dependency.dll": b"runtime dependency",
                    "bin/tools/mcp/2.7.1/MuseScoreMCP.exe": b"old MCP",
                    "bin/tools/mcp/MuseScoreMCP.exe": b"legacy MCP",
                    "bin/tools/mcp/licenses/LICENSE": b"license",
                    "personal/tools/build.py": b"developer tool", "qml/Controls/qmldir": b"QML dependency",
                    "plugins/User.qml": b"user plugin", "personal/VERSION": b"0.155.0\n"}
        for relative, raw in contents.items():
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        program = root / "program.exe"
        program.write_bytes(b"0.156.0 Kumo branch / Freddd13 new application")
        return source, program, contents

    def test_selected_runtime_resources_and_original_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, program, original = self.source(root)
            package = root / "稳定 程序"
            result = stage_program(source, program, package, "0.156.0")
            self.assertEqual(result["mcpVersion"], "2.7.2")
            for relative in ["bin/kumo.ini", "bin/tools/mcp/current.json", "bin/tools/mcp/2.7.2/_internal/dependency.dll", "qml/Controls/qmldir", "plugins/User.qml", "bin/tools/mcp/licenses/LICENSE"]:
                self.assertEqual((package / relative).read_bytes(), original[relative])
            self.assertFalse((package / "bin/tools/mcp/2.7.1").exists())
            self.assertFalse((package / "bin/tools/mcp/MuseScoreMCP.exe").exists())
            self.assertEqual((package / "bin/MuseScore3Evo.exe").read_bytes(), program.read_bytes())
            for relative, raw in original.items():
                self.assertEqual((source / relative).read_bytes(), raw)
            with self.assertRaises(ValueError):
                stage_program(source, program, package, "0.156.0")
            with self.assertRaises(ValueError):
                stage_program(source, program, source / "nested", "0.156.0")

    def test_archive_contents_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, program, _ = self.source(root)
            package = root / "稳定程序"
            result = stage_program(source, program, package, "0.156.0")
            manifest = write_manifest(package, result)
            archive = root / "program.zip"
            result = archive_program(package, archive)
            self.assertEqual(result["sha256"], digest(archive))
            with zipfile.ZipFile(archive) as zipped:
                self.assertEqual(len(zipped.namelist()), len(manifest["files"]) + 1)
                self.assertEqual(json.loads(zipped.read("稳定程序/release-manifest.json"))["version"], "0.156.0")
            with self.assertRaises(ValueError):
                archive_program(package, archive)

    def test_invalid_runtime_and_wrong_program_do_not_create_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, program, _ = self.source(root)
            target = root / "program"
            program.write_bytes(b"0.155.0 Kumo branch Freddd13")
            with self.assertRaises(ValueError):
                stage_program(source, program, target, "0.156.0")
            self.assertFalse(target.exists())
            program.write_bytes(b"0.156.0 Kumo branch Freddd13")
            (source / "bin/tools/mcp/current.json").write_text('{"directory":"../2.7.2"}', encoding="utf8")
            with self.assertRaises(ValueError):
                stage_program(source, program, target, "0.156.0")
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
