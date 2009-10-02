
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

