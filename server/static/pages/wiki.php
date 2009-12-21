<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    // console.info("Page Loaded");
    window.db = create_synckit();
    $('#debug').append("loading");
    /*
     * TODO: Actively set client schema instead of lazily doing it on server respnse.
     */
    
    /*
     * remove_views describes the server-generated managed data structures that are 
     * exported to the client. Each one is a table, but a table that is accessed (and thus synced)
     * in a particular way.  
     */
	var pageid = urlParam('pageid');
	var latency = urlParam('latency');
	var bandwidth = urlParam('bandwidth');
	
    var remote_views = {
      "Pages":{
		"type":"set",
		"style":"open"
      }
    };

	if (pageid != 0) {
		remote_views["Pages"]["filter"] = pageid;
	}
		
	var schema = {"Pages":["id integer NOT NULL PRIMARY KEY",
	              		   "title varchar(255)", 
	              		   "contents text", 
						   "weight float",
	              		   "date datetime NOT NULL"]
    };
    
    /*
     * The state represents what elements from the remove_views that the client has, so that the
     * server will not waste resources duplicating information.
     */
    var state = window.db.get_state(schema, remote_views);   
    var now = urlParam('now');
	
	if (now != 'undefined') {
		for (var table in state) {
			state[table]['now'] = now;
		}		
	}

	var endpoint = null;
	var params = null;
	
	var callback = function(data) {
		var endTime = (new Date).getTime();
        var dataTime = endTime - dataStart;

    // console.info("Server Response");
        // console.info(JSON.stringify(data));    
	    var bulkloadStart = (new Date).getTime();
		if (data) {
	        window.db.bulkload(data);			
		}
		endTime = (new Date).getTime();
        var bulkloadTime = endTime - bulkloadStart;

	      $('#newtemplate').attr('query', 'SELECT * from Pages WHERE id = ' + pageid + ';');
	  	  var templateStart = (new Date).getTime();
		  $('#newtemplate').render_new();
		  endTime = (new Date).getTime();
		
		
	      var templateTime = endTime - templateStart;

		  if (parent.LogData) {
			if (endpoint == null) {
				// We didn't hit the server
				parent.LogData("synckit", "CACHED", "CACHED", 0, 0, templateTime);
			}
			else {
				parent.LogData("synckit", window.location.href, JSON.stringify(params), dataTime, bulkloadTime, templateTime);
			}
		  }
	}

    // var state = {};
	
	if (state["Pages"]) {
	    endpoint = "/wiki/synckit";	
	    params = {"queries":JSON.stringify(state), "latency":latency, "bandwidth":bandwidth};    
	    var dataStart = (new Date).getTime();

	    $.post(endpoint, params, callback, "json");		
	}
	else {
		var dataStart = (new Date).getTime();
	    callback.call(null);
	}
    
});

</script>
</head>
<body>  
    
<div id="loading">
    <button id="clearButton" onclick="window.db.reset();">Reset DB</button><button onclick="window.db.dump();">Dump DB</button>
</div>

<div id="debug">
</div>
<div id="templated">
<p align="center"><b>Template Loading..!</b></p>
</div>

<table id="newtemplate" query="" as="entry">
	<tr itemscope="yes" itemtype="Entry" />
		<td><span itemprop="title">from</span></td>
		<td><span itemprop="contents">content</span></td>
	</tr>
</table>

</body>

</html>
