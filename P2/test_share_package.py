"""Sharing keeps the original program and every unrelated setting intact."""
from pathlib import Path
import configparser
import tempfile
import unittest

from make_share_package import disable_personal_features, make_share_package


class SharePackageTests(unittest.TestCase):
    def test_only_switch_changes_in_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "中文 原程序"
            (source / "bin").mkdir(parents=True)
            (source / "bin/MuseScore3Evo.exe").write_bytes(b"program")
            configuration = b"; personal settings\r\n[features]\r\nenable_exp_feature=true\r\nother=true\r\n[media]\r\ncache=E:/cache\r\n"
            (source / "bin/kumo.ini").write_bytes(configuration)
            (source / "plugins").mkdir()
            (source / "plugins/My.qml").write_bytes(b"user plugin")
            target = root / "分享 程序"
            self.assertEqual(make_share_package(source, target), target / "bin/MuseScore3Evo.exe")
            self.assertEqual((source / "bin/kumo.ini").read_bytes(), configuration)
            self.assertEqual((target / "bin/kumo.ini").read_bytes(), configuration.replace(b"enable_exp_feature=true", b"enable_exp_feature=false"))
            self.assertEqual((target / "plugins/My.qml").read_bytes(), b"user plugin")
            with self.assertRaises(ValueError):
                make_share_package(source, target)
            with self.assertRaises(ValueError):
                make_share_package(source, source / "nested")

    def test_absent_key_and_sections(self):
        variants = ["", "[other]\nvalue=42\n", "[features]\nother=true\n", "[features]\nother=true\n[media]\nvalue=42\n", "\n; note\n[features]\nenable_exp_feature=true\n"]
        with tempfile.TemporaryDirectory() as directory:
            for i, value in enumerate(variants):
                with self.subTest(value=value):
                    path = Path(directory) / (str(i) + ".ini")
                    path.write_text(value, encoding="utf8")
                    disable_personal_features(path)
                    parsed = configparser.ConfigParser()
                    parsed.read(path, encoding="utf8")
                    self.assertFalse(parsed.getboolean("features", "enable_exp_feature"))
                    if "value=42" in value:
                        self.assertIn("value=42", path.read_text("utf8"))
                    if value.startswith("\n; note"):
                        self.assertTrue(path.read_text("utf8").startswith("\n; note"))

    def test_utf8_bom_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kumo.ini"
            disable_personal_features(path)
            self.assertEqual(path.read_text("utf8"), "[features]\nenable_exp_feature=false\n")
            path.write_bytes(b"\xef\xbb\xbf[features]\nENABLE_EXP_FEATURE=true\n")
            disable_personal_features(path)
            self.assertEqual(path.read_bytes(), b"\xef\xbb\xbf[features]\nenable_exp_feature=false\n")


if __name__ == "__main__":
    unittest.main()
