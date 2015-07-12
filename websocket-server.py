#!/usr/bin/python

import concurrent.futures
import fcntl
import io
import os
import sys
import time
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.websocket


DIRNAME = os.path.dirname(__file__)
DATA_ROOT_PATH = os.path.join(DIRNAME, "data")
STATIC_PATH = os.path.join(DIRNAME, "static")
SETTINGS = {
    "executor": concurrent.futures.ThreadPoolExecutor(5),
    "static_path": STATIC_PATH,
    "debug": True,
    "compress_response": True
}


def follow_probe_file(probe_file):
    """Follow a file for new data written.

    It reads line by line, so lines must contain a CR/LF.

    :param probe_file: The file ojbect to read.
    :return Yield the lines as they are read.
    """
    probe_file.seek(0, 2)
    while True:
        line = probe_file.readline()
        if not line:
            time.sleep(0.5)
            continue
        else:
            yield line


class MainHandler(tornado.web.RequestHandler):
    """Main handler for the app.

    Used for serving the index page, that's all.
    """
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """The web socket handler.

    Open the file to read and send the messages back to the browser.
    """

    def __init__(self, application, request, **kwargs):
        super(WebSocketHandler, self).__init__(application, request, **kwargs)
        self.stream.set_nodelay(True)
        self.probe_file = None

    @property
    def executor(self):
        return self.settings["executor"]

    @tornado.gen.coroutine
    def open(self, *args, **kwargs):
        """Open the connection with the browser and maintain it."""
        future = yield self.executor.submit(self.read_file)
        self.write(future)

    def on_message(self, message):
        """Triggered when receiving a message."""
        # Not implemented.
        pass

    def on_close(self):
        """When the WebSocket connection on the browser is closed."""
        if all([self.probe_file, not self.probe_file.closed]):
            self.probe_file.close()

    def read_file(self):
        """Read the probe file and send back its content, line by line."""
        ret_msg = "Done"
        self.probe = self.get_argument("probe", None)
        if self.probe:
            self.probe_file_path = os.path.join(DATA_ROOT_PATH, self.probe)
            self._monitor_file()
        else:
            ret_msg = "No probe specified"
        return ret_msg

    def _monitor_file(self):
        """Monitor the filesystem for the file presence and read it."""
        while True:
            if os.path.exists(self.probe_file_path):
                try:
                    # Open the file and make sure it is non blocking.
                    self.probe_file = io.open(self.probe_file_path)
                    file_num = self.probe_file.fileno()
                    old_flags = fcntl.fcntl(file_num, fcntl.F_GETFL)
                    fcntl.fcntl(
                        file_num, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

                    for line in follow_probe_file(self.probe_file):
                        self.write_message(line)
                except Exception:
                    print (
                        "Something is wrong with the file %s" %
                        self.probe_file_path)
                finally:
                    self.probe_file.close()
            else:
                time.sleep(0.5)


application = tornado.web.Application(
    [
        (r"/$", MainHandler),
        (r"/websocket$", WebSocketHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_PATH})
    ],
    **SETTINGS
)


if __name__ == "__main__":
    try:
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        sys.exit(2)
