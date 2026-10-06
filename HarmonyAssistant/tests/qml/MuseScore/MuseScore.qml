import QtQuick 2.9
Item {
    property string menuPath
    property string description
    property string version
    property bool requiresScore
    property string pluginType
    property string dockArea
    property var curScore: null
    property var scores: []
    signal run()
    signal scoreStateChanged(var state)
}
