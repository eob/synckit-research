<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    // console.info("Page Loaded");
    window.db = create_synckit();
	var endpoint = "/wiki/synckit";	
     
    var viewspec = {
        "vshash": "435836f4ea590bd397a6d6ce9784fd5d",
        "syncspec": {
            "idfield": "id",
            "__type": "set"
        },
        "schema": ["id integer", "title text", "contents text", "access_probability real", "date datetime"]
    };
    window.db.build_view(endpoint, "Pages", viewspec);
	
    
	var latency = urlParam('latency');
	var bandwidth = urlParam('bandwidth');
	var pageid = urlParam('pageid');
    var now = urlParam('now');
    var extra_view_params = {};
	if (pageid != 0) {
		extra_view_params.filter = pageid;
	}	
	if (now != 'undefined') {
	    extra_view_params.now = now;
    }
    extra_view_params = {"Pages" : extra_view_params};
    extra_query_params = {"latency" : latency, "bandwidth" : bandwidth};

	var callback = function(data) {
        window.db.startTime("template");
	      $('#newtemplate').attr('query', 'SELECT * from sk_Pages1 WHERE id = ' + pageid + ';');
		  $('#newtemplate').render_new();
    	  window.db._templateTime = window.db.endTime("template");;
          if (parent.LogData != "undefined") {
              	parent.LogData("Wiki", "Sync Kit", window.location.href, JSON.stringify(params));
          }
	}

    window.db.sync(endpoint, ["Pages"], extra_view_params, extra_query_params, callback); 
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
