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
    2: 'o'
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


async def play(ttt, player, game_id: int):
    sign = BOARD_SYMBOLS[player]
    while True:
        col, found, row = input(f"your turn ({sign}): ").strip().partition(' ')
        try:
            if not found:
                raise ValueError
            x = int(col)
            y = int(row)
            turn = await ask(ttt, f"play?game={game_id}&player={player}&x={x}&y={y}")
            if turn['status'] == 'bad':
                raise ValueError
            break
        except ValueError:
            print("invalid input")
            continue


async def forever():
    """Hlavní herní smyčka. Rozděleno na fáze."""
    async with aiohttp.ClientSession() as ttt:
        phase = 0  # Jednotlivé fáze hry
        while True:
            if GAME_PHASES[phase] == 'NEW_GAME':
                """Zobrazovat seznam volných her a umožnit připojení."""
                game_list = await ask(ttt, "list")
                open_ids = []
                for game in game_list:
                    open_ids.append(game['id'])
                if open_ids:  # Otevřené hry
                    to_remove = []
                    for gid in open_ids:
                        stats = await ask(ttt, f"status?game={gid}")
                        if not ("board" in stats and is_board_empty(stats['board'])):
                            to_remove.append(gid)  # Neprázdná hra – smazat
                    open_ids = [i for i in open_ids if i not in to_remove]
                if not open_ids:  # Žádná otevřená hra
                    print("No game is currently open. Try starting a new one: 'new [name]'.")
                else:
                    print("Try starting a new game ('new [name]') or join an existing one ('<id>'): ")
                    for gid in open_ids:
                        game_name = f" {game['name']}" if game['name'] else ''
                        print(f"{gid}{game_name}")
                cmd, found, name = input().strip().partition(' ')  # TODO: Když se otevře hra, zatímco se čeká na input
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
                        print(f"Invalid input '{cmd}' – a numeric game ID expected.")
                waiting_message = True  # čekání na protihráče (vypsat jednou)
            if GAME_PHASES[phase] == 'PLAY':
                """Samotná hra: Polling + Tahy"""
                status = await ask(ttt, f"status?game={game_id}")
                if 'winner' in status:
                    if status['winner'] != player:
                        board = await show_board(ttt, game_id)
                        print(board)
                    if status['winner'] == 0:
                        # TODO: Při remíze hrací plocha zobrazená dvakrát
                        print("draw")  # Remíza
                    elif status['winner'] == player:
                        print("you win")  # Vítězství
                    else:
                        print("you lose")  # Prohra
                    phase += 1

                elif status['next'] == player:
                    board = await show_board(ttt, game_id)
                    print(board)

                    # TODO: Zakázat hrát bez protihráče
                    await play(ttt, player, game_id)

                    board = await show_board(ttt, game_id)
                    print(board)
                    waiting_message = True
                elif waiting_message:
                    # opponent = 2 if player == 1 else 1
                    print(f"waiting for the other player")
                    waiting_message = False
                await sleep(WAITING_INTERVAL)
            if GAME_PHASES[phase] == 'END':
                exit(0)  # Zavřít celou hru


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
