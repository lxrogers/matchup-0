var courtVis = {};

courtVis.defaultCourt = function(nrows, ncols) {
	var court = [];
  for (var i = 0; i < nrows; i++) {
    var row = [];
    for (var j = 0; j < ncols; j++) {
      row.push("x");
    }
    court.push(row)
  }
  return court;
}
var POSITIONS = {
	0: 'CENTER',
	1: 'FORWARD',
	2: 'GUARD'
}

var POSITION_MAP = {
	"Center": "CENTER",
	"Center-Forward": "CENTER",
	"Center-Guard" : "CENTER",
	"Forward": "FORWARD",
	"Forward-Center": "FORWARD",
	"Forward-Guard": "FORWARD",
	"Guard" : "GUARD",
	"Guard-Forward": "GUARD",
	"Guard-Center" : "GUARD",
	"" : "GUARD"
}

function classifyPlayer(player, playerData) {
	var key = player.firstName + " " + player.lastName;
	return POSITION_MAP[playerData[key]['position']]
}

function getTeamPositions(teams, playerData) {
	var team_positions = [];
	for (var i = 0; i < 2; i++) {
		var team = teams[i];
		var positions = {'CENTER': [], 'FORWARD': [], 'GUARD': []};
		for (var playerKey in team) {
			var player = team[playerKey];
			
			var position = classifyPlayer(player, playerData);
			positions[position].push(player);	
		}
		team_positions.push(positions);
	}
	return(team_positions);
}

function constructCourt() {
	var court = [];
  for (var i = 0; i < 5; i++) {
    var row = [];
    for (var j = 0; j < 8; j++) {
      row.push("");
    }
    court.push(row);
  }
  return court;
}

function fillPosition(position) {
	console.log("filling ", position)
	if (position.length == 0) {
		return ["","","","",""]
	}
	else if (position.length == 1) {
		return ["","",position[0], "",""];
	}
	else if (position.length == 2) {
		return ["",position[0], "", position[1], ""]
	}
	else if (position.length == 3) {
		return [position[0], "",  position[1], "", position[2]]
	}
	else if (position.length == 4) {
		return [position[1], position[2], position[3], position[4], ""]
	}
	else if (position.length == 5) {
		return position;
	}
}

function fillCourt(team_positions) {
	var court = constructCourt()
	
	for (var c = 0; c < 3; c++) {
		var position_name = POSITIONS[c];
		var column = fillPosition(team_positions[0][position_name])
		for (var r = 0; r < 5; r++) {
			court[r][c] = column[r];
		}
	}
	for (var c = 7; c > 4; c--) {
		var position_name = POSITIONS[7 - c]
		var column = fillPosition(team_positions[1][position_name])
		for (var r = 0; r < 5; r++) {
			court[r][c] = column[r];
		}
	}
	return court;
}

function annotatePlayer(player, playerData) {
	var player_key = player.firstName + " " + player.lastName;
	var annotation = {
		"tag": player.firstName.substr(0,1) + '. ' + player.lastName,
		"name" : player_key,
		"position": playerData[player_key]['position'],
		"data" : playerData[player_key]
	}
	return annotation;
}

function annotateCourt(filled_court, playerData) {
	var annotated_court = constructCourt();
	for (var r = 0; r < 5; r++) {
		for (var c = 0; c < 8; c++) {
			var player = filled_court[r][c];
			if (player != "" && typeof(player) != 'undefined') {
				console.log(player)
				var annotation = annotatePlayer(player, playerData);
				
				
				annotated_court[r][c] = annotation;//player.firstName.substr(0,1) + '. ' + player.lastName + '\n' + p;
			}
		}
	}
	return annotated_court;
}

courtVis.updateCourt = function(teams, playerData) {
	var team_positions = getTeamPositions(teams, playerData);
	var filled_court = fillCourt(team_positions);
	
	return annotateCourt(filled_court, playerData);
	//console.log("positions: ", team_positions)
	
}