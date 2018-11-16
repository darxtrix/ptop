const http = require('http');
const fs = require('fs');
const mongoose = require('mongoose');
const url = require('url');

const ptopVersion = fs.readFileSync('./VERSION');

mongoose.connect(`mongodb://${process.env.DB_USER}:${process.env.DB_PASSWORD}@${process.env.DB_URL}`)

var db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function() {
  console.log("Connected to database");
});

 
const TelemetrySchema = new mongoose.Schema({
  author: mongoose.Schema.ObjectId,
  ip: String,
  os_name: String,
  date: Date,
  version: String
});

const TelemetryModel = mongoose.model('Telemetry',TelemetrySchema);

http.createServer(function (req, res) {
	var query = url.parse(req.url,true).query;
	// prevent rouge enteries
	if ( query['os_name'] ) {
		const entry = new TelemetryModel({ip: req.headers['x-forwarded-for'] || req.connection.remoteAddress, os_name: query['os_name'], version: query['version'], date: new Date()});
		entry.save();
		console.log(`Successfuly added ${JSON.stringify(entry)} to the database`);
	}
	res.write(ptopVersion); 
	res.end(); 
}).listen(8003, function(){
 	console.log("Started telemetry server at 80"); 
});