<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
function replacementFieldByName(name) {
	if (name == "title") {
		return 1;
	}
	else if (name == "contents") {
		return 2;
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
	var pageid = urlParam('pageid');
	
    var remote_views = {
      "Pages":{
		"type":"set",
		"style":"open"
      }
    };

	// if (pageid != 0) {
	// 	remote_views["Pages"]["filter"] = pageid
	// }
	
	// // var schema = {"Pages":["id integer NOT NULL PRIMARY KEY",
	// //               		   "title varchar(255)", 
	// //               		   "contents text", 
	// // 					   "weight float",
	// //               		   "date datetime NOT NULL"]
	//     };
    
    /*
     * The state represents what elements from the remove_views that the client has, so that the
     * server will not waste resources duplicating information.
     */
    // var state = window.synckit.get_state(schema, remote_views);   
	var state = {"Pages":{"filter":[pageid]}};

    var now = urlParam('now');
	
	if (now != 'undefined') {
		for (var table in state) {
			state[table]['now'] = now;
		}		
	}

    endpoint = "/wiki/tokyo";
	var params = {"queries":JSON.stringify(state)};    
	
	var callback = function(data) {
	    window.synckit._dataTransferTime = window.synckit.timeEnd("dataFetch");;
        window.synckit.timeStart("template");
        $('#newtemplate').render_flying(data["Pages"]["results"]);
        window.synckit._templateTime = window.synckit.timeEnd("template");
        window.synckit._queryParams = params;
        if (parent.LogData != "undefined") {
            	parent.LogData("Wiki", "Flying Templates", window.location.href, window.synckit);
        }	      
	}

    window.synckit.timeStart("dataFetch");
    $.post(endpoint, params, callback, "json");		
    
});

</script>
</head>
<body>  
    
<div id="loading">
    <button id="clearButton" onclick="window.synckit.reset();">Reset DB</button><button onclick="window.synckit.dump();">Dump DB</button>
</div>

<div id="debug">
</div>
<div id="templated">
<p align="center"><b>Template Loading...</b></p>
</div>

<table id="newtemplate" query="" as="entry">
	<tr itemscope="yes" itemtype="Entry" />
		<td><span itemprop="title">from</span></td>
		<td><span itemprop="contents">content</span></td>
	</tr>
</table>

</body>

</html>
