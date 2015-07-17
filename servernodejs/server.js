// Adapted by Giuseppe Futia from the node.js documentation

/*jslint node: true */

"use strict";

var http = require('http');

http.createServer(function (req, res) {
    
    var json,
        body = "";
	
    req.setEncoding('utf8');

    req.on('data', function (data) {
        body += data;
        //console.log('data added');
    });
    
    req.on('end', function () {
        //console.log('req end');
        
        try {
           json = JSON.parse(body);
           
        } catch (e) {
            console.info('Content-Type is not application/json');
            res.writeHead(400, {'Content-Type': 'text/plain'});
            res.end('Error: Invalid Content-Type\n');
            return;
        }
        
        if(json.hasOwnProperty('ip_client') && json.hasOwnProperty('traceroute') && json.hasOwnProperty('reverse') && json.hasOwnProperty('whois') && json.hasOwnProperty('default_nameserver')){
                for(var myKey in json) {
                    if (myKey=="ip_client")
                    {
                         var ip_client=json[myKey][0]["payload"]["address"];
                    } 
             }

            }
            else
            {
                console.info('Incorrect structure for received json');
                res.writeHead(400, {'Content-Type': 'text/plain'});
                res.end('Error: Invalid Content-Type\n');
                return;
            }
        
        var d = new Date().getTime();
        var fs = require('fs');
        var dir = './'+ ip_client;
        if (!fs.existsSync(dir)){
            fs.mkdirSync(dir);
        }
        fs.writeFile(dir+'/'+d, JSON.stringify(json, null, 4), function(err) {
            if(err) {
                return console.log(err);
            }

            console.log("The file is saved!");
        });
        
        console.info("Sending data");
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(body);
    });
}).listen(5000);

console.info('Server running at http://localhost:5000/');
