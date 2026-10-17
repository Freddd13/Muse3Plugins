from pathlib import Path
import shutil
R=Path(__file__).resolve().parent/'native'
p=R/'libmscore/regionalvariants.h'
s=p.read_text(encoding='utf8').replace('QVariantMap chooseMain(','''QVariantMap selectMany(Score *, const QVariantMap &choices);
QVariantMap storeCombination(Score *, const QString &name);
QVariantMap selectCombination(Score *, const QString &combination);
MasterScore *comparison(Score *, const QString &group, const QString &variant, QString *error);
QVariantList differences(Score *, Score *, const QString &group);
QVariantMap chooseMain(''')
p.write_text(s,encoding='utf8',newline='\n')
p=R/'libmscore/regionalvariants.cpp';s=p.read_text(encoding='utf8');s=s.replace('} // namespace RegionalVariants','#include "regionalvarianttools.inc"\n} // namespace RegionalVariants');p.write_text(s,encoding='utf8',newline='\n')
shutil.copy2(R.parent/'variant_model_052.inc',R/'libmscore/regionalvarianttools.inc')
for suffix in ['cpp','h']:shutil.copy2(R.parent/f'regionalcomparison_052.{suffix}',R/f'mscore/workflow/regionalcomparison.{suffix}')
p=R/'libmscore/regionalvariants.cpp';s=p.read_text(encoding='utf8').replace('#include "audio.h"','#include "audio.h"\n#include "articulation.h"')
anchor='      auto assets = data.value("assets").toMap();\n      for (auto it = assets.begin(); it != assets.end(); ++it) {'
assert s.count(anchor)==1
s=s.replace(anchor,'''      const auto combinations=data.value("combinations").toList();QSet<QString> combinationIds;
      if(combinations.size()>64){*problem=QObject::tr("组合数量超过64个。");return false;}
      for(auto value:combinations){const auto combination=value.toMap();const auto key=combination.value("id").toString();const auto choices=combination.value("choices").toMap();
            if(key.isEmpty()||combinationIds.contains(key)||choices.isEmpty()){*problem=QObject::tr("组合名称或写法记录不完整。");return false;}
            combinationIds.insert(key);
            for(auto i=choices.begin();i!=choices.end();++i){const int group=groupIndex(groups,i.key());
                  if(group<0||variantIndex(groups[group].toMap().value("variants").toList(),i.value().toString())<0){*problem=QObject::tr("组合中的写法已经改变，请恢复先前保存的文件。");return false;}
                  }
            }
'''+anchor)
p.write_text(s,encoding='utf8',newline='\n')
p=R.parent/'apply_native.py';s=p.read_text(encoding='utf8');at=s.index(" patch('mscore/plugin/plugin.cmake'");s=s[:at]+" patch('mscore/plugin/plugin.cmake','    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcontrols.cpp','    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcontrols.cpp\\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcomparison.cpp\\n    ${PROJECT_SOURCE_DIR}/mscore/workflow/regionalcomparison.h')\n"+s[at:];p.write_text(s,encoding='utf8',newline='\n')
