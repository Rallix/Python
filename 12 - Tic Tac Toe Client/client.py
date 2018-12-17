import re
import json
import aiohttp
import asyncio
from http import HTTPStatus
from urllib import parse
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv


if len(argv) != 3:
    exit("The program expects to be called with one command-line argument:\n"
         "./client.py host 9001")

HOST_NAME = argv[2]  # upstream
if not HOST_NAME.startswith('http://') or HOST_NAME.startswith('https://'):
    HOST_NAME = f"http://{HOST_NAME}"

PORT = argv[1]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")

server = ThreadedHTTPServer(('', PORT), TicTacToeHandler)  # "multiple games may run in parallel"
try:
    print(f'Started httpserver on port {PORT}.')
    server.serve_forever()  # odpovídat na příchozí požadavky
except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
