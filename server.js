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
var tonydb = require('./tonydb')

var games_updating = 0;
var retrieved_player_data = false;
var retrieved_lineup_data = false;
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

console.log("environment: ", router.settings.env)
tonydb.initialize(router.settings.env);

//router.use(express.static(path.resolve(__dirname, 'client')));
router.get('/', function (req, res) {
  res.render('index');
});

router.get('/game/:gameid', function(req, res) {
  var gid = req.params.gameid;
  //console.log(packageGameResponse(gid));
  res.render('game', {'gameid': gid, 'livegame': packageGameResponse(gid)});
  //res.send("gameid is set to " + req.params.gameid);
});

var matchupSockets = [];

//matchup data
var schedule = {}; // map of gameID -> scheduleGame
var liveGames = {}; // map of gameID -> liveGame 
var playerData = {}; // map of GameID -> Player key -> data object
var lineupData = {}; // Teams -> LineupKey -> Linup Data

io.on('connection', function (socket) {
    console.log("socket connected " + socket);
    console.log("emitting to socket: ",Object.keys(playerData).length)
    socket.emit('liveupdate', packageLiveGames());
    socket.emit('data', playerData);
    socket.emit('lineupdata', lineupData)
    
    
    
    matchupSockets.push(socket);
    
    socket.on('disconnect', function () {
      matchupSockets.splice(matchupSockets.indexOf(socket), 1);
    });
    updateGameClients();
    
  });

function broadcast(event, data) {
  matchupSockets.forEach(function (socket) {
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
    if (callback) callback();
  });
}

function updateLineupData() {
  lineupData = {};
  for (var gameid in liveGames) {
    (function(id) {
      if(liveGames[id].timetag == "hasn't started yet") {
        console.log(id + "hasn't started")
      }
      tools.getLineupData(liveGames[id], function(error, data) {
        if (!lineupData[id]) {
          lineupData[id] = [];
        }
        lineupData[id].push(data);
      })
      
    })(gameid)
  }
  retrieved_lineup_data = true;
}

function updatePlayerData() {
  playerData = {};
  for (var gameid in liveGames) {
    (function(id) {
      if (liveGames[id].timetag == "hasn't started yet") {
        console.log(id + "hasn't started")
        playerData[id] = {error: "game hasn't started"};
        return;
      }
      tools.getPlayerData(liveGames[id], function(error, data) {
        playerData[id] = data;
      });
    })(gameid)
    
    //TODO add sempahore here
  }
  retrieved_player_data = true;
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
  if (games_updating == 0) {
    console.log("broadcasting update");
    broadcast('liveupdate', packageLiveGames());
    if (retrieved_player_data === false) {
      updatePlayerData();
    }
    if (retrieved_lineup_data === false) {
      updateLineupData();
    }
  }
}

function updateGameClients() {
  console.log("updating game clients");
  for (var propertyName in liveGames) {
    broadcast(propertyName + "update", liveGames[propertyName])
  }
}

function packageGameResponse(gameid) {
  //need tagline, relevant players
  var response = {};
  //console.log("response package" + liveGames[gameid])
  return liveGames[gameid];
}

function packageLiveGames() {
  var package = [];
  
  //convert to array
  for (var propertyName in liveGames) {
    //console.log(propertyName);
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

//live game data for front page
setInterval(function() {
  console.log("UPDATING HOME PAGE");
  updateLiveGames();
}, 10000)

updateSchedule(updateLiveGames);

//live game data for games
setInterval(function() {
  console.log("UPDATING GAME PAGES");
  //get map of gameid->teams->players
  updateGameClients();
}, 10000)

