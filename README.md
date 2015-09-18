# python-utils
Commonly-used utilities and helpers

##db.py
Postgres database connection manager, backed by a threaded connection pool.

Usage:

```python
from flutil import db

db_url = 'postgres://foo:bar@baz:port/db_name'
con = db.PoolManager(db_url)

query = 'select * from foo where bar = (?)'
with con.cursor() as c:
	c.execute(query, (bar,))

statement = 'insert into foo (bar, baz) values (?, ?)'
with con.cursor(commit_on_close=True) as c:
	c.execute(statement, (bar, baz))
```

## flask_server.py
Flask server backed by Tornado for multi-threaded connection handling

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

