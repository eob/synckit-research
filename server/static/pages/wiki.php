<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    // console.info("Page Loaded");
    window.synckit = create_synckit();
	var endpoint = "/wiki/synckit";	
     
    var viewspec = {
        "vshash": "4398b2b55a17d6cc99c5da03f1832a56",
        "syncspec": {
            "idfield": "id",
            "__type": "set"
        },
        "schema": ["id serial", "title text", "contents text", "access_probability double precision", "date timestamp with time zone"]
    };

    window.synckit.build_view(endpoint, "Pages", viewspec);
	
    
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
        window.synckit.timeStart("template");
	      $('#newtemplate').attr('query', 'SELECT * from sk_Pages1 WHERE id = ' + pageid + ';');
		  $('#newtemplate').render_new();
    	  window.synckit._templateTime = window.synckit.timeEnd("template");;
          if (parent.LogData != "undefined") {
              	parent.LogData("Wiki", "Sync Kit", window.location.href, JSON.stringify(window.synckit._queryParams), window.synckit);
          }
	}

    window.synckit.sync(endpoint, ["Pages"], extra_view_params, extra_query_params, callback); 
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
