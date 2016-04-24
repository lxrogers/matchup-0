var exports = module.exports = {};

/* getTimeOffset
 * @param venue: venue name
 */
var VENUE_TO_OFFSET = {
    "Barclays Center": -5
}
exports.getTimeOffset = function(venue) {
    return VENUE_TO_OFFSET[venue];
}

var QUARTER_TO_NAME = {
    1: "1st",
    2: "2nd",
    3: "3rd",
    4: "4th"
}

exports.getTimeTag = function(event_status_json) {
  var name = QUARTER_TO_NAME[event_status_json.period];
  if (!event_status_json.isActive) {
      if (event_status_json.period == 4)
        return "final";
      else if (event_status_json.period == 2)
        return "halftime";
      else
        return "hasn't started yet";
  }
  if (isEndOfQuarter(event_status_json)) {
      return "End Of " + name;
  }
  else {
      return name + " - " + getTime(event_status_json);
  }
}

function getTime(event_status_json) {
    return "" + event_status_json.minutes + ":" + event_status_json.seconds;
}

function isEndOfQuarter(event_status_json) {
    return (event_status_json.minHeight == 0 && event_status_json.seconds == 0)
}