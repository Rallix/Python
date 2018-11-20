import ssl
import http.client
from sys import argv
from urllib import request
from http.server import BaseHTTPRequestHandler, HTTPServer


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./http-forward.py 9001 hostname")

HOST_NAME = argv[2]
PORT = argv[1]

