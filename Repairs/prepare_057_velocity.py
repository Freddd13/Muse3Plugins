from pathlib import Path
R=Path(__file__).resolve().parent;P=R.parent;H=P.parent/'muse3_dev/MuseScore';D=R/'staged057'
def stage(k,s):
 p=D/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode())
s=(P/'PerformanceExpression/Alignment.js').read_text(encoding='utf8').replace('(config.strength===undefined?50:config.strength)','(config.strength===undefined?100:config.strength)',1)
s=s.replace('        var measured=Math.max(', '''        if(config.velocityWriteMode==="follow"&&n.velocityBase<=0){kept.push({id:n.id,reason:"当前位置的力度参考为 0；选择逐音固定力度即可采用演奏值。"});return;}
        var measured=Math.max(''',1)
s=s.replace('target:target,source:"measured"','target:target,originalVelocity:n.velocity,writeMode:config.velocityWriteMode||"preserve",sourceSeconds:m.seconds,scoreSeconds:n.scoreSeconds===undefined?n.onSeconds:n.scoreSeconds,source:"measured"',1)
s=s.replace('source:"inferred"','writeMode:config.velocityWriteMode||"preserve",source:"inferred"',1)
stage('plugins/PerformanceExpression/Alignment.js',s)
s=(P/'PerformanceExpression/PerformanceExpression_MS3.qml').read_text(encoding='utf8')
s=s.replace('strength:50,velocityStrength:50','strength:100,velocityStrength:100,velocityWriteMode:"fixed"',1)
s=s.replace(' function cancel(){',''' function freshVelocitySettings(){var next=Project.copy(config);next.velocityStrength=100;next.velocityWriteMode="fixed";config=next}
 function velocityWriteText(item){var mode=item.writeMode||"preserve";return mode==="fixed"||mode==="preserve"&&item.oldType===1?"固定力度 "+item.target:"跟随力度记号 "+Math.round((item.target-item.oldBase)*100/item.oldBase)+"%"}
 function cancel(){''',1)
s=s.replace('   root.appliedProgress=({velocity:{},tempos:{}});root.recordingImport=true','   root.freshVelocitySettings();root.appliedProgress=({velocity:{},tempos:{}});root.recordingImport=true',1)
s=s.replace('onAccepted:{root.appliedProgress=({velocity:{},tempos:{}});root.loadedSourceHash="";', 'onAccepted:{root.freshVelocitySettings();root.appliedProgress=({velocity:{},tempos:{}});root.loadedSourceHash="";',1)
s=s.replace('root.config.rubato?"力度 / 速度强度 %":"力度强度 %"','root.config.rubato?"采用演奏效果的比例（力度／速度）":"采用演奏力度的比例"',1)
at=s.index('  Label {visible:!root.compact&&root.previewing;')
s=s[:at]+'''  RowLayout {Layout.fillWidth:true
   Label {text:"保存方式";color:theme.muted}
   Desk.DeskComboBox {objectName:"expressionVelocityWriteMode";Layout.fillWidth:true;model:["逐音固定力度","继续跟随力度记号","保留各音原保存方式"];currentIndex:root.config.velocityWriteMode==="fixed"?0:root.config.velocityWriteMode==="follow"?1:2;onActivated:root.editConfig("velocityWriteMode",["fixed","follow","preserve"][currentIndex]);ToolTip.visible:hovered;ToolTip.text:currentIndex===0?"这些音直接采用演奏力度，谱上的力度记号继续显示。":currentIndex===1?"按各音的力度记号换算增减百分比；以后调整记号，这些音一起变化。":"各音继续使用原来的相对或固定方式。"}
  }
'''+s[at:]
s=s.replace('(modelData.oldType===1?modelData.target:Math.round((modelData.target-modelData.oldBase)*100/modelData.oldBase))','root.velocityWriteText(modelData)',1)
s=s.replace('(modelData.oldBpm||modelData.oldBase)','(modelData.oldBpm||modelData.originalVelocity||modelData.oldBase)',1)
stage('plugins/PerformanceExpression/PerformanceExpression_MS3.qml',s)
base=R/'native/mscore/workflow/workflowexpression.cpp';s=(base if base.exists() else H/'mscore/workflow/workflowexpression.cpp').read_text(encoding='utf8')
a='  auto type=note->veloType();velocities.insert(note,{type,type==Ms::Note::ValueType::USER_VAL?target:NoteVelocity::offsetFor(base,target)});'
b='''  const auto mode=v.value("writeMode","preserve").toString();
  if(mode!="fixed"&&mode!="follow"&&mode!="preserve")return {{"error",tr("请选择逐音固定力度、跟随力度记号或保留原保存方式。")}};
  if(mode=="follow"&&base<=0)return {{"error",tr("当前位置的力度参考为 0，选择逐音固定力度后可以采用演奏值。")}};
  auto type=mode=="fixed"?Ms::Note::ValueType::USER_VAL:mode=="follow"?Ms::Note::ValueType::OFFSET_VAL:note->veloType();
  velocities.insert(note,{type,type==Ms::Note::ValueType::USER_VAL?target:NoteVelocity::offsetFor(base,target)});'''
assert a in s;s=s.replace(a,b,1);stage('native/mscore/workflow/workflowexpression.cpp',s)
print('0.57 velocity adoption staged separately')
