
# also published as a gist - https://gist.github.com/evan-burke/9b690d0df243b9bb0a72b3f8109b7465

""" This is pretty basic but makes it a little eaiser to use sqlite3 for common tasks.

    Example usage:
    db = sqlitelib(dbfile)
    result = db.execute("select * from mytable")
    
    or:
    with sqlitelib(dbfile) as db:
      result = db.execute("select * from  mytable")
    
    """

import sqlite3

class sqlitelib(object):
    """ wrapper for sqlite3 providing some convenience functions.
        Autocommit is on by default, and query results are lists of dicts. """
    
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.conn = self.connect()
        
    def __enter__(self):
        return self #.__init__()
        
    def connect(self):
        self.conn = sqlite3.connect(self.dbfile, isolation_level=None)
        self.conn.row_factory = self.dict_factory
        return self.conn
    
    def execute(self, sql, parameters=None):
        if not parameters:
            c = self.conn.execute(sql)
        else:
            c = self.conn.execute(sql, parameters)
        data = c.fetchall()
        return data
    
    def executemany(self, sql, parameters):
        c = self.conn.executemany(sql, parameters)
        data = c.fetchall()
        return data
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def close(self):
        self.conn.close()
        
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
