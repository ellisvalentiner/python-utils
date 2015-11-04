import logging
import argparse
import time
import signal

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 10


def start_service(app, service_name, num_processes=None):
    parser = argparse.ArgumentParser(description='Start {} service'.format(service_name))
    parser.add_argument('-p', '--port', default=8080, required=False, type=int)
    parser.add_argument('-d', '--debug', default=False, action='store_true', required=False)
    args = parser.parse_args()

    if args.debug:
        app.run('0.0.0.0', args.port, args.debug, threaded=True)
    else:
        http_server = HTTPServer(WSGIContainer(app))

        def shutdown():
            logging.info('Stopping http server')
            http_server.stop()

            logging.info('Forcing shutdown in %s seconds ...',
                         MAX_WAIT_SECONDS_BEFORE_SHUTDOWN)
            io_loop = IOLoop.instance()

            deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
                    logging.info('Shutdown')
            stop_loop()

        def sig_handler(sig, frame):
            logging.warning('Caught signal: %s', sig)
            IOLoop.instance().add_callback(shutdown)

        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        http_server.bind(args.port)
        http_server.start(num_processes)  # Forks multiple sub-processes
        IOLoop.current().start()

        logging.info('Goodbye')
