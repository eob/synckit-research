_skProto = function() {

    // Error Check -- Make sure 'new' keyword was used
    // ----------------------------------------------------------------
    if ( !(this instanceof _skProto) ) 
       return new _skProto();
       
    // Member Variables
    // ----------------------------------------------------------------
    this._localdb = null;
    this._timers = null;
    
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
    
    this.timeStart = function(obj) {
        this._timers[obj] = null;            
        this._timers[obj] = (new Date).getTime();
    }
    
    this.timeEnd = function(obj) {
        if (this._timers[obj]) {
            var diff = (new Date).getTime() - this._timers[obj];
            this._timers[obj] = null;            
            return diff;
        }
        return null;
    }
    
    this.table_exists = function(table) {
        var result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", [table]);
        var retval = result.isValidRow();
        result.close();
        return retval;
    }
    
    this.create_tables = function() {
        console.info("Creating Stats Table");
        if (this._localdb !== null) {
            this.execute("CREATE TABLE IF NOT EXISTS sk_endpoints (id integer PRIMARY KEY AUTOINCREMENT, endpoint_uri varchar(512), UNIQUE (endpoint_uri));").close();
            this.execute("CREATE TABLE IF NOT EXISTS sk_views (id integer PRIMARY KEY AUTOINCREMENT, endpoint_id integer REFERENCES sk_endpoints(id), name varchar(128), schema text, syncspec text, vshash varchar(32), UNIQUE (endpoint_id, name));").close();
        } else {
            console.error("Could not create stats table. Local DB is null.");
        }        
    };
    
    this.reset = function() {
        console.info("Resetting DB");
        if (this._localdb !== null) {
            this._localdb.remove();
            this.opendb("synckit");
            this.create_tables();
        }
        else {
            console.error("Local DB is null.");
        }
    };

    /* When this function completes, the given endpoint will update the
     * sk_endpoints and sk_views tables to contain the most up-to-date
     * information on the view with name viewname and viewspec.  If the old
     * view is out of date (the view's stored vshash is not the one in the
     * viewspec), the table will be updated with the new viewspec
     * information, the old view will be dropped, and a new view will be
     * created in its stead. */
    this.build_view = function(endpoint, viewname, viewspec) {
        var endpoint_id = this.get_or_create_endpoint_id(endpoint);
        var view_res = this.execute("SELECT * FROM sk_views WHERE endpoint_id = ? and name = ?;", [endpoint_id, viewname]);
        if (!view_res.isValidRow()) {
            view_res.close();
            // if it doesn't exist, create it.
            // create an entry in sk_views
            this.execute("INSERT INTO sk_views (endpoint_id, name, schema, syncspec, vshash) VALUES (?, ?, ?, ?, ?);", [endpoint_id, viewname, JSON.stringify(viewspec.schema), JSON.stringify(viewspec.syncspec), viewspec.vshash]).close();
            // create a table for the view
            this.create_view_table(this.view_table_name(endpoint_id, viewname), viewspec.schema, viewspec.syncspec)
        } else if (viewspec.vshash != view_res.fieldByName('vshash')) {
            view_res.close();
            // if it exists, but had an outdated id, re-create it
            // update the entry in sk_views
            this.execute("UPDATE sk_views SET schema = ?, syncspec = ?, vshash = ? WHERE endpoint_id = ? AND name = ?;", [JSON.stringify(viewspec.schema), JSON.stringify(viewspec.syncspec), viewspec.vshash, endpoint_id, viewname]).close();
            var view_table_name = this.view_table_name(endpoint_id, viewname);
            // drop the old view's table
            this.execute("DROP TABLE IF EXISTS " + view_table_name + ";").close();
            // create the new view's table
            this.create_view_table(view_table_name, viewspec.schema, viewspec.syncspec)
        }
    };

    /* Returns the ID of the endpoint uri, creating an entry if one doesn't
     * exist.*/
    this.get_or_create_endpoint_id = function(endpoint) {
        endpoint_res = this.execute("SELECT id FROM sk_endpoints WHERE endpoint_uri = ?;", [endpoint]);
        endpoint_id = 0;
        if (!endpoint_res.isValidRow()) {
            endpoint_res.close();
            this.execute("INSERT INTO sk_endpoints (endpoint_uri) VALUES (?);", [endpoint]).close();
            endpoint_res = this.execute("SELECT id FROM sk_endpoints WHERE endpoint_uri = ?;", [endpoint]);
        }
        var retval = endpoint_res.fieldByName('id');
        endpoint_res.close();
        return retval;
    };

    /* Returns the name of the view (table) in the database for the view
     * named viewname in the endpoint specified */
    this.view_table_name = function(endpoint_id, viewname) {
        return "sk_" + viewname + endpoint_id;
    };
   
    /* Returns view information for the view at endpoint with
     * id=endpoint_id, and name specified by viewname.  fields is an array
     * of fields to be returned in a dictionary.  Possibilities are:
     * "syncspec" "vshash and "schema". */
    this.get_view_info = function(endpoint_id, viewname, fields) {
        var sql = "SELECT ";
        for (var i = 0; i < fields.length; i++) {
            sql += "?,";
        }
        sql = sql.substr(0, sql.length - 1);
        sql += " FROM sk_views WHERE endpoint_id = ? AND viewname = ?;";
        var args = fields.concat([endpoint_id, viewname]);
        var res = this.execute(sql, args);
        var ret = {}
        if (res.isValidRow()) {
            for (var field in fields) {
                ret[field] = res.fieldByName(field);
            }
        } else {
            console.log('Could not find view in get_view_info: ' + viewname);
        }
        res.close();
        return ret;
    };
    
    /* Build the view table and any necessary indices on the table
     * depending on the type of syncspec specified. 
     * NOTE/potential sql injection attack: because we can't use prepared 
     * statements for CREATE TABLE statements, be careful what table/field 
     * names you pass into this.*/
    this.create_view_table = function(view_table_name, schema, syncspec) {
        var sql = "CREATE TABLE " + view_table_name + " ("; 
        for (var i = 0; i < schema.length; i++) {
            sql += schema[i] + ",";
        }
        sql = sql.substr(0, sql.length - 1);
        if (syncspec.__type === "queue") {
            sql += ", UNIQUE (" + syncspec.sortfield + ")";
        } else if (syncspec.__type === "set") {
            sql += ", UNIQUE (" + syncspec.idfield + ")";
        }
        // TODO: do we need to index cube fields?
        sql += ");";
        this.execute(sql).close();
    };
    
    /* Synchronizes the local database with endpoint_uri.
     *   views_to_sync is a list of the view names of the views you wish to sync.
     *   extra_view_params is a dictionary of the form
     *       { "viewname1": {param1: val1, param2: val2},
     *         "viewname2": {param3: val3} }
     *     these parameters will be added to the query for each view.
     *     they are useful for things like sets, which must append 
     *     the ID of the item being queried (e.g., {"setname": {"filter": 30}})
     *   extra_query_params is a flat dictionary which contains arguments
     *     that will be appended to the query dictionary and apply
     *     query-wide.  arguments such as "__latency" and "__bandwidth"
     *     should be added to this dictionary. */
    this.sync = function(endpoint_uri, views_to_sync, extra_view_params, extra_query_params, callback) {
        var endpoint_id = this.get_or_create_endpoint_id(endpoint_uri);
        var query = this.generate_query(endpoint_id, views_to_sync, extra_view_params);
        this.issue_query(endpoint_uri, query, extra_query_params, callback);
    };

    /* Returns the state of each of the views for a given endpoint.  This
     * can be sent to the server to receive an updated state.  endpoint_id
     * represents the URI of the endpoint being queried. views_to_sync and
     * extra_view_params are documented in this.sync. */
    this.generate_query = function(endpoint_id, views_to_sync, extra_view_params) {
        if (this._localdb !== null) {
            var query = {};
            // loop through the views we wish to sync.
            for (var viewname in views_to_sync) {
                var view_info = this.get_view_info(endpoint_id, viewname, ['syncspec', 'vshash']);
                var syncspec = view_info.syncspec
                var vshash = view_info.vshash
                if (syncspec.__type == "set") {
                    this.set_query(endpoint_id, viewname, syncspec, extra_view_params[viewname], query);
                }
                else if (syncspec.__type == "queue") {
                    this.queue_query(endpoint_id, viewname, syncspec, extra_view_params[viewname], query);
                }
                else if (syncspec.__type == "cube") {
                    this.cube_query(endpoint_id, viewname, syncspec, extra_view_params[viewname], query);
                }

                if (viewname in query) {
                    query[viewname].__vshash = vshash;
                }
            }
            return query;
        }
        else {
            console.error("Local DB is null. No Stats available");
            return {};
        }        
    };

    /* Configures the 'query' dictionary to append a query for the endpoint
     * and view specified by viewname, whose type is a set.  The syncspec
     * contains sync information for this set, and extra_params may be
     * empty, or contain a 'filter' argument, which specifies which id to
     * ask for specifically.  'query' will only be updated if there is no
     * 'filter' parameter, or if the id specified by the 'filter' parameter
     * does not exist in the current view. */
    this.set_query = function(endpoint_id, viewname, syncspec, extra_params, query) {
        if (syncspec.__type != "set") {
            console.log("Configuring a set that isn't: " + view_name);
            return;
        }
        var send_query = true;
        var sq = {};
        // Do we want to filter only a specific row?
        if (extra_params && ('filter' in extra_params)) {
            var theid = extra_params.filter;
            var table = this.view_table_name(endpoint_id, viewname);
            var res = this.execute("SELECT ? FROM ? WHERE ?=?;", [syncspec.idfield, table, syncspec.idfield, theid]);
            // If the row doesn't already exist, we continue with the query.
            // Otherwise, we've got the row, and don't send the query.
            if (! res.isValidRow()) {
                sq.filter = theid;
            } else {
                send_query = false;
            }
            res.close();
        }

        // send_query is true if there was no filter, or if the filtered id
        // wasn't found.
        if (send_query) {
            // generate a list of ids we already have and add those to the
            // query.
            var res = this.execute("SELECT ? FROM ?", [syncspec.idfield, table]);
            var already = [];
            while (res.isValidRow()) {
                already.push(res.field(0));
                res.next();
            }
            if (already.length > 0) {
                sq.exclude = already;	
            }
            res.close();
            query[viewname] = sq;
        }
    };

    /* Configures the 'query' dictionary to append a query for the endpoint
     * and view specified by viewname, whose type is a queue.  The syncspec
     * contains sync information for this queue, and extra_params may be
     * empty, or contain a 'now' argument, which is only used for
     * testing.  'now' can be set to the date at which to display the
     * queue, to facilitate time-travel: no row with sortfield greater than
     * the 'now' value will be displayed. */
    this.queue_query = function(endpoint_id, viewname, syncspec, extra_params, query) {
        if (syncspec.__type != "queue") {
            console.log("Configuring a queue that isn't: " + view_name);
            return;
        }

        var sq = {};
        var minmax;
        if (syncspec.order == "DESC") {
            minmax = "min";
        }
        else if (syncspec.order == "ASC") {
            minmax = "max";
        }
        var table = this.view_table_name(endpoint_id, viewname);
        var stmt = "SELECT ?(?) FROM ?;"
        var res  = this.execute(stmt, [minmax, syncspec.sortfield, table]);
        if (res.isValidRow() && (res.field(0) != null)) {
            sq[minmax] = res.field(0);
        }
        res.close();
        if (extra_params && ('now' in extra_params)) {
            sq.now = extra_params.now;
        }
        query[viewname] = sq;
    };

    /* Configures the 'query' dictionary to append a query for the endpoint
     * and view specified by viewname, whose type is a data cube.  The syncspec
     * contains sync information for this cube.  Currently, there is no
     * special functionality of the state of the cube, so an empty query is
     * always sent for the view. */
    this.cube_query = function(endpoint_id, viewname, syncspec, extra_params, query) {
        if (syncspec.__type != "cube") {
            console.log("Configuring a cube that isn't: " + view_name);
            return;
        }
        query[viewname] = {};
    };
    
    /* Sends the query to the endpoint after appending extra_query_params
     * to it.  Once a response comes back, this.bulkload will be called
     * asynchronously, which will call the callback that the user specified
     * after properly syncing the local database. */
    this.issue_query = function(endpoint_uri, endpoint_id, query, extra_query_params, callback) {
        for (var key in extra_query_params) {
            query[key] = extra_query_params[key];
        }
        var params = {"queries":JSON.stringify(query)};
        var bulkload_func = function(response) {
            this.bulkload(response, endpoint_id, endpoint_uri, callback);
        };
        jQuery.post(endpoint_uri, params, bulkload_func, "json");
    };

    this.execute = function(statement, args) {
        if (this._localdb !== null) {
            console.log("$$$" + statement);
            console.log(args);
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
            res.close();
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
    
    this.bulkload = function(response, endpoint_id, endpoint_uri, callback) {
        console.info("hey");
        this.timeStart("Performing Bulkload Insertion"); 
        for (var viewname in response) {
            var viewdata = response[viewname];
            if (typeof(viewdata) == "string") {
                console.info("Skipping view " + viewname + " with message: " + viewdata);
                continue;
            }
            
            // if a viewspec comes back, the server is signalling that we
            // might have a new schema for this view.  try to rebuild the view.
            if ("viewspec" in viewdata) {
                this.build_view(endpoint_uri, viewname, viewdata.viewspec);
            }

            // Insert the results into the view if any exist
            var results = viewdata.results;
            if (results.length == 0) {
            	continue;
            }
            var viewtable = view_table_name(endpoint_id, viewname);
            var sqlStatement = "INSERT INTO " + viewtable + " VALUES (";
            for (var z = 0; z<results[0].length; z++) {
                sqlStatement += "?,";
            }   
            sqlStatement = sqlStatement.substr(0,sqlStatement.length - 1);
            sqlStatement += ");";
            
            this.execute("BEGIN");
            for (var row in results) {
                this.execute(sqlStatement, row);
            }
            this.execute("COMMIT").close();
        }
        // Alert the sync requester that the job is done.
        callback();
        this.timeEnd("Performing Bulkload Insertion");
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
            var retval = result.isValidRow();
            result.close();
            return retval;
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
            var retval = result.isValidRow();
            result.close();
            return retval;
            
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
            rs.close();
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
        this.opendb("synckit"); 
        this.create_tables();
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

function urlParam(name){
	var results = new RegExp('[#&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results) {
		return results[1].replace(/%20/,' ')
	}
	return 0;
}

