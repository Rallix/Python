import ssl
import json
import socket
import http.client
from http import HTTPStatus
from urllib import parse
from urllib import request as rq
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv

# TODO: Tic Tac Toe

if len(argv) != 2:
    exit("The program expects to be called with one command-line argument:\n"
         "./ttt.py 9001")
PORT = argv[1]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")
