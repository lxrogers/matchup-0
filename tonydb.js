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
    db.any("SELECT * FROM player_data WHERE first_last in ($1^);", pgp.as.csv(player_names)).then(function (data) {
        //do stuff to data
        callback('success', indexBy(data, 'first_last'));
    })
    .catch(function (error) {
        console.log("Error: " + error)
        // error;
    });
}
//this could be in my file
var todays_players = ["Dwyane Wade", "LeBron James", "Kevin Durant"];

exports.getPlayerData(todays_players, printData)
pgp.end();
