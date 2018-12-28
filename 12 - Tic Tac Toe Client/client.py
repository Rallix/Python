import json
import aiohttp
import asyncio
from asyncio import sleep
from http import HTTPStatus
from sys import argv

WAITING_INTERVAL = 1  # ptát se ~jednou za vteřinu
BOARD_SYMBOLS = {
    0: '_',
    1: 'x',
    2: 'y'
}
GAME_PHASES = {
    0: 'NEW_GAME',
    1: 'PLAY',
    2: 'END'
}


def is_board_empty(board):
    """Zjistí, jestli je hrací pole úplně prázdné, t.j. nová hra."""
    flatten = lambda l: [item for sublist in l for item in sublist]
    return all(field == 0 for field in flatten(board))


async def wait():
    """Uspí async funkce na globálně stanovenou dobu."""
    await sleep(WAITING_INTERVAL)


async def ask(ttt, request: str):
    """Zavolá požadavek na TicTacToe server a získá odpověď jako JSON."""
    request_url = f"{FULL_ADDRESS}/{request}"  # Např. http://localhost:9001/status?game=0
    async with ttt.get(request_url) as response:
        assert response.status == HTTPStatus.OK
        content = await response.text()
        return json.loads(content)


async def show_board(ttt, game_id: int):
    """Vrátí herní plochu v čitelném formátu."""
    status = await ask(ttt, f"status?game={game_id}")
    full_board = []
    for row in status['board']:  # každý řádek
        board_row = ""
        for field in row:  # každé políčko
            board_row += str(BOARD_SYMBOLS[field])  # postupně doplňovat
        full_board.append(board_row)
    return "\n".join(full_board)  # odřádkovat řádky


async def forever():
    """Hlavní herní smyčka. Rozděleno na fáze."""
    async with aiohttp.ClientSession() as ttt:
        phase = 0  # Jednotlivé fáze hry
        while True:
            if GAME_PHASES[phase] == 'NEW_GAME':
                """Zobrazovat seznam volných her a umožnit připojení."""
                game_list = await ask(ttt, "list")
                # print(game_list)
                open_ids = []
                for game in game_list:
                    open_ids.append(game['id'])
                if not open_ids:  # Žádná otevřená hra
                    print("No game is currently open. Try starting a new one: 'new [name]'.")
                else:  # Otevřené hry
                    for gid in open_ids:
                        stats = await ask(ttt, f"status?game={gid}")
                        if "board" in stats and is_board_empty(stats['board']):
                            print(f"Open game '{game['name']}' with ID: {gid}")  # TODO: Zobrazit instrukce u protihráče
                cmd, found, name = input().strip().partition(' ')
                game_id = -1
                if cmd == 'new':
                    # Požadavek na založení nové hry
                    with_name = ''
                    if found:
                        with_name = f'?name={name}'
                    response = await ask(ttt, f"start{with_name}")

                    game_id = response['id']
                    player = 1
                    phase += 1  # Založena nová hra, přejít do fáze čekání na protihráče
                else:
                    # Připojení se ke hře
                    try:
                        game_id = int(cmd)
                        if game_id not in open_ids:
                            print(f"There's no open game with ID {game_id}.")
                            continue
                        player = 2
                        phase += 1  # Připojeno k otevřené hře jako hráč '2', už se hraje
                    except ValueError:
                        print(f"Invalid input '{game_id}' – a numeric game ID expected.")
                keep_waiting = True  # čekání na protihráče (vypsat jednou)
            if GAME_PHASES[phase] == 'PLAY':
                """Samotná hra: Polling + Tahy"""
                # print('Playing!')
                status = await ask(ttt, f"status?game={game_id}")
                if 'winner' in status:
                    if status['winner'] != player:
                        # Zobrazit hrací plochu pro protihráče
                        pass  # TODO: Zobrazit hrací plochu
                    if status['winner'] == 0:
                        print("draw")  # Remíza
                    elif status['winner'] == player:
                        print("you win")  # Vítězství
                    else:
                        print("you lose")  # Prohra

                elif status['next'] == player:
                    # TODO: Zobrazit hrací plochu
                    # TODO: Čekat na tah
                    keep_waiting = True
                elif keep_waiting:
                    opponent = 2 if player == 1 else 1
                    print(f"Waiting for player {opponent}'s turn.")
                await sleep(WAITING_INTERVAL)
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
