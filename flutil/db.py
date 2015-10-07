import os
import logging
import psycopg2

from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

MAX_CONNECTION_ATTEMPTS = 10


class EnvironmentVariableNotFoundException(Exception):
    pass

class PoolManager:
    connections = {}

    @staticmethod
    def get_url_from_environment(name=None):
        """
        Try name as upper-cased and with _DATABASE_URL appended,
        accepting the first name that exists.

        """
        attempts = (name.upper(), '%s_DATABASE_URL' % name.upper(), )

        for env in attempts:
            if env in os.environ:
                return os.environ.get(env), env

        raise EnvironmentVariableNotFoundException(\
            "The envrionment variables %s were not found." % ' or '.join(attempts) )

    @classmethod
    def from_name(cls, name=None, cached=True):
        """
        Return a pool instance by name (following our convention of NAME_DATABASE_URL)
        first checking to see if it's already been created and returning that instance.

        Unless the `cached` argument is False, in which case a new instance is always returned.

        """
        if not name:
            name = 'DATABASE_URL'

        url, env = cls.get_url_from_environment(name)

        if not cached:
            return cls(connection_url=url, name=env)

        if url in cls.connections:
            return cls.connections.get(url)

        new_conn = cls(connection_url=url, name=env)
        cls.connections[url] = new_conn
        return new_conn

    def __init__(self, connection_url, name=None, mincount=2, maxcount=40, cursor_factory=RealDictCursor):
        self.connection_url = connection_url
        self.name = name or connection_url

        self._pool = pool.ThreadedConnectionPool(mincount, maxcount, connection_url, cursor_factory=cursor_factory)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

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
