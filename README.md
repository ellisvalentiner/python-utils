# python-utils
Commonly-used utilities and helpers

##db.py
Postgres database connection manager, backed by a threaded connection pool.

Usage:

```python
from flutil import db

db_url = 'postgres://foo:bar@baz:port/db_name'
con = db.PoolManager(db_url)
```
or:

```python
env_var_name = 'FOO_DATABASE_URL'
con = db.PoolManager.from_name(env_var_name)
```

```python-utils
query = 'select * from foo where bar = (?)'
with con.cursor() as c:
	c.execute(query, (bar,))

statement = 'insert into foo (bar, baz) values (?, ?)'
with con.cursor(commit_on_close=True) as c:
	c.execute(statement, (bar, baz))
```

## flask_server.py
Flask application server backed by Tornado for multi-threaded connection handling.

Usage:

```python
from flask import Flask
from flutil import flask_service

app = Flask(__name__)

@app.route('/foo', methods=['POST'])
def foo():
	...
	
@app.route('/bar', methods=['POST'])
def bar():
	...
	
if __name__ == '__main__':
    service_name = 'foo'
    flask_server.start_service(app, service_name)
```	

## errors.py
Decorator for forwarding uncaught exceptions to Bugsnag

Usage:

```python
@with_bugsnag
def foo():
    ...
```

Requires the following env vars:

+ `BUGSNAG_RELEASE_STAGE` (e.g., live/dev/stage)
+ `BUGSNAG_API_KEY`


## metrics.py
Decorator for forwarding flask endpoint response code counts and timing info to statsd

Usage:

```python
@app.route('foo')
@with_metrics
def foo():
   ...
``` 

Requires the following env vars:

+ `METRICS_HOST`
+ `METRICS_HOST_PORT`
+ `RELEASE_STAGE` (e.g., live/dev/stage)
+ `SERVICE_NAME` 

Response code counters are named like so:
`{RELEASE_STAGE}.{SERVICE_NAME}.{MODULE_NAME}.{FUNCTION_NAME}.{RESPONSE_CODE}`

Timers are named like so:
`{RELEASE_STAGE}.{SERVICE_NAME}.{MODULE_NAME}.{FUNCTION_NAME}.response_time_ms`
