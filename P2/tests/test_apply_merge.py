import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('apply_batch', Path(__file__).resolve().parents[1] / 'apply.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


class GuideMerge(unittest.TestCase):
    def test_independent_appended_chapter_is_preserved(self):
        base = b'# Guide\n\nCurrent steps.\n'
        result = batch.merge_guide(base.replace(b'Current', b'Updated'), base, base + b'\n## Fonts\nUser notes.\n')
        self.assertIn(b'Updated steps', result)
        self.assertIn(b'User notes', result)

    def test_unchanged_copy_keeps_newer_guide(self):
        self.assertEqual(batch.merge_guide(b'old\n', b'old\n', b'new\n'), b'new\n')

    def test_overlapping_change_is_reported(self):
        with self.assertRaises(RuntimeError):
            batch.merge_guide(b'ours\n', b'base\n', b'theirs\n')


if __name__ == '__main__':
    unittest.main()
