import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


MAX_CONNECTION_ATTEMPTS = 10


class PoolManager:
    def __init__(self, connection_url, name=None, mincount=2, maxcount=40,
                 cursor_factory=RealDictCursor):
        self._pool = pool.ThreadedConnectionPool(mincount, maxcount, connection_url, cursor_factory=cursor_factory)
        self.name = name or connection_url

    def __del__(self):
        self._pool.closeall()

    @contextmanager
    def cursor(self, commit_on_close=False):
        for _ in range(MAX_CONNECTION_ATTEMPTS):
            try:
                con = self._pool.getconn()
                if not con.closed:
                    break
            except psycopg2.DatabaseError, psycopg2.OperationalError:
                pass
        else:
            raise RuntimeError('Could not get a connection to: {}'.format(self.name))

        try:
            yield con.cursor()
            if commit_on_close:
                con.commit()
        except pool.PoolError as e:
            logging.log(logging.ERROR, e.message)
        finally:
            try:
                self._pool.putconn(con)
            except psycopg2.pool.PoolError as e:
                logging.warn(e.message)
