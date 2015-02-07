Item {
	x: 200;
	y: 100;

	Rectangle {
		id: rect1;
		width: 100;
		height: 100;
		color: "#f00";
	}

	Rectangle {
		id: rect2;
		width: 100;
		height: 100;
		x: 150;
		y: 100;
		color: "#0f0";
		radius: 20;

		border.width: 10;
		border.color: "#c80";
	}

	Rectangle {
		id: rect3;
		radius: 10;
		width: 100;
		height: 100;
		x: 300;
		color: "#00f";
	}
	Text {
		x: 200;
		y: 200;
		text: "Hello, world";
		font.pointSize: 32;
	}

	Rectangle {
		anchors.right: rect3.right;
		anchors.left: rect1.left;
		anchors.leftMargin: 20;
		anchors.rightMargin: 20;
		height: 30;
		color: "#f0f";
	}
}
