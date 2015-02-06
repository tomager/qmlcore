/* qml.core javascript code */

if (!_globals.core)
	_globals.core = {}

_globals.core.Object = function(parent) {
	this.parent = parent;
	this._local = {}
	this._changedHandlers = {}
}

_globals.core.Object.prototype._update = function(name, value) {}

_globals.core.Object.prototype._setId = function (name) {
	var p = this;
	while(p) {
		p._local[name] = this;
		p = p.parent;
	}
}

_globals.core.Object.prototype.onChanged = function (name, callback) {
	if (name in this._changedHandlers)
		this._changedHandlers[name].push(callback);
	else
		this._changedHandlers[name] = [callback];
}

_globals.core.Object.prototype._emitChanged = function (name, value) {
	if (name in this._changedHandlers) {
		var handlers = this._changedHandlers[name];
		handlers.forEach(function(callback) { callback(value); });
	}
}

_globals.core.Object.prototype.get = function (name) {
	if (name in this._local)
		return this._local[name];
	if (this.hasOwnProperty(name))
		return this[name];
	console.log(name, this);
	throw ("invalid property requested: '" + name + "' in context of " + this);
}


function setup(context) {
	_globals.core.Item.prototype.children = []

	_globals.core.Border.prototype._update = function(name, value) {
		switch(name) {
			case 'width': this.parent.element.css('border-width', value); return;
			case 'color': this.parent.element.css('border-color', value); return;
		}
	}

	_globals.core.Item.prototype._update = function(name, value) {
		switch(name) {
			case 'width': 	this.element.css('width', value); return;
			case 'height':	this.element.css('height', value); return;
			case 'x':		this.element.css('left', value); return;
			case 'y':		this.element.css('top', value); return;
			case 'radius':	this.element.css('border-radius', value); return;
		}
		_globals.core.Object.prototype._update.apply(this, arguments);
	}

	_globals.core.Font.prototype._update = function(name, value) {
		switch(name) {
			case 'pointSize': this.parent.element.css('font-size', value + "pt"); return;
			case 'pixelSize': this.parent.element.css('font-size', value + "px"); return;
			case 'italic': this.parent.element.css('font-style', value? 'italic': 'normal'); return;
		}
		_globals.core.Object.prototype._update.apply(this, arguments);
	}

	_globals.core.Text.prototype._update = function(name, value) {
		switch(name) {
			case 'text': this.element.text(value); return;
		}
		_globals.core.Item.prototype._update.apply(this, arguments);
	}

	_globals.core.Rectangle.prototype._update = function(name, value) {
		switch(name) {
			case 'color': this.element.css('background-color', value); return;
		}
		_globals.core.Item.prototype._update.apply(this, arguments);
	}
}

exports.Context = function() {
	var windowW = $(window).width();
	var windowH = $(window).height();
	console.log("window size: " + windowW + "x" + windowH);
	var body = $('body');
	var div = $("<div id='renderer'></div>");
	body.append(div)
	//fixme: derive context from Object
	this._local = {}
	this.element = div
	this.element.css({width: windowW, height: windowH});
	console.log("context created");

	setup(this);
}

exports.Context.prototype.start = function(name) {
	var proto;
	if (typeof name == 'string') {
		console.log('creating component...', name);
		var path = name.split('.');
		proto = _globals;
		for (var i = 0; i < path.length; ++i)
			proto = proto[path[i]]
	}
	else
		proto = name;
	var instance = Object.create(proto.prototype);
	proto.apply(instance, [this]);
	return instance;
}

exports.addProperty = function(self, type, name) {
	var value;
	switch(type) {
		case 'int':			value = 0;
		case 'bool':		value = false;
		case 'real':		value = 0.0;
		default: if (type[0].toUpperCase() == type[0]) value = null;
	}
	Object.defineProperty(self, name, {
		get: function() {
			return value;
		},
		set: function(newValue) {
			oldValue = value;
			if (oldValue != newValue) {
				value = newValue;
				self._update(name, newValue, oldValue);
				self._emitChanged(name, newValue);
			}
		}
	});
}

exports._bootstrap = function(self, name) {
	switch(name) {
		case 'core.Item':
			if (self.element)
				throw "double ctor call";
			self.element = $('<div/>');
			self.parent.element.append(self.element);
			break;
	}
}
