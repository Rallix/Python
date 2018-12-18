import json
import aiohttp
import asyncio
# from http import HTTPStatus
from sys import argv

import ttt


async def forever():
    
    pass

if len(argv) != 3:
    exit("The program expects to be called with one command-line argument:\n"
         "./client.py host 9001")

HOST_NAME = argv[1]
if not HOST_NAME.startswith('http://') or HOST_NAME.startswith('https://'):
    HOST_NAME = f"http://{HOST_NAME}"

PORT = argv[2]
try:
    PORT = int(PORT)
except ValueError:
    exit("The PORT number must be a valid integer.")

FULL_ADDRESS = f"{HOST_NAME}:{PORT}"

event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(forever())
finally:
    event_loop.close()
