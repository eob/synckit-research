<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    // console.info("Page Loaded");
    window.db = create_synckit();
    
    /*
     * TODO: Actively set client schema instead of lazily doing it on server respnse.
     */
    
    /*
     * remove_views describes the server-generated managed data structures that are 
     * exported to the client. Each one is a table, but a table that is accessed (and thus synced)
     * in a particular way.  
     */
    var remote_views = {
      "Posts":{
        "type":"queue",
        "field":"date",
        "order":"ASC"
      }
    };

	var schema = {"Posts":["id integer NOT NULL PRIMARY KEY",
	              		   "author varchar(200) NOT NULL", 
	              		   "title text NOT NULL", 
	              		   "content varchar(200)", 
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

    // var state = {};
    var endpoint = "/blog/entries";
    var params = {"queries":JSON.stringify(state)};   
    parent.LogData("test_dom_load_time", "test-dom-load-time", JSON.stringify(params), 0, 0, 0);
	
	var foo = function() {
    $.post(endpoint, params, function(data) {
		var endTime = (new Date).getTime();
        var dataTime = endTime - dataStart;
	    var bulkloadStart = (new Date).getTime();
        window.db.bulkload(data);
		endTime = (new Date).getTime();
        var bulkloadTime = endTime - bulkloadStart;
	      var templateStart = (new Date).getTime();
		  $('#newtemplate').render_new();
		  endTime = (new Date).getTime();
	      var templateTime = endTime - templateStart;
	      
		  if (parent.LogData != "undefined") {
			parent.LogData("synckit-blog", window.location.href, JSON.stringify(params), dataTime, bulkloadTime, templateTime);
		  }
    }, "json");
	};
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
<p align="center"><b>Template Loading...</b></p>
</div>

<table id="newtemplate" query="SELECT * From Posts LIMIT 10;" as="entry">
	<tr itemscope="yes" itemtype="Entry" />
		<td><span itemprop="title">from</span></td>
		<td><span itemprop="content">content</span></td>
	</tr>
</table>

</body>

</html>
