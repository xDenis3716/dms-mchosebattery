import QtQuick
import Quickshell.Io
import qs.Common
import qs.Widgets
import qs.Modules.Plugins

PluginComponent {
    id: root

    property int battery: -1
    property string status: "starting"
    readonly property string helperPath: Qt.resolvedUrl("mchose_battery.py").toString().replace("file://", "")
    readonly property string label: battery >= 0 ? battery + "%" : "?"
    readonly property color pillColor: battery >= 0 ? Theme.surfaceText : Theme.surfaceVariantText

    function handleOutput(t) {
        try {
            var d = JSON.parse(t.trim())
            if (d.ok) {
                root.battery = d.battery2
                root.status = "ok"
            } else {
                root.status = d.reason; root.battery = -1
            }
        } catch (e) {
            root.status = "bad output"; root.battery = -1
        }
    }

    Process {
        id: reader
        command: ["python3", root.helperPath]
        stdout: StdioCollector {
            onStreamFinished: root.handleOutput(text)
        }
    }

    Timer {
        interval: 120000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            if (!reader.running) {
                reader.running = true
            }
        }
    }

    horizontalBarPill: Component {
        Row {
            spacing: Theme.spacingXS

            DankIcon {
                name: "mouse"
                size: Theme.iconSize - 4
                color: root.battery >= 0 ? Theme.primary : Theme.surfaceVariantText
                anchors.verticalCenter: parent.verticalCenter
            }

            StyledText {
                text: root.label
                font.pixelSize: Theme.fontSizeMedium
                color: root.pillColor
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    verticalBarPill: Component {
        Column {
            spacing: Theme.spacingXS

            DankIcon {
                name: "mouse"
                size: Theme.iconSize - 4
                color: root.battery >= 0 ? Theme.primary : Theme.surfaceVariantText
                anchors.horizontalCenter: parent.horizontalCenter
            }

            StyledText {
                text: root.label
                font.pixelSize: Theme.fontSizeSmall
                color: root.pillColor
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }
}

