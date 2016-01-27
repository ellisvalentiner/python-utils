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
    """
    Provides convenience methods around creating DatabasePool objects, and
    attempts to cache those connections when possible.

    """
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

        See the DatabasePool class below for more information on the additional
        arguments that can be passed to this method.

        """
        if not name:
            name = 'DATABASE_URL'

        url, env = cls.get_url_from_environment(name)

        # Set the name for the DatabasePool to the environment variable
        kwargs['name'] = env

        return cls.from_url(url, **kwargs)

    @classmethod
    def from_url(cls, url, **kwargs):
        """
        Return a pool instance by Database URL.

        See the DatabasePool class below for more information on the additional
        arguments that can be passed to this method.

        """
        kwargs['connection_url'] = url

        # If cached=False is provided, return a fresh instance.
        if not kwargs.get('cached', True):
            return DatabasePool(**kwargs)

        # Generate a hashing key based on the keyword arguments.
        cache_key = hash(frozenset(kwargs.items()))

        if cache_key in cls._connections:
            return cls._connections.get(cache_key)

        new_conn = DatabasePool(**kwargs)
        cls._connections[cache_key] = new_conn
        return new_conn


class DatabasePool:
    """
    Creates and manages a pool of connections to a database.

    This wraps PersistentConnectionPool, see http://initd.org/psycopg/docs/pool.html

    - connection_url is a postgresql://user@host/database style DSN
    - name is an optional nickname for the database connection
    - mincount is the minimum number of connections to keep open
    - maxcount is the maximum number of connections to have open
    - cursor_factory defines the factory used for inflating database rows

    """
    def __init__(self, connection_url, name=None, mincount=2, maxcount=40, cursor_factory=RealDictCursor, **kwargs):
        self.connection_url = connection_url
        self.name = name or connection_url
        self._pool = pool.PersistentConnectionPool(mincount, maxcount, connection_url, cursor_factory=cursor_factory)

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
