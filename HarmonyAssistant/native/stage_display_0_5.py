# -*- coding: utf-8 -*-
"""Prepare review copies inside the plugin workspace; never changes native checkout."""
from pathlib import Path
import shutil
here=Path(__file__).resolve().parent
source=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
stage=here.parent/'tests/staged-native-0.5'
names=['mscore/plugin/qmlplugin.h','mscore/plugin/qmlplugin.cpp',
       'mscore/plugin/api/scoreobserver.cpp','mscore/scoreview.h','mscore/scoreview.cpp',
       'mtest/mscore/pluginhost/tst_pluginhost.cpp']
for name in names:
    target=stage/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(str(source/name),str(target))
for name in ['test_annotation_overlap_0_4_1.py','extend_display_0_5.py','test_display_0_5.py']:
    script=(here/name).read_text(encoding='utf-8')
    if name=='test_annotation_overlap_0_4_1.py':
        script=script.replace("p=Path(r'E:\\programming\\funcodes\\muse3_dev\\MuseScore\\mtest\\mscore\\pluginhost\\tst_pluginhost.cpp')",'p=stage/"mtest/mscore/pluginhost/tst_pluginhost.cpp"')
    else:
        script=script.replace("repo=Path(r'E:\\programming\\funcodes\\muse3_dev\\MuseScore')",'repo=stage')
        script=script.replace('here=Path(__file__).resolve().parent','here=script_directory')
    exec(compile(script,name,'exec'),{'stage':stage,'script_directory':here,'__file__':str(here/name)})
print('Review source copies ready:',stage)
