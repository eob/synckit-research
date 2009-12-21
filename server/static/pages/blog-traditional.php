<html>
<head>
<?php include "synckit-header.php" ?>
<script>
$(function() {
	var callback = function(data) {
		  if (parent.LogData) {
			parent.LogData("traditional-blog-test-load", "TRAD", "TRAD", 0, 0, 0);
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
		
<!-- end post -->
    </ul>
</body>
</html>
