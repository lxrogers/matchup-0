var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
var time = require('./time');

var exports = module.exports = {};

exports.newFunction = function(param1, param2) {
  
}

exports.get = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("get", url, true);
    xhr.responseType = "json";
    xhr.onload = function() {
      var status = xhr.status;
      if (status == 200) {
        callback(null, xhr.responseText);
      } else {
        callback(status);
      }
    };
    xhr.send();
};


/* -------------------- API HELPER FUNCTIONS ----------------------- */
/*
 *
 * Schedule
 *    -> Schedule Games []
 *      -> Schedule Game
 *        -> gameID, startDate, endDate, etc.
 */
function getSIGameDetailsUrl(gameID) {
    return 'http://www.si.com/pbp/liveupdate?json=1&sport=basketball%2Fnba&id=' +
            gameID + '&box=true&pbp=true&linescore=true';
}

function getSIGameScheduleUrl(date) {
    return "http://www.si.com/pbp/liveupdate?sport=NBA&date=" +
    getTodayDateString(date) + "&pbp=false&box=false&json=1";
}

function getTodayDateString(d) {
    var dateString = d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
    console.log("datestring", d, dateString);
    return dateString;
}

exports.getSchedule = function(date, callback) {
    var url = getSIGameScheduleUrl(date);
    console.log("getting schedule for " + date)
    exports.get(url, 
    function(err, schedule_data) {
      var schedule = constructSchedule(schedule_data);
      if (callback) 
        callback(err, schedule);
    })
};

function constructSchedule(schedule_data) {
  var schedule_json = JSON.parse(schedule_data);
  var events_data = schedule_json['apiResults'][0]['league']['season']['eventType'][0]['events'];
  
  var schedule = {}
  events_data.forEach(function(event) {
    var scheduleGame = constructScheduleGame(event);
    schedule[scheduleGame.gameID] = scheduleGame;
  })
  
  return schedule;
}

function constructScheduleGame(event_data) {
  var scheduleGame = {
    gameID : event_data['eventId'],
    startDate : event_data['startDate'][0],
    endDate : event_data['startDate'][1],
    teams : event_data['teams'],
    //include some helper functions
  };
  return scheduleGame;
}

/* getSIGameDetails
 * @param gameID: SI GameID
 * @param callback: callback to be performed on entire SI JSON content
 */
exports.getLiveGame = function(gameID, callback) {
    var url = getSIGameDetailsUrl(gameID);
    exports.get(url, function(err, data) {
      if (err) {
        console.log("error: ", err)
      }
      var liveGameJSON = JSON.parse(data);
      var liveGame = constructLiveGame(liveGameJSON);
      if (callback)
        callback(err, liveGame);
    });
};

function constructLiveGame(liveGameJSON) {
  var event_data = liveGameJSON['apiResults'][0]['league']['season']['eventType'][0]['events'][0];
  var liveGame = {
    gameID : event_data['eventId'],
    isActive : event_data['eventStatus'].isActive,
    boxscores : event_data['boxscores'],
    teams : event_data['teams'],
    timetag : time.getTimeTag(event_data['eventStatus']),
    order : getOrder(event_data['eventStatus'], event_data['eventId'])
  };
  return liveGame;
}

function getOrder(status, gameID) {
  if (status.isActive || status.period == 2) 
    return gameID - 10000;
  else
    return gameID;
}

exports.getEasternTimezoneDate = function() {
  var local_date = new Date();
  var local_time = local_date.getTime();
  var local_offset = local_date.getTimezoneOffset() * 60000;
  var utc = local_time + local_offset;
  var offset = -7;
  var et = utc + (3600000*offset);
  return new Date(et);
}