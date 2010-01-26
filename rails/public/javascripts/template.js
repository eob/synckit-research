_dataIterator = function(data, type) {

    // Error Check -- Make sure 'new' keyword was used
    // ----------------------------------------------------------------
    if ( !(this instanceof _dataIterator) ) 
       return new _dataIterator(data, type);
       
    // Member Variables
    // ----------------------------------------------------------------
    this._type = type;
    this._data = data;

    // Methods
    // ----------------------------------------------------------------
    this.rowIsValid = function() {
        if (this._type == "JS") {
            return (this._index < this._data.length);            
        }
    };
    
    this.advance = function() {
        if (this._type == "JS") {
            this._index = this._index + 1;            
        }        
    };

    this.currentRow = function() {
        if (this._type == "JS") {
            return this._data[this._index];            
        }
    };

    this.currentRowValueForName = function(name) {
        if (this._type == "JS") {
            return this._data[this._index][name];            
        }
    };
    
    // Initialization
    // ----------------------------------------------------------------
    if (this._type == "JS") {
        this._index = -1;
    }
    this.advance();
    
    
};

function gatherTemplateTree(node) {
    var itemType = jQuery(node).attr("itemtype");
    var kids = new Array();
    
    jQuery(node).children().each(function (j) {
        var retArr = gatherTemplateTree(this);
        if (retArr != null) {
            kids.push(retArr);
        }
    });
    
    if (kids.length == 0) {
        // No children had templates
        if (itemType) {
            return node;
        }
        else {
            // This one isn't either
            return null;
        }
    }
    else {
        // Children had templates
        if (itemType) {
            return {"p":node, "c":kids};
        }
        else {
            if (kids.length > 1) {
                return kids;
            }
            else {
                return kids[0];
            }
        }
    }
}

function dataForSource(source) {
    var type = null;
    if (source.indexOf("SQL:") == 0) {
        type = "SQL";
        source = source.substring(4);
    }
    else if (source.indexOf("JS:") == 0) {
        type = "JS";
        source = source.substring(3);        
    }

    // Now do it
    if (type == "SQL") {
        return null;
        //return window.db.execute(query);
        return null;
    }
    else if (type == "JS") {
        return new _dataIterator(eval(source), type);
    }
}

function renderTree(tree, data_sources, state) {
    if (tree instanceof Array) {
        jQuery.each(tree, function(key, value) {
            renderTree(value, data_sources, state);
        });
    }
    else if ((tree instanceof Object) && (! tree.nodeName)) {
        state = renderElement(tree["p"], data_sources, state)
        renderTree(tree["c"], data_sources, state);                
    }
    else {
        renderElement(tree, data_sources, state);        
    }
}

function renderElement(item, data_sources, state) {
    // Get the thing for this item
    var iterator_name = jQuery(item).attr('itemtype');
    // FIX FIX FIX
    var iterator = data_sources[iterator_name];
    if (iterator == null) {
        console.error("Iterator was null for item " + iterator_name);
        return;
    }

    var t = jQuery(item).clone();
    jQuery(item).html("");
    while (iterator.rowIsValid()) {
        var rendered = t.clone();
        rendered.find("[itemprop]").each(function(j) {
             var prop = jQuery(this).attr("itemprop");
             var val = iterator.currentRowValueForName(prop);
             jQuery(this).html(val);
         });
        jQuery(item).after(rendered);
        iterator.advance();
    }    
    console.log(item);
    return state;
}

jQuery.fn.render = function(callback) {
    // Prepare all data sources
    data_sources = {};
    jQuery(this).find("[data-source]").each(function(j) {
        var data_name = jQuery(this).attr("data-result");
        if (data_name) {
            data_sources[data_name] = dataForSource(jQuery(this).attr("data-source"));
        }
    });
    
    // Gather 
    templates = gatherTemplateTree(this);
    
    // Render
    renderTree(templates, data_sources, null);
    
    // while (res.isValidRow()) {
    //  // Loop over each item to do
    //  templates.each(function(i) {
    //      jQuery(this).find("[itemprop]").each(function(j) {
    //          var prop = jQuery(this).attr("itemprop");
    //          var val = res.fieldByName(prop);
    //          jQuery(this).html(val);
    //      });
    //      jQuery(this).before(jQuery(this).clone());
    //  });
    //  res.next();
    //     }
    // 
    // templates.each(function(i) {
    //  jQuery(this).remove();
    // });
    // 
    // window.db.timeEnd("Rendering SQL Template");
    // if (callback != "undefined") {
    //  callback.call();
    // }
}
