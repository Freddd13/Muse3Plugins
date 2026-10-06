# -*- coding: utf-8 -*-
"""Stage native changes in the plugin workspace; hash-guard later installation."""
from pathlib import Path
import hashlib,json
repo=Path(r'E:\programming\funcodes\muse3_dev\MuseScore')
stage=Path(__file__).resolve().parent/'next-1.4'
files=['mscore/notepreview.h','mscore/scoreview.cpp','mscore/events.cpp',
       'mscore/plugin/api/scoreobserver.h','mscore/plugin/api/scoreobserver.cpp']
manifest={}
for name in files:
    src=repo/name;dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists(),name
    data=src.read_bytes();dst.write_bytes(data);manifest[name]=hashlib.sha256(data).hexdigest()
(stage/'baseline.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
