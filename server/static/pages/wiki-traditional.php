<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
    window.synckit = create_synckit();
	var callback = function(data) {
        if (parent.LogData != "undefined") {
            parent.LogData("Wiki", "Traditional", window.location.href, window.synckit);
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
