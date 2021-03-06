<html>
<head>
<?php include "synckit-header.php" ?>
<script>
function replacementFieldByName(name) {
	if (name == "id") {
		return 0;
	}
	if (name == "title") {
		return 2;
	}
	else if (name == "author") {
		return 1;
	}
	else if (name == "content") {
		return 3;
	}
}

$(function() {
    // console.info("Page Loaded");
    window.synckit = create_synckit();
    
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

//	var schema = {"Posts":["id integer NOT NULL PRIMARY KEY",
//	              		   "author varchar(200) NOT NULL", 
//	              		   "title text NOT NULL", 
//	              		   "content varchar(200)", 
//	              		   "date datetime NOT NULL"]
//	              };
    
    /*
     * The state represents what elements from the remove_views that the client has, so that the
     * server will not waste resources duplicating information.
     */
    //var state = window.synckit.get_state(schema, remote_views);   
         
    // var state = {};
    var endpoint = "/blog/flying_entries";
	var state = {"Posts":{}};
    var now = urlParam('now');
	if (now != 'undefined') {
		for (var table in state) {
			state[table]['now'] = now;
		}		
	}

    var params = {"queries":JSON.stringify(state)};    

    window.synckit.timeStart("dataFetch");
    $.post(endpoint, params, function(data) {
	    window.synckit._dataTransferTime = window.synckit.timeEnd("dataFetch");;
        window.synckit.timeStart("template");
        $('#newtemplate').render_flying(data["Posts"]["results"]);
        window.synckit._templateTime = window.synckit.timeEnd("template");;
        window.synckit._queryParams = params;
        if (parent.LogData != "undefined") {
            	parent.LogData("Blog", "Flying Templates", window.location.href, window.synckit);
        }	      
    }, "json");
    
});
</script>
</head>
<body>
    
    
<div id="loading">
    <button onclick=";">--(no op)--</button><button onclick="">--(no op)--</button>
</div>

<div id="debug">
</div>
<div id="templated">
<p align="center"><b>FLYING TEMPLATES</b></p>
</div>

<table id="newtemplate" query="SELECT * From Posts LIMIT 10;" as="entry">
	<tr itemscope="yes" itemtype="Entry" />
		<td><span itemprop="title">from</span></td>
		<td><span itemprop="content">content</span></td>
	</tr>
</table>

</body>

</html>
