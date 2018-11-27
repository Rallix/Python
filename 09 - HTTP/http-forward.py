import ssl
import json
import socket
import http.client
from http import HTTPStatus
from urllib import parse
from urllib import request as rq
from urllib.error import HTTPError
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv


def pretend_timeout():
    """Nasimuluje vypršení časového limitu."""
    print('-- Simulating a sever timeout.')
    raise socket.timeout


# noinspection PyPep8Naming
class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # print(self.headers)
        headers = dict(self.headers)
        get = rq.Request(method="GET", headers=headers, url=HOST_NAME, data=None)
        self.respond(get, timeout=1)

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        field_data = self.rfile.read(length).decode('utf8')
        # fields = parse.parse_qs(field_data)
        # print(field_data)
        j = dict()
        try:
            content = json.loads(field_data)
            keys = content.keys()
            if 'type' not in keys:
                # TODO: Metoda 'respond' typ do výstupu ovšem nepřidává… Ok?
                content['type'] = 'GET'  # default (OK)

            if content['type'].upper() == 'POST':
                if 'url' not in keys or 'content' not in keys:
                    raise ValueError  # chybí url, content pro POST
            elif content['type'].upper() == 'GET':
                content['content'] = None
            elif content['type'].upper() not in ['GET', 'POST']:
                raise ValueError  # nepodporovaný request

            if 'headers' not in keys:
                content['headers'] = None
            if 'timeout' not in keys:
                content['timeout'] = 1
            post = rq.Request(
                method=content['type'],
                headers=content['headers'],
                url=content['url'],
                data=content['content']
            )
            self.respond(post, timeout=content['timeout'])
        except ValueError:
            # Chybný formát => string 'content'
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            j['code'] = 'invalid json'
            self.wfile.write(bytes(json.dumps(j), 'utf-8'))  # A bytes-like object…

    def respond(self, request, timeout=1):
        """Zapíše odpověď serveru z požadavků."""
        j = dict()
        mimetype = 'application/json'
        try:
            with rq.urlopen(url=request.get_full_url(), timeout=timeout) as response:
                self.send_response(code=HTTPStatus.OK)  # or response.getcode()
                self.send_header('Content-type', mimetype)
                self.end_headers()
                j['code'] = response.getcode()
                j['headers'] = dict(response.getheaders())
                data = response.read()
                try:
                    # Validní json => 'json'
                    j['json'] = json.loads(data.decode('utf-8'))
                except ValueError:  # 'Easier to Ask for Forgiveness than Permission'
                    # Chybný formát => string 'content'
                    j['content'] = data.decode('utf-8')
        except HTTPError as he:
            print(f"{he.url} ({he.code}): {he.msg}")
        except socket.timeout:
            # 408 HTTPStatus.REQUEST_TIMEOUT
            self.send_response(code=HTTPStatus.REQUEST_TIMEOUT)
            self.send_header('Content-type', mimetype)
            self.end_headers()
            j['code'] = 'timeout'
        finally:
            # ↓ TODO: A bytes-like object is required… (~ bytes + utf-8)
            self.wfile.write(bytes(json.dumps(j), 'utf-8'))


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./http-forward.py 9001 example.com")
HOST_NAME = argv[2]  # upstream
if not HOST_NAME.startswith('http://') or HOST_NAME.startswith('https://'):
    HOST_NAME = f"http://{HOST_NAME}"

PORT = argv[1]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")

server = HTTPServer(('', PORT), WebHandler)
try:
    # print(f'Started httpserver on port {PORT}.\n')
    server.serve_forever()  # odpovídat na příchozí požadavky
except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
