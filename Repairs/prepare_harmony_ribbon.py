from pathlib import Path
p=Path('HarmonyAssistant/Preferences.js');s=p.read_text(encoding='utf8').replace('respectExistingHarmony:true,chordMask:true','respectExistingHarmony:true,avoidScoreContent:false,chordMask:true',1).replace('"respectExistingHarmony","chordMask"','"respectExistingHarmony","avoidScoreContent","chordMask"',1);p.write_bytes(s.encode('utf8'))
p=Path('HarmonyAssistant/AppearanceEditor.qml');s=p.read_text(encoding='utf8').replace('    DeskSwitch {text:"记号背景遮罩"','    DeskSwitch {text:"避让其它谱面内容"; objectName:"harmonyAvoidScoreContent"; checked:configuration.avoidScoreContent; onToggled:if(checked!==configuration.avoidScoreContent)editor.option("avoidScoreContent",checked)}\n    DeskSwitch {text:"记号背景遮罩"',1)
s=s.replace('关闭遮罩后只显示文字，仍避让原谱，当前记号以文字色高亮。','默认在最上层显示；相邻记号重叠时上下排列。避让和遮罩分别开关，横向位置始终对应和弦变化。')
s=s.replace('关闭可同时显示，仍会避让。编辑框始终优先。','关闭后可同时显示原谱和分析结果。开启避让时也会保护正在编辑的文字。')
s=s.replace('记号在同一系统统一高度，过密时省略；双击可跳转面板。','不冲突的记号保持同一高度，过密时上下排列；双击可跳转面板。');p.write_bytes(s.encode('utf8'))
p=Path('HarmonyAssistant/HarmonyAssistant_MS3.qml');s=p.read_text(encoding='utf8').replace('version: "1.5.0"','version: "1.6.0"',1).replace('property int preferredRibbonHeight: 140','property int preferredRibbonHeight: 44',1).replace('            d.chordMask=configuration.chordMask','            d.chordMask=configuration.chordMask;d.onTop=true;d.avoidScoreContent=configuration.avoidScoreContent',1)
start=s.index('        Item {\n            visible:root.ribbon; anchors.fill:parent; clip:true')
end=s.index('\n        }\n    }\n}',start)+len('\n        }')
new='''        Item {
            visible:root.ribbon; anchors.fill:parent; clip:true
            Item {
                id:ribbonGroup; objectName:"harmonyRibbonGroup"
                width:Math.min(850,Math.max(100,parent.width-ribbonControls.width-36))
                height:Math.min(38,parent.height-4);anchors.verticalCenter:parent.verticalCenter
                x:{var maximum=Math.max(12,parent.width-ribbonControls.width-width-36);
                    return configuration.ribbonAlign===0 ? 12 : configuration.ribbonAlign===2 ? maximum :
                        configuration.ribbonAlign===3 ? 12+(maximum-12)*configuration.ribbonPosition/100 : Math.max(12,Math.min(maximum,(parent.width-ribbonControls.width-width)/2))}
                RowLayout {
                    anchors.fill:parent;spacing:10
                    StableLabel {objectName:"harmonyRibbonChord";text:root.summaryChordText;color:root.summaryInk;font.pixelSize:22;font.bold:true;Layout.preferredWidth:Math.min(240,Math.max(70,ribbonGroup.width*.4));Layout.alignment:Qt.AlignVCenter}
                    StableLabel {text:root.summaryDegreeText;color:root.summaryInk;font.pixelSize:13;Layout.preferredWidth:Math.min(80,ribbonGroup.width*.22);Layout.alignment:Qt.AlignVCenter}
                    StableLabel {text:(configuration.summaryMode===0?"实时":"所属和弦")+" · "+positionText;color:muted;font.pixelSize:11;visible:ribbonGroup.width>360;Layout.fillWidth:true;Layout.alignment:Qt.AlignVCenter}
                    Row {
                        id:ribbonTones;visible:ribbonGroup.width>=760;spacing:3;Layout.alignment:Qt.AlignVCenter
                        Repeater {model:root.summaryToneRows;delegate:Rectangle {
                            width:26;height:24;color:theme.field;radius:1
                            Rectangle{x:0;y:5;width:2;height:14;color:modelData.present?modelData.color:"#d0d0d0"}
                            UiLabel{anchors.centerIn:parent;text:modelData.label;color:modelData.present?ink:muted;font.pixelSize:11}
                        }}
                    }
                }
            }
            Row {
                id:ribbonControls;spacing:4;width:230;anchors.right:parent.right;anchors.rightMargin:12;anchors.verticalCenter:parent.verticalCenter
                DeskComboBox {width:98;model:["靠左","居中","靠右","自定位置"];currentIndex:configuration.ribbonAlign;implicitHeight:28;font.pixelSize:11;onActivated:root.setRibbonPosition(currentIndex)}
                DeskButton {width:58;text:"详情";checked:root.dualDetailActive;visible:typeof root.showDetailPanel==="function";onClicked:root.toggleDetailPanel();ToolTip.visible:hovered;ToolTip.text:"显示／隐藏右侧详情"}
                DeskButton {width:58;text:"更多";onClicked:ribbonMenu.open()}
                Menu {
                    id:ribbonMenu
                    MenuItem{text:root.unplacedMarkers.length?"记号列表（有待检查项）":"记号列表";enabled:root.advancedNative;onTriggered:{markerWindow.show();markerWindow.raise();markerWindow.requestActivate()}}
                    MenuItem{text:"详细窗口";onTriggered:root.openDetailWindow()}
                    MenuItem{text:"悬浮这个面板";enabled:typeof root.setPanelFloating==="function";onTriggered:root.setPanelFloating(true)}
                    MenuItem{text:"收紧顶部高度";enabled:typeof root.resizePanel==="function";onTriggered:root.resizePanel(44)}
                }
            }
        }'''
s=s[:start]+new+s[end:];p.write_bytes(s.encode('utf8'))
