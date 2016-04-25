var gameTools = {};

gameTools.getStatHeaders = function(playerData) {
	var firstKey = Object.keys(playerData)[0]
	var headers = [];
  for (var propertyName in playerData[firstKey]) {
    headers.push({name: propertyName, value: propertyName})
  }
  return headers;
}

gameTools.getOnCourtPlayers = function(team) {
	var on_court_players = [];
	for (var player_key in team['boxscore'].playerstats) {
    var player = team['boxscore'].playerstats[player_key]
    
    if (player.onCourt == "true") {
      on_court_players.push(player.player)
    }
  }
  return on_court_players;
}

function getLineupKey(players) {
  var formatted_player_arr = []
  for (var key in players) {
      formatted_player_arr.push([players[key].lastName, players[key].firstName].join(','))
  }
  formatted_player_arr = formatted_player_arr.sort()
  return formatted_player_arr.join(' - ')
}

gameTools.getLineupKeys = function(teams) {
  var keys = [];
  for (var team_key in teams) {
    var team = teams[team_key];
    var on_court_players = gameTools.getOnCourtPlayers(team);
    var key = getLineupKey(on_court_players)
    keys.push(key);
  }
  return keys;
}