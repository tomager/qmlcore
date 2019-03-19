var shakaGetMessage = function(code) {
	for (var k in shaka.util.Error.Code) {
		if (shaka.util.Error.Code[k] == code)
			return k
	}
}

var shakaSignalError = function(ui, err) {
	if (!err.message)
		err.message = shakaGetMessage(err.code)
	ui.error(err)
}

var Player = function(ui) {
	var player = ui._context.createElement('video')

	this._player = player

	if (!shaka.Player.isBrowserSupported()) {
		throw new Error("browser is not supported, backend should not have been registered")
	}

	var shakaPlayer = new shaka.Player(player.dom);
	this.shakaPlayer = shakaPlayer;

	var dom = player.dom
	player.on('play', function() { ui.waiting = false; ui.paused = dom.paused }.bind(ui))
	player.on('pause', function() { ui.paused = dom.paused }.bind(ui))
	player.on('ended', function() { ui.finished() }.bind(ui))
	player.on('seeked', function() { log("seeked"); ui.seeking = false; ui.waiting = false }.bind(ui))
	player.on('canplay', function() { log("canplay", dom.readyState); ui.ready = dom.readyState }.bind(ui))
	player.on('seeking', function() { log("seeking"); ui.seeking = true; ui.waiting = true }.bind(ui))
	player.on('waiting', function() { log("waiting"); ui.waiting = true }.bind(ui))
	player.on('stalled', function() { log("Was stalled", dom.networkState); ui.waiting = true; ui.stalled = true }.bind(ui))
	player.on('emptied', function() { log("Was emptied", dom.networkState); }.bind(ui))
	player.on('volumechange', function() { ui.muted = dom.muted }.bind(ui))
	player.on('canplaythrough', function() { log("ready to play"); ui.paused = dom.paused }.bind(ui))

	var onError = function() {
		log("Player error occurred", dom.error, "src", ui.source)

		if (!dom.error || !ui.source)
			return

		ui.error(dom.error)

		log("player.error", dom.error)
		switch (dom.error.code) {
		case 1:
			log("MEDIA_ERR_ABORTED error occurred")
			break;
		case 2:
			log("MEDIA_ERR_NETWORK error occurred")
			break;
		case 3:
			log("MEDIA_ERR_DECODE error occurred")
			break;
		case 4:
			log("MEDIA_ERR_SRC_NOT_SUPPORTED error occurred")
			break;
		default:
			log("UNDEFINED error occurred")
			break;
		}
	}.bind(ui)

	player.on('error', onError)
	this.shakaPlayer.addEventListener('error', ui._context.wrapNativeCallback(onError));

	player.on('timeupdate', function() {
		ui.waiting = false
		ui.stalled = false
		if (!ui.seeking)
			ui.progress = dom.currentTime
	}.bind(ui))

	player.on('durationchange', function() {
		var d = dom.duration
		log("Duration", d)
		ui.duration = isFinite(d) ? d : 0
	}.bind(ui))

	player.on('progress', function() {
		var last = dom.buffered.length - 1
		ui.waiting = false
		if (last >= 0)
			ui.buffered = dom.buffered.end(last) - dom.buffered.start(last)
	}.bind(ui))

	this.element = player
	this.ui = ui
	this.setAutoPlay(ui.autoPlay)

	ui.element.remove()
	ui.element = player
	ui.parent.element.append(ui.element)
}

Player.prototype = Object.create(_globals.video.html5.backend.Player.prototype)

Player.prototype.setupDrm = function(type, options, callback, error) {
	var laServer = {}
	if (type === "widevine")
		laServer["com.widevine.alpha"] = options.laServer
	else if (type === "playready")
		laServer["com.microsoft.playready"] = options.laServer
	else
		error ? error(new Error("Unknown or not supported DRM type " + type)) : log("Unknown or not supported DRM type " + type)

	var config = { drm: { servers: laServer }, manifest: { dash: { defaultPresentationDelay: 30 } } }
	log("SetupDRM", config)
	this.shakaPlayer.configure(config);
	if (callback)
		callback()
}

Player.prototype.stop = function() {
	log("stop player")
	var self = this
	if (this._loaded) {
		this.shakaPlayer.unload()
			.then(function(e) { log("Unloaded"); self.shakaPlayer.destroy(); self.shakaPlayer = new shaka.Player(self._player.dom); })
			.catch(function(e) { log("Unload failed", e); self.shakaPlayer.destroy(); self.shakaPlayer = new shaka.Player(self._player.dom); })
	} else {
		this.pause()
	}
}

Player.prototype.setSource = function(url) {
	var ui = this.ui
	if (url) {
		var urlLower = url.toLowerCase()
		var querryIndex = url.indexOf("?")
		if (querryIndex >= 0)
			urlLower = urlLower.substring(0, querryIndex)
		var extIndex = urlLower.lastIndexOf(".")
		var extension = urlLower.substring(extIndex, urlLower.length)
		var player = this._player
		if (extension === ".mpd") {
			this._loaded = true
			this.shakaPlayer.load(url)
				.then(function() { console.log('The video has now been loaded!'); })
				.catch(ui._context.wrapNativeCallback(function(err) { log("Failed to load manifest", err); shakaSignalError(ui, err) }));
		} else {
			this._loaded = false
			this._player.dom.src = url
		}
	}
}

Player.prototype.getVideoTracks = function() {
	var video = []
	var tracks = this.shakaPlayer.getVariantTracks()

	for (var i = 0; i < tracks.length; ++i) {
		var track = tracks[i]
		video.push({
			id: track.id,
			width: track.width,
			framerate: track.frameRate,
			bandwidth: track.videoBandwidth,
			height: track.height
		})
	}
	return video
}

Player.prototype.getAudioTracks = function() {
	var tracks = this.shakaPlayer.getVariantTracks()
	var audioTracks = {}
	for (var i = 0; i < tracks.length; ++i) {
		var track = tracks[i]
		if (audioTracks[track.audioId])
			continue

		audioTracks[track.audioId] = {
			id: track.audioId,
			language: track.language,
			codec: track.audioCodec
		}
	}

	var audio = []
	for (var i in audioTracks) {
		audio.push(audioTracks[i])
	}
	log("Available audio tracks", audio)

	return audio
}

Player.prototype.setAudioTrack = function(trackId) {
	var tracks = this.shakaPlayer.getVariantTracks()

	var found = tracks.filter(function(element) {
		return element.audioId === trackId
	})

	log("Try to set audio track", found)
	if (found && found.length) {
		this.shakaPlayer.configure({
			abr: {
				enabled: false,
				switchInterval: 0
			}
		});
		this.shakaPlayer.selectVariantTrack(found[0])
	}
}

Player.prototype.setVideoTrack = function(trackId) {
	var tracks = this.shakaPlayer.getVariantTracks()

	var found = tracks.filter(function(element) {
		return element.id === trackId
	})

	log("Try to set video track", found)
	if (found && found.length) {
		this.shakaPlayer.configure({
			abr: {
				enabled: false,
				switchInterval: 0
			}
		});
		this.shakaPlayer.selectVariantTrack(found[0])
	}
}

exports.createPlayer = function(ui) {
	return new Player(ui)
}

exports.probeUrl = function(url) {
	return 150
}

exports.Player = Player
