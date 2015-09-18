import os
import logging
import psycopg2

from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

MAX_CONNECTION_ATTEMPTS = 10


class PoolManager:
    @staticmethod
    def get_url_from_environment(name=None):
        if name:
            # Try name exactly as provided, upper-cased, and finally, with _DATABASE_URL appended.
            # Accept the first name that exists
            for env in (name, name.upper(), '_'.join([name.upper(), 'DATABASE_URL'])):
                if env in os.environ:
                    return os.environ.get(env), env

        # Default to nothing for the userdata database url, which is just DATABASE_URL
        env = 'DATABASE_URL'
        return os.environ.get(env, None), env

    @classmethod
    def from_name(cls, name=None):
        url, env = cls.get_url_from_environment(name)
        if not url:
            assert 'Please specify a valid database, or ensure %s exists in your environment.' % (env, )
        return cls(connection_url=url, name=env)

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
