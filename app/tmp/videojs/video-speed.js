(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.videojsPlaybackrateAdjuster = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
(function (global){
'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

function _interopDefault(ex) {
  return ex && (typeof ex === 'undefined' ? 'undefined' : _typeof(ex)) === 'object' && 'default' in ex ? ex['default'] : ex;
}

var videojs = _interopDefault((typeof window !== "undefined" ? window['videojs'] : typeof global !== "undefined" ? global['videojs'] : null));

var createNewRanges = function createNewRanges(timeRanges, playbackRate) {
  var newRanges = [];

  for (var i = 0; i < timeRanges.length; i++) {
    newRanges.push([timeRanges.start(i) / playbackRate, timeRanges.end(i) / playbackRate]);
  }

  return videojs.createTimeRange(newRanges);
};

var playbackrateAdjuster = function playbackrateAdjuster(player) {
  var tech = void 0;

  player.on('ratechange', function () {
    tech.trigger('durationchange');
    tech.trigger('timeupdate');
  });

  return {
    setSource: function setSource(srcObj, next) {
      next(null, srcObj);
    },
    setTech: function setTech(newTech) {
      tech = newTech;
    },
    duration: function duration(dur) {
      return dur / player.playbackRate();
    },
    currentTime: function currentTime(ct) {
      return ct / player.playbackRate();
    },
    setCurrentTime: function setCurrentTime(ct) {
      return ct * player.playbackRate();
    },
    buffered: function buffered(bf) {
      return createNewRanges(bf, player.playbackRate());
    },
    seekable: function seekable(_seekable) {
      return createNewRanges(_seekable, player.playbackRate());
    },
    played: function played(_played) {
      return createNewRanges(_played, player.playbackRate());
    }
  };
};

// Register the plugin with video.js.
videojs.use('*', playbackrateAdjuster);

// Include the version number.
playbackrateAdjuster.VERSION = '1.0.0';

module.exports = playbackrateAdjuster;

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

},{}]},{},[1])(1)
});
