"""Check that packaging selects the verified component and retains other DLLs."""
from pathlib import Path
import hashlib
import json
import subprocess
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
CMAKE = Path('C:/Program Files/CMake/bin/cmake.exe')
HELPER = ROOT / 'native/personal/qtquick-runtime.cmake'


class RuntimeSelection(unittest.TestCase):
    def prepare(self, patch=True, checksum=True, sdk_checksum=True, version='5.15.2'):
        folder = ROOT / 'out' / ('runtime-127-' + uuid.uuid4().hex[:12])
        sdk, fixed = folder / 'sdk', folder / 'fixed with spaces'
        sdk.mkdir(parents=True)
        fixed.mkdir()
        old, other = sdk / 'Qt5Quick.dll', sdk / 'Qt5Gui.dll'
        old.write_bytes(b'original Quick')
        other.write_bytes(b'original Gui')
        if patch:
            new = fixed / 'Qt5Quick.dll'
            new.write_bytes(b'patched Quick')
            (fixed / 'Qt5Quick.sha256').write_text(hashlib.sha256(new.read_bytes()).hexdigest() if checksum else 'bad')
            (fixed / 'Qt5Quick.original.sha256').write_text(hashlib.sha256(old.read_bytes()).hexdigest() if sdk_checksum else 'bad')
            (fixed / 'Qt5Quick.fix.json').write_text(json.dumps({'fixCommit': 'QTBUG-80415'}))
        project = f'''cmake_minimum_required(VERSION 3.16)
project(RuntimeSelection NONE)
set(Qt5Core_VERSION "{version}")
set(KUMO_QTQUICK_PATCH_DIR "{fixed.as_posix()}" CACHE PATH "")
include("{HELPER.as_posix()}")
set(runtime "{old.as_posix()}" "{other.as_posix()}")
kumo_select_qtquick_runtime(runtime)
file(WRITE "${{CMAKE_BINARY_DIR}}/selected.txt" "${{runtime}}")
install(FILES ${{runtime}} DESTINATION bin)
'''
        (folder / 'CMakeLists.txt').write_text(project)
        result = subprocess.run([str(CMAKE), '-S', str(folder), '-B', str(folder / 'build')], capture_output=True, text=True)
        return folder, result

    def test_installed_files(self):
        folder, result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        chosen = (folder / 'build/selected.txt').read_text().split(';')
        self.assertEqual(chosen, [(folder / 'fixed with spaces/Qt5Quick.dll').as_posix(), (folder / 'sdk/Qt5Gui.dll').as_posix()])
        output = folder / 'installed'
        subprocess.run([str(CMAKE), '--install', str(folder / 'build'), '--prefix', str(output)], check=True, capture_output=True)
        self.assertEqual((output / 'bin/Qt5Quick.dll').read_bytes(), b'patched Quick')
        self.assertEqual((output / 'bin/Qt5Gui.dll').read_bytes(), b'original Gui')
        self.assertTrue((output / 'personal/thirdparty/qtquick/Qt5Quick.fix.json').is_file())

    def test_without_patch(self):
        folder, result = self.prepare(patch=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((folder / 'build/selected.txt').read_text().split(';')[0], (folder / 'sdk/Qt5Quick.dll').as_posix())

    def test_changed_component(self):
        _, result = self.prepare(checksum=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('checksum differs', result.stderr)

    def test_another_sdk_build(self):
        _, result = self.prepare(sdk_checksum=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('another SDK build', result.stderr)

    def test_another_qt_version(self):
        _, result = self.prepare(version='5.15.3')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('for Qt 5.15.2', result.stderr)


if __name__ == '__main__':
    unittest.main()
