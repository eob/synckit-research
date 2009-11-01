# Custom DB backend postgresql_psycopg2 based
# implements persistent database connection using global variable

from django.db.backends.postgresql_psycopg2.base import DatabaseError, DatabaseWrapper as BaseDatabaseWrapper, \
    IntegrityError
from psycopg2 import OperationalError

connection = None

class DatabaseWrapper(BaseDatabaseWrapper):
    def _cursor(self, *args, **kwargs):
        global connection
        if connection is not None and self.connection is None:
            try: # Check if connection is alive
                connection.cursor().execute('SELECT 1')
            except OperationalError: # The connection is not working, need reconnect
                connection = None
            else:
                self.connection = connection
        cursor = super(DatabaseWrapper, self)._cursor(*args, **kwargs)
        if connection is None and self.connection is not None:
            connection = self.connection
        return cursor

    def close(self):
        if self.connection is not None:
            self.connection.commit()
            self.connection = None

