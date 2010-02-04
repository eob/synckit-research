<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    window.synckit = create_synckit();
	var callback = function(data) {
        if (parent.LogData != "undefined") {
            var x = "";
            // the x arg used to be: JSON.stringify(params, synckit)
            	parent.LogData("Blog", "Traditional", window.location.href, x, window.synckit);
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
    