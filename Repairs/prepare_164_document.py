from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];N=ROOT/'P2/native'
file=N/'mscore/CMakeLists.txt';text=file.read_text('utf8')
if 'scorevideo/scorevideo.cpp' not in text:
    text=text.replace('      seq.cpp workflow/referencebus.cpp','      scorevideo/scorevideo.cpp scorevideo/scorevideo.h scorevideo/scorevideoframe.cpp scorevideo/scorevideotimeline.cpp\n      seq.cpp workflow/referencebus.cpp',1);file.write_text(text,encoding='utf8',newline='\n')
file=N/'mtest/mscore/pluginhost/tst_pluginhost.cpp';text=file.read_text('utf8')
if 'void scoreVideoPictures164();' not in text:
    text=text.replace('      void velocityPeekHold159();','      void scoreVideoPictures164_data();\n      void scoreVideoPictures164();\n      void scoreVideoTimeAndStorage164();\n      void velocityPeekHold159();',1)
    text=text.replace('#include "reference_163_tests.inc"','#include "reference_163_tests.inc"\n#include "scorevideo_164_tests.inc"',1)
    file.write_text(text,encoding='utf8',newline='\n')
