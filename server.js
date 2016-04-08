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
router.use(express.static(__dirname + '/public'));
router.set('view engine', 'jade');
router.set('views', './public/views')
io.set('log level', 1);

//router.use(express.static(path.resolve(__dirname, 'client')));
router.get('/', function (req, res) {
  res.render('index', { title: 'Hey', message: 'Hello there!'});
});
var sockets = [];

//matchup data
var schedule = {}; // map of gameID -> scheduleGame
var liveGames = {}; // map of gameID -> liveGame 
var playerData = {}; // map of Player key -> data object

io.on('connection', function (socket) {
    socket.emit('liveupdate', packageLiveGames());
  
    sockets.push(socket);

    socket.on('disconnect', function () {
      sockets.splice(sockets.indexOf(socket), 1);
    });
    
  });

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
function updateSchedule(callback) {
  tools.getSchedule(tools.getEasternTimezoneDate(), function(err, _schedule) {
    schedule = _schedule;
    console.log(_schedule);
    if (callback) callback();
  });
}

//update livegames using schedule
function updateLiveGames(callback) {
  games_updating = Object.keys(schedule).length
  
  for (var gid in schedule) {
    tools.getLiveGame(gid, function(err, liveGame) {
      var key = "" + liveGame.gameID;
      updateLiveGame(key, liveGame);
    });
  }
}

function updateLiveGame(key, liveGame) {
  liveGames[key] = liveGame;
  
  games_updating -= 1;
  
  if (games_updating == 0)
    console.log('broadcasting update')
    broadcast('liveupdate', packageLiveGames());
}

function packageLiveGames() {
  var package = [];
  
  //convert to array
  for (var propertyName in liveGames) {
    package.push(liveGames[propertyName]);
  }
  
  //sort by quarter
  package.sort(function(a, b) {
    return (a.order - b.order);
  })
  //break into triplets
  var tripletPackage = []
            
  for (var i = 0; i < package.length; i++) {
    var tripletIndex = Math.floor(i / 3);
    
    if (tripletIndex % 3 == 0) {
      tripletPackage.push([])
    }
    tripletPackage[tripletIndex].push(package[i]);
  }
  
  return tripletPackage;
}

var count = 0;
setInterval(function() {
  console.log("UPDATING GAMES");
  updateLiveGames();
}, 10000)

updateSchedule(updateLiveGames);