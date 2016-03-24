// Loading and initializing the library:

// schema and test with a few data points
var connection_options = {
    host: 'localhost', // server name or IP address;
    port: 5432,
    database: 'development',
    user: 'postgres',
    password: 'steph43'
};

var pgp = require('pg-promise')({});

var db = pgp(connection_options);

db.none('CREATE TABLE players(' +
    'id SERIAL PRIMARY KEY,'+
    'name VARCHAR(40) not null,'+
    'height real not null'+
    ')').then(function (data) {
        // success;
    })
    .catch(function (error) {
        console.log("error:" + error);
    });