// script that pulls from sources
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

var getJSON = function(url, callback) {
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

getJSON("http://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear=2015-16",
function(err, data) {
  if (err != null) {
    console.log("Something went wrong: " + err);
  } else {
      console.log(JSON.parse(data)['resultSets']);
  }
});