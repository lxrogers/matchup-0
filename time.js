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
    4: "4th",
    5: "OT1",
    6: "OT2",
    7: "OT3",
    8: "OT4"
}

var INACTIVE_QUARTERS = {
  1: "End First",
  2: "Halftime",
  3: "End Third",
  4: "End Fourth",
  5: "End OT1",
  6: "End OT2",
  7: "End OT3",
  8: "End OT4",
}

exports.getTimeTag = function(event_status_json) {
  var name = QUARTER_TO_NAME[event_status_json.period];
  if (!event_status_json.isActive) {
     return INACTIVE_QUARTERS[event_status_json.period];
  }
  if (event_status_json.name != "In-Progress") {
    return "final"
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