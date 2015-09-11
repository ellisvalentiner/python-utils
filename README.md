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