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
        "vshash": "92ec2eb0d74d31ee0ca0763c2e52f7fa",
        "syncspec": {
            "limit": 10, 
            "__type": "queue",
            "order": "ASC", 
            "sortfield": "date"
        }, 
        "schema": ["id integer", "author integer", "title varchar(200)", "contents text", "date datetime"]
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
        	parent.LogData("Blog", "Sync Kit", window.location.href, JSON.stringify(params));
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
