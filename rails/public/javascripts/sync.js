_skProto = function() {

    // Error Check -- Make sure 'new' keyword was used
    // ----------------------------------------------------------------
    if ( !(this instanceof _skProto) ) 
       return new _skProto();
       
    // Member Variables
    // ----------------------------------------------------------------
    this._localdb = null;
    
    // Methods
    // ----------------------------------------------------------------
    this.opendb = function(name) {
        if (this._localdb !== null) {
            this._localdb.open(name);
        }
        else {
            console.error("Local DB is null.");
        }
    };
    
    this.create_stats_table = function() {
        console.info("Creating Stats Table");
        if (this._localdb !== null) {
            this.execute("CREATE TABLE IF NOT EXISTS sk_stats (entity varchar(255), type varchar(255), state varchar(255));");
        }
        else {
            console.error("Could not create stats table. Local DB is null.");
        }        
    };
    
    this.reset = function() {
        console.info("Resetting DB");
        if (this._localdb !== null) {
            this._localdb.remove();
            this.opendb("synckit");
            this.create_stats_table();
        }
        else {
            console.error("Local DB is null.");
        }
    };
    
    this.get_state = function() {
        if (this._localdb !== null) {
            var res = this.execute("SELECT entity, state FROM sk_stats;");
            var state = {};
            while (res.isValidRow()) {
                state[result.field(0)] = result.field(1);
                result.next();
            }
            return state;
        }
        else {
            console.error("Local DB is null. No Stats available");
            return {};
        }        
    };
    
    this.execute = function(statement, args) {
        if (this._localdb !== null) {
            return this._localdb.execute(statement, args);                
        }
        else {
            console.error("Can't execute query. Local DB is null.");
        }
    };

    // Returns the result of a query as a JSON statement
    this.json_results_for = function(statement, args) {
        if (this._localdb !== null) {
            var res = this._localdb.execute(statement, args);
            var ans = [];
            while (res.isValidRow()) {
                var obj = {};
                for (var i=0; i<res.fieldCount(); i++) {
                    obj[res.fieldName(i)] = res.field(i);
                }
                ans[ans.length] = obj;
                res.next();
            }
            return ans;      
        }
        else {
            console.error("Can't execute query. Local DB is null.");
        }
    };

    // Takes a hash table where keys are the label
    // and values are the sql statements
    this.process_data_spec = function(data_spec) {
        var ret = {};
        for (var key in data_spec) {
            var val = data_spec[key];
            if (typeof(val) == "string") {
                ret[key] = this.json_results_for(val);
            }
            else if (typeof(val) == "object") {
                ret[key] = this.process_data_spec(val);
            }
        }
        return ret;
    }
    
    this.bulkload = function(data) {
        console.time("Performing Bulkload Insertion");
        for (var i=0; i<data.length; i++) {
            var def = data[i];
            var table = def[0];
            var schema = def[1];
            var sqlStatement = "INSERT INTO " + table + " VALUES (";
            for (var z = 0; z<schema.length; z++) {
                sqlStatement += "?,";
            }   
            sqlStatement = sqlStatement.substr(0,sqlStatement.length - 1);
            sqlStatement += ");";
            
            this.execute("CREATE TABLE IF NOT EXISTS " + table + " (" + schema.join() + ");");
            var rows = def[2];
                for (var j=0; j<rows.length; j++) {
                    var row = rows[j];  
                    this.execute(sqlStatement, row);
                }
        }
        console.timeEnd("Performing Bulkload Insertion");
    };

    
    // Debugging Methods
    // ----------------------------------------------------------------
    // 
    this.dump_stats = function(table) {
        if (typeof(table) == "undefined") {
            // Get a list of all tables
            var result = this.execute("SELECT name FROM sqlite_master WHERE type='table';");
            while (result.isValidRow()) {
                console.info("===" + result.field(0) + "===");
                this.dump_stats(result.field(0));
                console.info("=============================");
                console.info("=============================");
                result.next();
            }
            return result.isValidRow();
        }
    };
    
    this.dump = function(table) {
        if (typeof(table) == "undefined") {
            // Get a list of all tables
            var result = this.execute("SELECT name FROM sqlite_master WHERE type='table';");
            while (result.isValidRow()) {
                console.info("===" + result.field(0) + "===");
                this.dump(result.field(0));
                console.info("=============================");
                console.info("=============================");
                result.next();
            }
            return result.isValidRow();
            
        }
        
        if (this._localdb !== null) {
            var rs = this.execute("SELECT * FROM " + table + ";");
            while (rs.isValidRow()) {
              for (var i=0; i<rs.fieldCount(); i++) {
                  console.log(rs.fieldName(i) + ": " + rs.field(i));
              }
              console.log("----");
              rs.next();
            }
        }
        else {
            console.error("Can't dump. Local DB is null.");
        }
    };
    
    // Initialization
    // ----------------------------------------------------------------

    if ((typeof(google) != "undefined") &&
        (typeof(google.gears) != "undefined")) {
        
        this._localdb = google.gears.factory.create('beta.database');   
        // _localdb.greet("Ted");
        this.opendb("synckit"); 
        this.create_stats_table();
    }
    else {
        this._localdb = null;
        console.error("Google Gears not found.");
    }
    
};

create_synckit = function() {
    var db = new _skProto();
    return db;
};
