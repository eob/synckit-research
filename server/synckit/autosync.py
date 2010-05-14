# from django.db import connection, transaction

class AutoSync:
    
    def __init__(self, query, version_field = None):
        self.query = ""
        self.tables = {}
        self.fields = {}
        self.parts = {}
        self.table_fields = {}

        self.query = query
        self.version_field = version_field
        self.extract_clauses()
        self.identify_tables()
        self.identify_fields()
    
    def printOut(self, versions):
        print "QUERY: %s" % self.query
        print 
        print "== Clauses ====================================="
        print "SELECT: %s" % self.parts["SELECT"]
        print "FROM: %s" % self.parts["FROM"]
        if "WHERE" in self.parts:
            print "WHERE: %s" % self.parts["WHERE"]
        print
        print "== Tables ======================================"
        for table in self.tables:
            print table
            for t in self.table_fields[table]:
                t_type = "Dependency"
                if t[1]:
                    t_type = "Projected"
                t_certainty = "Uncertain"
                if t[2]:
                    t_certainty = "Certain"
                    
                print "  - %s (%s, %s)" % (t[0], t_type, t_certainty)
            print
        print "== Queries ====================================="
        queries = self.generate_queries(versions)
        for (table, query) in queries.items():
            print table
            print "  %s" % query
            print

        print "== Spec ========================================"
        print self.spec()

    def extract_clauses(self):
        # Strip out whitespace
        self.query = self.query.strip()

        # Get rid of the semicolon
        if self.query[-1] == ';':
            self.query = self.query[:-1]
            
        # Split out the SELECT FROM and WHERE clauses
        upper = self.query.upper()

        # Split them into arrays
        split = self.query.split(' ')
        upsplit = upper.split(' ')

        # Remove ORDER BY's BY and remove 
        for i in range(len(split)-1):
            if upsplit[i] == "ORDER" and upsplit[i+1] == "BY":
                upsplit.pop(i+1)
                split.pop(i+1)
                
        # The tokens we use to divide them, and the 
        # corresponding hash keys they should go into
        tokens = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'LIMIT']
        names = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'LIMIT']
        
        outstanding_token = None
        outstanding_start = None
        
        for i in range(len(upsplit)):
            if upsplit[i] in tokens:
                index = tokens.index(upsplit[i])
                if outstanding_token != None:
                    self.parts[names[outstanding_token]] = ' '.join(split[outstanding_start:i])
                outstanding_token = index
                outstanding_start = i+1
        if outstanding_token != None:
            self.parts[names[outstanding_token]] = ' '.join(split[outstanding_start:])

    def identify_tables(self):
        # Identify each table
        for table in self.parts["FROM"].split(","):
            i_as = table.upper().find(" AS ")
            if i_as >= 0:
                self.tables[table[(i_as+4):].strip()] = table[0:i_as].strip()
                self.table_fields[table[(i_as+4):].strip()] = []
            else:
                self.tables[table.strip()] = table.strip()
                self.table_fields[table.strip()] = []

    def type_for_field(self, table, field):
        # TODO: Make this query the DB
        if (field[-2:].lower() == "id"):
            return "integer"
        elif field[-4:].lower() == "date":
            return "date"
        else:
            return "text"
        
    def identify_fields(self):        
        # Identify each field
        for field in self.parts["SELECT"].split(","):
            i_as = field.upper().find(" AS ")
            if i_as >= 0:
                self.fields[field[(i_as+4):].strip()] = field[0:i_as].strip()
            else:
                self.fields[field.strip()] = field.strip()

        # Identify each field
        # (field, materialized, certain)
        # Map each variable to a table
        for (field, orig_field) in self.fields.items():
            if field != orig_field:
                field = orig_field
            self.add_variable(field, True)
        # Now add all the ones in the where clause
        if "WHERE" in self.parts:
            for token in self.parts["WHERE"].split(" "):
                if token.upper() not in ["AND", "OR", "=", ">", "<", "-", "+", ">=", "<="]:
                    # we have a field
                    self.add_variable(token, False) 
    
    # (field, materialized, certain)
    def add_variable(self, field, materialized):
        i_dot = field.find('.')
        if i_dot >= 0:
            # For the case where the table is explicitly specified
            table = field.split('.')[0]
            if table in self.table_fields:
                self.table_fields[table].append((field, materialized, True))
            else:
                print "Found a table reference (%s) that shouldn't exist." % table
                assert False
        else:
            # If the table is implicitly specified 
            if len(self.tables) == 1:
                # And we only have one table
                table = self.tables.keys()[0]
                self.table_fields[table].append((field, materialized, True))
            else:
                # We have multiple tables
                for table in self.tables.keys():
                    self.table_fields[table].append((field, materialized, False))

    def spec(self):
        spec = {}
        sync_spec = {
            '__type' : 'auto',
            'version' : self.version_field,
        }
        for table in self.tables:
            table_schema = []
            
            for t in self.table_fields[table]:
                if t[2]:
                    # Certain
                    table_schema.append("%s %s" % (t[0].split('.')[1], self.type_for_field(table, t[0])))
                else:
                    # TODO: do a check to see if the field is in the table
                    # Uncertain: ERROR! Not supported
                    pass
            spec[table] = {
                "schema" : table_schema, \
                "syncspec" : sync_spec, \
                "vshash" : id
            }

        return spec
        
    def generate_queries(self, versions):
        queries = {}
        
        where_additions = []
        now_additions = []
        for proj,table in self.tables.items():
            if proj in versions:
                if "min" in versions[proj]:
                    where_additions.append("(%s.version > %s)" % (proj, versions[proj]["min"]))
                if "max" in versions[proj]:
                    where_additions.append("(%s.version < %s)" % (proj, versions[proj]["max"]))                    
                if "now" in versions[proj]:
                    now_additions.append("(%s.version < %s)" % (proj, versions[proj]["now"]))                    
            else:
                where_additions.append("(1)")
        where_addition = " OR ".join(where_additions)
        now_addition = " OR ".join(now_additions)
        
        for table in self.tables:
            fields = ", ".join([t[0] for t in self.table_fields[table]])
            q = "SELECT %s FROM %s " % (fields, self.parts["FROM"])
            if "WHERE" in self.parts:
                q += "WHERE (%s) AND (%s) AND (%s)" % (self.parts["WHERE"], where_addition, now_addition)
            else:
                q += "WHERE (%s) AND (%s)" % (where_addition, now_addition)
            if "ORDER" in self.parts:
                q += " ORDER %s" % self.parts["ORDER"]
            if "LIMIT" in self.parts:
                q += " LIMIT %s" % self.parts["LIMIT"]
            queries[table] = q
            
        return queries
        

    def runqueries(self, request):
        # Extract the version numbers
        
        return self.get_results(versions)
        
    def get_results(self, versions):
        cursor = connection.cursor()    
        
        queries = self.generate_queries(versions)
        results = {}
        for table,query in queries.items():
            result_arr = []
            cursor.execute(query)
            for row in cursor.fetchall() :
                result_arr.append([str(item) for item in row])
            results[table] = result_arr
        return results
        
    def runqueries(self, request):
        return {}

def main():
    query = "SELECT blog_entry.id, blog_entry.title, blog_entry.contents, blog_entry.date FROM blog_entry LIMIT 10;"

    versions = {"blog_entry":{
        "min":"version",
        "now":"now"
    }}

    qr = AutoSync(query)

    qr.extract_clauses()
    qr.identify_tables()
    qr.identify_fields()
    qr.printOut(versions)

if __name__ == "__main__":
    main()
