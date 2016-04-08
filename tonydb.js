var pg = require('pg-promise');

var exports = module.exports = {};

exports.newFunction = function(param1, param2) {
  
}

//something like this:
//I will know which players are on the court (name or SI id)
// and I'll want to find out other things about that player
// or lineup

//server might request all of the data for that day

function regularFunction(param1, param2) {
    
}

//getPlayerData: get all of the relevant data for 
// @param players: list of players
// return some type of map player key -> array of data
exports.getPlayerData = function(players) {
    //format request string
    //send postgres request
    //format results into object similar to below
    var results = {
        "Anthony Davis" : {
            "height": "6 8",
            "shoes" : "nike"
        },
        "Player 2": {
            "height": "6 8",
            "shoes" : "nike"
        }
        //...
    }
    return results;
}

var map = {};