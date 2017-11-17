import MySQLdb
import sys

class Connector:
    db_server = None
    db_user = None
    db_pass = None
    db_name = None
    conn = None
    conn_cur = None

    """
    Constructor.
    """
    def __init__(self, db_server, db_user, db_pass, db_name):
        self.db_server = db_server
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

    """
    Get a mysql connection
    """
    def get_connection(self):
        try:
            self.conn = MySQLdb.connect(self.db_server, self.db_user, self.db_pass, self.db_name)
            return self.conn
        except:
            return None

    """
    Reconnect to the Database
    """
    def reconnect(self):
        self.get_connection()
        self.conn.get_cursor()

    """
    Inserts
    """
    def do_insert(self, query):
        data = dict()
        try:
            if self.conn is None:
                self.get_connection()
            self.conn_cur = self.conn.cursor()
            self.conn_cur.execute(query)
            self.conn.commit()
            insert_id = self.conn_cur.lastrowid
            data['data'] = insert_id
            data['status'] = 'OK'
            self.conn_cur.close()
        except:
            error = str(sys.exc_info()[1])
            self.conn.rollback()
            data['data'] = None
            data['status'] = 'FAIL'
        return data

    """
    Selects
    """
    def do_select(self, query, fetchall=False):
        data = {}
        try:
            self.get_connection()
            self.conn_cur = self.conn.cursor()
            self.conn_cur.execute(query)
            #if fetchall is True:
            #    res = self.conn_cur.fetchall()
            #else:
            res = self.conn_cur.fetchone()
            if res is not None:
                data['data'] = res
            else:
                data['data'] = None
            data['status'] = 'OK'
            self.conn_cur.close()
        except:
            data['data'] = None
            data['status'] = 'FAIL'
        return data

    """
    Inserts
    """
    def do_update(self, query):
        data = dict()
        try:
            if self.conn is None:
                self.get_connection()
            self.conn_cur = self.conn.cursor()
            self.conn_cur.execute(query)
            self.conn.commit()
            data['status'] = 'OK'
            self.conn_cur.close()
        except:
            error = str(sys.exc_info()[1])
            self.conn.rollback()
            data['data'] = None
            data['status'] = 'FAIL'
        return data

    """
    Close DB objects
    """
    def close_db_objects(self):
        if self.conn_cur is not None:
            self.conn_cur.close()
        if self.conn is not None:
            self.conn.close()
