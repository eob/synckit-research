<!DOCTYPE html>
<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    // console.info("Page Loaded");
    window.synckit = create_synckit(); 
    var endpoint = "/blog/entries";

    var viewspec = {
        "vshash": "3c9977be25383449119b351ce5388e81",
        "syncspec": {
             "limit": 10,
             "__type": "queue",
             "order": "ASC",
             "sortfield": "date"
            }, 
        "schema": ["id serial", "author integer", "title varchar(200)", "contents text", "date timestamp with time zone"]
    };

    window.synckit.build_view(endpoint, "Posts", viewspec);

    // 'now' is a parameter used for time-travel through the posts
    var extra_view_params = {};
    var now = urlParam('now');
	if (now != 'undefined') {
	    extra_view_params.Posts = {"now": now};
	}
    
    var callback = function() {
        window.synckit.timeStart("template");
		$('#newtemplate').render_new();
	    window.synckit._templateTime = window.synckit.timeEnd("template");;
        if (parent.LogData != "undefined") {
        	parent.LogData("Blog", "Sync Kit", window.location.href, JSON.stringify(window.synckit._queryParams), window.synckit);
        }
    };

    window.synckit.sync(endpoint, ["Posts"], extra_view_params, {}, callback);
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

<table id="newtemplate" query="SELECT * From sk_Posts1 LIMIT 10;" as="entry">
	<tr itemscope="yes" itemtype="Entry" />
		<td><span itemprop="title">from</span></td>
		<td><span itemprop="contents">content</span></td>
	</tr>
</table>

</body>

</html>
