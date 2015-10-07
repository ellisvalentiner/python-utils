import os
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

MAX_CONNECTION_ATTEMPTS = 10


class EnvironmentVariableNotFoundException(Exception):
    pass


class PoolManager:
    _connections = {}

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

        raise EnvironmentVariableNotFoundException(
            "The envrionment variables %s were not found." % ' or '.join(attempts))

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        Return a pool instance by name (following our convention of NAME_DATABASE_URL)
        first checking to see if it's already been created and returning that instance.

        Unless the `cached` argument is False, in which case a new instance is always returned.

        """
        if not name:
            name = 'DATABASE_URL'

        url, env = PoolManager.get_url_from_environment(name)

        return cls.from_url(url, **kwargs)

    @classmethod
    def from_url(cls, url, **kwargs):
        kwargs['connection_url'] = url

        if not kwargs.get('cached', True):
            return DatabasePool(**kwargs)

        cache_key = hash(frozenset(kwargs.items()))

        if cache_key in cls._connections:
            return cls._connections.get(cache_key)

        new_conn = DatabasePool(**kwargs)
        cls._connections[cache_key] = new_conn
        return new_conn


class DatabasePool:
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
