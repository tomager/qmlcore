ListView {
	height: 50;
	anchors.top: parent.top;
	anchors.left: parent.left;
	anchors.right: parent.right;
	spacing: 2;
	orientation: ListView.Horizontal;
	delegate: IconTextDelegate { }
}