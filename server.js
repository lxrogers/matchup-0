//
// # SimpleServer
//
// A simple chat server using Socket.IO, Express, and Async.
//
var http = require('http');
var path = require('path');


var async = require('async');
var socketio = require('socket.io');
var express = require('express');

var tools = require('./tools')

var games_updating = 0;
//
// ## SimpleServer `SimpleServer(obj)`
//
// Creates a new instance of SimpleServer with the following options:
//  * `port` - The HTTP port to listen on. If `process.env.PORT` is set, _it overrides this value_.
//

//networking
var router = express();
var server = http.createServer(router);
var io = socketio.listen(server);

router.use(express.static(path.resolve(__dirname, 'client')));
var messages = [];
var sockets = [];

//matchup data
var schedule = null; //holds tools.Schedule Object 
var liveGames = {}; // map of gameID -> liveGame 

io.on('connection', function (socket) {
    messages.forEach(function (data) {
      socket.emit('message', data);
    });

    sockets.push(socket);

    socket.on('disconnect', function () {
      sockets.splice(sockets.indexOf(socket), 1);
      updateRoster();
    });

    socket.on('message', function (msg) {
      var text = String(msg || '');

      if (!text)
        return;

      socket.get('name', function (err, name) {
        var data = {
          name: name,
          text: text
        };

        broadcast('message', data);
        messages.push(data);
      });
    });

    socket.on('identify', function (name) {
      socket.set('name', String(name || 'Anonymous'), function (err) {
        updateRoster();
      });
    });
  });

function updateRoster() {
  async.map(
    sockets,
    function (socket, callback) {
      socket.get('name', callback);
    },
    function (err, names) {
      broadcast('roster', names);
    }
  );
}

function broadcast(event, data) {
  sockets.forEach(function (socket) {
    socket.emit(event, data);
  });
}

server.listen(process.env.PORT || 3000, process.env.IP || "0.0.0.0", function(){
  var addr = server.address();
  console.log("Chat server listening at", addr.address + ":" + addr.port);
});

//Update Schedule
function updateSchedule() {
  tools.getSchedule(tools.getEasternTimezoneDate(), function(err, _schedule) {
    schedule = _schedule;
    console.log(_schedule);
  });
}

//update livegames using schedule
function updateLiveGames(callback) {
  games_updating = schedule.scheduleGames.length;
  schedule.scheduleGames.forEach(function(scheduleGame) {
    var liveGame = tools.getLiveGame(scheduleGame.gameID, function(err, liveGame) {
      var key = "" + liveGame.gameID;
      updateLiveGame(key, liveGame)
    });
  });
}

function updateLiveGame(key, liveGame) {
  liveGames[key] = liveGame;
  //broadcast('message', {name: "hey", text:"hi"});
  
  games_updating -= 1;
  console.log('broadcasting update ' + key + " games left: " + games_updating)
  if (games_updating == 0)
    broadcast('liveupdate', liveGames);
  
}

var count = 0;
setInterval(function() {
  console.log("UPDATING GAMES");
  updateLiveGames();
}, 10000)

updateSchedule();