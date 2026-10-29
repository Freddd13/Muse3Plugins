from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest

module_path = Path(__file__).parent / 'native/personal/tools/package_user_guide.py'
spec = importlib.util.spec_from_file_location('package_user_guide', module_path)
guide = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guide
spec.loader.exec_module(guide)


class PackagedGuideTests(unittest.TestCase):
    def test_local_guide_and_source_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, installed = root / 'source', root / 'program'
            (source / 'personal/docs').mkdir(parents=True)
            (source / 'libmscore').mkdir()
            (source / 'libmscore/note.cpp').write_text('code', encoding='utf8')
            text = '[操作](docs/help.md#example)\n[源码](../libmscore/note.cpp)\n```md\n[例子](missing.md)\n```\n'
            (source / 'personal/USER_GUIDE.md').write_text(text, encoding='utf8')
            (source / 'personal/docs/help.md').write_text('![图](image.png)\n[首页](../USER_GUIDE.md)', encoding='utf8')
            (source / 'personal/docs/image.png').write_bytes(b'image')
            repository = guide.Repository(source, 'https://example.org/project', 'revision', {'libmscore/note.cpp'})
            result = guide.export_guide(source, installed, [repository])
            self.assertEqual(result['documents'], 2)
            self.assertFalse(result['unresolved'])
            self.assertFalse(guide.check_export(installed)['broken'])
            self.assertEqual((installed / 'personal/docs/image.png').read_bytes(), b'image')
            output = (installed / 'personal/USER_GUIDE.md').read_text('utf8')
            self.assertIn('[操作](docs/help.md#example)', output)
            self.assertIn('https://example.org/project/blob/revision/libmscore/note.cpp', output)
            self.assertIn('[例子](missing.md)', output)
            self.assertEqual((source / 'personal/USER_GUIDE.md').read_text('utf8'), text)
            nested = source / 'install'
            guide.export_guide(source, nested, [repository])
            self.assertFalse(guide.check_export(nested)['broken'])
            self.assertEqual((source / 'personal/USER_GUIDE.md').read_text('utf8'), text)

    def test_cross_repository_and_unpublished_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, other, installed = root / 'source', root / 'materials', root / 'program'
            (source / 'personal').mkdir(parents=True)
            other.mkdir()
            (other / '音符.md').write_text('reference', encoding='utf8')
            (other / 'private.md').write_text('unpublished', encoding='utf8')
            (source / 'personal/USER_GUIDE.md').write_text('[资料](../../materials/音符.md)\n[未发布](../../materials/private.md)', encoding='utf8')
            repository = guide.Repository(other, 'https://example.org/materials', 'revision', {'音符.md'})
            result = guide.export_guide(source, installed, [repository])
            self.assertEqual(len(result['updated_links']), 1)
            self.assertEqual(len(result['unresolved']), 1)
            self.assertEqual(len(guide.check_export(installed)['broken']), 1)
            self.assertIn('%E9%9F%B3%E7%AC%A6.md', result['updated_links'][0]['url'])
            with self.assertRaises(ValueError):
                guide.export_guide(source, source, [repository])


if __name__ == '__main__':
    unittest.main()
