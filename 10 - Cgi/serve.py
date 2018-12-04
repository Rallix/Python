import json
import socket
import inspect
import http.client
from http import HTTPStatus
from urllib import parse
from urllib import request as rq
from urllib.error import HTTPError, URLError
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer, CGIHTTPRequestHandler
from sys import argv


class ThreadedServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class CGIHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        """The GET method indicates that the script should produce a document
        based on the meta-variable values.  By convention, the GET method is
        'safe' and 'idempotent' and SHOULD NOT have the significance of
        taking an action other than producing a document.

        The meaning of the GET method may be modified and refined by
        protocol-specific meta-variables."""
        self.respond('GET')

    def do_POST(self):
        """The POST method is used to request the script perform processing and
        produce a document based on the data in the request message-body, in
        addition to meta-variable values.  A common use is form submission in
        HTML, intended to initiate processing by the script that has a
        permanent affect, such a change in a database.

        The script MUST check the value of the CONTENT_LENGTH variable before
        reading the attached message-body, and SHOULD check the CONTENT_TYPE
        value before processing it."""
        self.respond('POST')

    def do_HEAD(self):
        """The HEAD method requests the script to do sufficient processing to
        return the response header fields, without providing a response
        message-body.  The script MUST NOT provide a response message-body
        for a HEAD request.  If it does, then the server MUST discard the
        message-body when reading the response from the script."""
        self.respond('HEAD')

    def run_cgi(self):
        """Runs the Common Gateway Interface file."""
        pass

    def respond(self, method='GET'):
        j = dict()
        request_path = parse.urlparse(self.path).path[1:]
        j["path"] = request_path
        print(j)
        self.wfile.write(bytes(json.dumps(j), 'utf-8'))  # A bytes-like object…
        pass


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./serve.py 9001 dir")
DIRECTORY = argv[2]  # CGI složka – přes HTTP
PORT = argv[1]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")

server = ThreadedServer(('', PORT), CGIHandler)
try:
    print(f'Started httpserver on port {PORT}.\n')
    server.serve_forever()  # odpovídat na příchozí požadavky
except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
