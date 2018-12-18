import json
from http import HTTPStatus
# from urllib import parse
from sys import argv
from os import getcwd
from os.path import *
# from urllib import request as rq
# from urllib.error import HTTPError, URLError
from socketserver import ThreadingMixIn
from http.server import CGIHTTPRequestHandler, HTTPServer


class ThreadedServer(ThreadingMixIn, HTTPServer):
    """Zpracovává požadavky ve vlastních vláknech."""


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
        # self.respond('HEAD')
        super()

    # --> výchozí metoda stačí
    # def run_cgi(self):
    #     """Runs the Common Gateway Interface file."""
    #     pass

    def respond(self, method):
        path = DIRECTORY
        if method == 'HEAD':
            raise NotImplementedError("Responding to the HEAD request is not supported.")
        elif method == 'GET':
            path = join(DIRECTORY, self.path)
        elif method == 'POST':
            # TODO: Proměnné prostředí
            length = self.headers['Content-Length']
            try:
                length = int(length)
            except ValueError:
                length = 0  # špatná hlavička… nemělo by nastat
            field_data = self.rfile.read(length).decode('utf8')
            # print(field_data)
            content = json.loads(field_data)
            keys = content.keys()
            if 'content' in keys:
                path = join(DIRECTORY, content['content'])
        if not isfile(path):
            return self.send_error(HTTPStatus.NOT_FOUND, f"File at '{path}' doesn't exist.")

        size = getsize(path)
        # print(f"Size {size}: {path}")
        if len(path) > 4 and path.lower()[-4:] == ".cgi":
            self.cgi_info = "", self.path[1:]
            self.run_cgi()
        else:
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Length', size)
            self.end_headers()
            with open(path, 'rb') as FILE:
                fc = FILE.read()
                # print(fc)
                self.wfile.write(fc)


def get_relpath(directory):
    """Vrátí relativní umístění určité složky v ohledu na současnou pracovní složku."""
    return relpath(directory, getcwd())


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./serve.py 9001 dir")

DIRECTORY = get_relpath(abspath(argv[2]))  # CGI složka – přes HTTP
PORT = argv[1]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")

server = ThreadedServer(('', PORT), CGIHandler)
try:
    # print(f'Started httpserver on port {PORT}.\n')
    server.serve_forever()  # odpovídat na příchozí požadavky
except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
