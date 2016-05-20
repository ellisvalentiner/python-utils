import time
import os
from functools import wraps

import statsd


METRICS_HOST = os.getenv('METRICS_HOST')
METRICS_PORT = int(os.getenv('METRICS_HOST_PORT', 8125))
RELEASE_STAGE = os.getenv('RELEASE_STAGE', 'undefined')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'undefined')
PREFIX = '{}.{}'.format(RELEASE_STAGE, SERVICE_NAME)

if METRICS_HOST:
    _statsd_client = statsd.StatsClient(METRICS_HOST, METRICS_PORT, PREFIX)
else:
    print "warning - METRICS_HOST not set, not forwarding metrics"
    _statsd_client = None


def with_metrics(function_to_wrap):
    """
    Add this decorator to any Flask route to forward response times and status code counters.
    Note: be sure this decorator is placed below Flask's @app.route decorator
    """
    if not _statsd_client:
        return function_to_wrap

    endpoint = '{}.{}'.format(function_to_wrap.__module__, function_to_wrap.__name__)

    @wraps(function_to_wrap)
    def wrapped_endpoint(*args, **kwargs):
        t = time.time()
        retval = function_to_wrap(*args, **kwargs)
        response_time_ms = (time.time() - t) * 1000
        status_code = retval[1] if retval else 500  # if wrapped function doesn't return a value, flask is gonna spout a 500

        _statsd_client.timing('{}.response_time_ms'.format(endpoint), response_time_ms)
        _statsd_client.gauge('{}.{}'.format(endpoint, status_code), 1, delta=True)

        return retval

    return wrapped_endpoint
