<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
	var callback = function(data) {
        if (parent.LogData != "undefined") {
            	parent.LogData("Blog", "Traditional", window.location.href, JSON.stringify(params));
        }	      
	}
   callback.call(null);    
});
</script>
</head>
<body>                
   
    
<div id="loading">
    <button onclick="">----</button><button onclick="">------</button>
</div>

<div id="debug">
</div>
<p align="center"><b>--- Loading...</b></p>
    <ul>
	<div class="entry">
	</div>
		
 {% block content %}{% endblock %}
<!-- end post -->
    </ul>
</body>
</html>
