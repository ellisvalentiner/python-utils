import logging
import os
import bugsnag

bugsnag.configure(api_key=os.getenv('BUGSNAG_API_KEY', ''),
                  project_root=os.getenv('PROJECT_ROOT', '/'),
                  notify_release_stages=[os.getenv('BUGSNAG_RELEASE_STAGE', 'testing')])

def log_exception(e, context_msg=None):
    if context_msg:
        msg = '%s: %s' % (context_msg, e.message)
    else:
        msg = e.message

    bugsnag.notify(e, context=context_msg)
    logging.error(msg)


# decorator to use for quick and dirty bugsnag injections
# use case:
# from errors import with_bugsnag
# @with_bugsnag
# def f(x):
#     return 10/x
# f(0)
# > ERROR:root:asdf: integer division or modulo by zero

def with_bugsnag(func):
    def wrapped_except(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_exception(e, context_msg=func.__name__)
    return wrapped_except
