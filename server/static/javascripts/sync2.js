

function databaseNameFromUrl(url) {
    var local = url.slice(url.lastIndexOf('/') + 1);
    local = local.slice(0,local.indexOf('.'));
    return local;
}

function tableExists(table) {
    var result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", [table]);
    return result.isValidRow();
}

function resetDatabase() {
    db.remove();
    db.open('backstage');
}

function render() {
    alert('render!');
}

jQuery.fn.templateRemote = function(link) {
	var me = this;
    console.time("Fetching Remote Template");
	$.get(link, function(data) {
	    console.timeEnd("Fetching Remote Template");
	    try {
            $(me).template(data);
        }
        catch(err) {
            alert(err.message);
        }
	});
}

jQuery.fn.template = function(value) {
	if (value === undefined) {
    	return this.data("backstage_template");        
    }
    else {
        this.data("backstage_template", value);
        if (this.templateData() != undefined) {
            this.renderTemplate();
        }
        return this;
    }
};

jQuery.fn.templateData = function(value) {
	if (value === undefined) {
    	return this.data("backstage_templateData");        
    }
    else {
        this.data("backstage_templateData", value);
        if (this.template() != undefined) {
            this.renderTemplate();
        }
        return this;
    }
};

jQuery.fn.queryLocal = function(datasource, dataset, query) {
	// First download any data source we don't already have
	window.numberToGo = 0; // HACK HACK HACK
	var hadToLoad = 0;
	var me = this;
		
	var datasources = dataset.split(",");
	for (var i=0; i<datasources.length; i++) {
	    var datasource = databaseNameFromUrl(datasources[i]);
		if (! tableExists(datasource)) {
			console.time("Bulkloading Dataset " + datasources[i]);
			numberToGo++;
			hadToLoad++;
			$.get(datasources[i],
				function(data){
					console.timeEnd("Bulkloading Dataset " + this.url);
					try {
					    bulkload(this.url, data);					
				        numberToGo--;
				        if (numberToGo == 0) {
				            // We've bulkloaded everything. Now really render local
				            $(me).reallyQueryLocal(datasource, dataset, query);
				        }
			        }
			        catch(err) {
			            alert(err.message);
			        }
				}
			);
		}
	}

	// OK. Now we've got the
	if (hadToLoad == 0) {
        $(me).reallyQueryLocal(datasource, dataset, query);	    
	} 
}

jQuery.fn.reallyQueryLocal = function(datasource, dataset, query) {
    // Query the database.
    console.time("Querying Local Database: " + query);
    var result = db.execute(query);
    var me = this;
    
    // This is going to hurt in performance time
    var rows = new Array();
    var fields = new Array();
    
    if (result.isValidRow()) {
        for (var i=0; i<result.fieldCount(); i++) {
            fields[i] = result.fieldName(i);
        }
    }

    var j=0;
    while (result.isValidRow()) {
      var row = {};
      for (var i=0; i<result.fieldCount(); i++) {
          row[fields[i]] = result.field(i);
      }
      rows[j] = row;
      result.next();
      j++;
    }
    result.close();
    var json = {'query':rows};
    console.timeEnd("Querying Local Database: " + query);
    $(me).templateData(json);        
}

jQuery.fn.queryRemote = function(url) {
	var me = this;
	var label = $('#label').val();
	console.time("Query Remote Database");
	$.getJSON(
		url,
		{
		    "label":label
		},
		function(data){
			console.timeEnd("Query Remote Database");
			try {
				$(me).templateData(data);				    
			}
			catch(err) {
			    alert(err.message);
			}
		}
	);		
}

jQuery.fn.renderTemplate = function() {
	console.time("Rendering Template");
    var templateString = this.template();
    var value = this.templateData();
    var template = jsontemplate.Template(templateString);
	console.log("Template Size: " + templateString.length);
	console.log(value);
    var rendered = template.expand(value);
	console.log("Rendered Size: " + rendered.length);
    this.html(rendered);
	console.timeEnd("Rendering Template");
}

function mergeTemplates() {
    try {
        window.db = google.gears.factory.create('beta.database');
        db.open('backstage');
        $("[datasource]").each(function(i) {
            $(this).templateRemote($(this).attr('template'));
            $(this).queryRemote($(this).attr('datasource'), $(this).attr('dataset'), $(this).attr('query'));
        });
    }
    catch(err) {
        alert(err.message);
    }
}
