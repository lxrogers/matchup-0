var pgp = require('pg-promise')();

var cn = {
    host: 'localhost', // server name or IP address; 
    port: 5432,
    database: 'development',
    user: 'postgres',
    password: 'steph43'
};

var db = pgp(cn);

var exports = module.exports = {};

function printData(error, data) {
    console.log("LAWRENCE CALLBACK: ")
    console.log(data);
}

//something like this:
//I will know which players are on the court (name or SI id)
// and I'll want to find out other things about that player
// or lineup

//server might request all of the data for that day
var indexBy = function(array, property) {
  var results = {};
  (array||[]).forEach(function(object) {
    results[object[property]] = object;
  });
  return results
};

exports.getPlayerData = function(player_names, callback) {
    // make request to db
    // store answer
    // call callback function on answer
    //callback(data);
    db.any("SELECT * FROM player_data WHERE first_last in ($1:csv);", player_names).then(function (data) {
        //do stuff to data
        callback('success', indexBy(data, 'first_last'));
    })
    .catch(function (error) {
        console.log("Error: " + error)
        // error;
    });
}

// Team name format is "City Nickname"
exports.getLineupDataForTeam = function(team_name, callback) {
    // create map of key: lineup data
    db.any("SELECT a.* FROM lineup_traditional_stats a JOIN team_overview b ON a.team_id = b.team_id WHERE b.team_name = $1", team_name).then(function (data) {
        callback('success', indexBy(data, 'group_name'))
    })
    .catch(function (error) {
        console.log("Error: " + error)
        // error;
    });
}

var test_players = [
    {
        firstName: 'Goran',
        lastName: 'Dragic'
    },
    {
        firstName: 'Luol',
        lastName: 'Deng'
    },
    {
        firstName: 'Josh',
        lastName: 'Richardson'
    },
    {
        firstName: "Hassan",
        lastName: "Whiteside"
    },
    {
        firstName: "Justise",
        lastName: "Winslow"
    }
];

// takes in player object
exports.getLineupKey = function(players) {
    var formatted_player_arr = []
    for (var key in players) {
        formatted_player_arr.push([players[key].lastName, players[key].firstName].join(','))
    }
    formatted_player_arr = formatted_player_arr.sort()
    return formatted_player_arr.join(' - ')
    // return key string
}

//this could be in my file
var todays_players = ["Dwyane Wade", "LeBron James", "Kevin Durant"];

exports.getLineupDataForTeam("Miami Heat", function(error, data) {
    var key = exports.getLineupKey(test_players)
    console.log(data[key])  
})

exports.getPlayerData(todays_players, printData)


pgp.end();
