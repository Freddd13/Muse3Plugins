# coding: utf-8
"""Check the maintained regional module; source mirrors are authoritative."""
from pathlib import Path
root=Path(__file__).resolve().parent/'native'
required={
 'libmscore/regionalvariants.cpp':['validateFragment(', 'QVariantMap expand(', 'bool exportOrdinary(', 'clearAfterLoad()'],
 'libmscore/scorefile.cpp':['RegionalVariants::save(', 'RegionalVariants::restore(', 'QSaveFile'],
 'mscore/workflow/regionalpanel.cpp':['void selectTree(', 'void showRegionalVariantPanel(', 'void ordinary()', 'void importLegacy()']
}
for name,tokens in required.items():
 text=(root/name).read_text(encoding='utf8')
 for token in tokens:
  if token not in text:raise RuntimeError(name+': missing '+token)
print('分段方案源码、保存接口和面板入口齐全。')
