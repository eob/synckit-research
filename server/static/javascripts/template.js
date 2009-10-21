
jQuery.fn.template = function(value) {
	if (value === undefined) {
    	return this.data("backstage_template");        
    }
    else {
        this.data("backstage_template", value);
        return this;
    }
};

jQuery.fn.templateData = function(value) {
	if (value === undefined) {
    	return this.data("backstage_templateData");        
    }
    else {
        this.data("backstage_templateData", value);
        return this;
    }
};

jQuery.fn.render = function() {
	console.time("Rendering Template");
    var templateString = this.template();
    var value = this.templateData();
    var template = jsontemplate.Template(templateString);
    // console.log("Template Size: " + templateString.length);
    // console.log(value);
    var rendered = template.expand(value);
    // console.log("Rendered Size: " + rendered.length);
    this.html(rendered);
	console.timeEnd("Rendering Template");
}

jQuery.fn.render_new = function() {
	console.time("Rendering SQL Template");
	var query = this.attr('query');
	var templates = this.find("[itemscope]");
	var res = window.db.execute(query);
	var map = {};
	
	
	while (res.isValidRow()) {
		// Loop over each item to do
		templates.each(function(i) {
			jQuery(this).find("[itemprop]").each(function(j) {
				var prop = jQuery(this).attr("itemprop");
				var val = res.fieldByName(prop);
				jQuery(this).html(val);
			});
			jQuery(this).before(jQuery(this).clone());
		});
		res.next();
    }

	templates.each(function(i) {
		jQuery(this).remove();
	});

		console.timeEnd("Rendering SQL Template");
}

