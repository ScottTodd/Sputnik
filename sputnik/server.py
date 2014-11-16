"""Sputnik HTTPServer Implementation

This module provides the Sputnik HTTPServer implementation. It is responsible
for serving the web interface, and interfaces with the Bouncer singleton to
connect to and disconnect from networks.
"""

import os
import handlers
import tornado.web
import tornado.httpserver
import tornado.platform.asyncio


class HTTPServer(tornado.web.Application):
    """An Asynchronous HTTP Server that diplays the frontend.

    The HTTPServer renders the frontend and accepts commands used to control
    the Bouncer singleton. For development purposes, it may be helpful to set
    the DEBUG environment variable. e.g. `export DEBUG=True`
    """

    def __init__(self):
        """Creates an instance of an HTTPServer.

            Defines the available routes and initializes the server using the
            static path and template path specified within.
        """

        routes = [(r"/edit", handlers.EditHandler),
                  (r"/",     handlers.MainHandler)]

        tornado.platform.asyncio.AsyncIOMainLoop().install()
        super().__init__(debug=os.environ.get("DEBUG"),
                         handlers=routes,
                         static_path="static",
                         template_path="templates")

    def start(self, port=8080):
        """Starts the HTTP listen server.

        This loads the Tornado HTTPServer on the specified port.

        Args:
            port (int, optional): The port to listen on. Defaults to 8080
        """

        tornado.httpserver.HTTPServer(self).listen(port)