/*** @using { core.RAIIEventEmitter } **/

const platform = require("tns-core-modules/platform")
const utils = require("tns-core-modules/utils/utils")

const observableModule = require("data/observable")
const Observable = observableModule.Observable

const layoutModule = require('ui/layouts/absolute-layout')
const AbsoluteLayout = layoutModule.AbsoluteLayout

const labelModule = require('ui/label')
const Label = labelModule.Label

const imageModule = require('ui/image')
const Image = imageModule.Image

function dekebabize(name) {
	return name.replace(/-([a-z])/g, (g) => { return g[1].toUpperCase() })
}

const styleNames = {
	textAlign: 'textAlignment'
}

const specialHandlers = {
	left: (object, name, value) => {
		object[name] = value
		AbsoluteLayout.setLeft(object, value)
	},

	top: (object, name, value) => {
		object[name] = value
		AbsoluteLayout.setTop(object, value)
	},

	visibility: (object, name, value) => {
		object[name] = value === 'inherit'? 'visible': value
	},
}


class Element extends _globals.core.RAIIEventEmitter {
	constructor(layout, impl) {
		super()
		this.layout = layout
		this.impl = impl
		if (impl)
			layout.addChild(impl)
	}

	append(el) {
		this.layout.addChild((el instanceof Element)? el.layout: el)
	}

	remove() {
		let layout = this.layout
		let parent = layout.parent
		if (parent)
			parent.removeChild(layout)
	}

	addClass(name) {
		//log('Element.addClass', name)
	}

	_setStyleInObject(object, name, value) {
		if (!object)
			return true

		if (name in styleNames)
			name = styleNames[name]

		if (name in object) {
			if (name in specialHandlers) {
				specialHandlers[name](object, name, value)
			} else {
				object[name] = value
			}
			return true
		} else
			return false
	}

	_setStyle(name, value) {
		let ok1 = this._setStyleInObject(this.layout, name, value)
		let ok2 = this._setStyleInObject(this.impl, name, value)
		if (!ok1 && !ok2)
			log('skipping style', name)
	}

	style(target, value) {
		if (typeof target === 'object') {
			for(let k in target) {
				this.style(k, target[k])
			}
		} else {
			let layout = this.layout
			let name = dekebabize(target)
			if (value === undefined)
				throw new Error("style is write-only")
			this._setStyle(name, value)
		}
	}
}

let context = null
let page = null
let finalization_callback = null

exports.capabilities = {}
exports.init = function(ctx) {
	log('backend initialization...')
	context = ctx
	const options = ctx.options
	const nativeContext = options.nativeContext
	const parentLayout = nativeContext.getViewById(options.id)
	if (!parentLayout)
		throw new Error('could not find view with id ' + options.id)

	page = nativeContext
	ctx.element = new Element(parentLayout, null)

	let mw = page.getMeasuredWidth(), mh = page.getMeasuredHeight()
	let w = utils.layout.toDeviceIndependentPixels(mw)
	let h = utils.layout.toDeviceIndependentPixels(mh)
	log('page size: ', mw, 'x', mh, w, 'x', h)
	context.width = w
	context.height = h
}


exports.run = function(ctx, callback) {
	finalization_callback = callback
}

exports.finalize = function() {
	finalization_callback()
	finalization_callback = null
}

exports.initSystem = function(system) {
}

exports.createElement = function(ctx, tag, cls) {
	//log('creating element', tag, cls)
	let impl
	switch(cls) {
		case 'core-text':
			impl = new Label()
			break
		case 'core-image':
			impl = new Image()
			break
		default:
			impl = null
	}
	return new Element(new AbsoluteLayout(), impl)
}

exports.initImage = function(image) {
}

var ImageStatusNull			= 0
var ImageStatusLoaded		= 1
var ImageStatusUnloaded		= 2
var ImageStatusError		= 3


exports.loadImage = function(image) {
	log('loading image ' + image.source)
	let source
	if (image.source.indexOf('://') >= 0)
		source = image.source
	else if (source)
		source = '~/' + image.source
	else
		source = ''

	image.element.impl.imageSource = source
}

exports.initText = function(text) {
}

exports.setText = function(text, html) {
	text.element.impl.text = html
}

exports.layoutText = function(text) {
	log('layoutText')
}

exports.setAnimation = function (component, name, animation) {
	return false
}

exports.requestAnimationFrame = function(callback) {
	return setTimeout(callback, 0)
}

exports.cancelAnimationFrame = function (timer) {
	clearTimeout(timer)
}

exports.tick = function(ctx) {
}
