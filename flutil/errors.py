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
def with_bugsnag(function_to_snag):
    def wrapped_except(*args, **kwargs):
        try:
            return function_to_snag(*args, **kwargs)
        except Exception as e:
            log_exception(e, context_msg=function_to_snag.__name__)
    return wrapped_except
