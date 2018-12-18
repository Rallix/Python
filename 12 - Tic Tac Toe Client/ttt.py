import re
import json
from http import HTTPStatus
from urllib import parse
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class TicTacToeHandler(BaseHTTPRequestHandler):
    """Handle TicTacToe requests."""
    games = dict()
    index = -1  # ! TicTacToeHandler.index, NOT self.index
    mimetype = 'application/json'

    def do_GET(self):
        url = self.path
        # print(url)

        mode, found, params = url.partition('?')
        mode = re.sub('^\W*', '', mode)  # odstranit všechnu bagáž ze začátku
        params = parse.parse_qs(params)  # {'key' : ['value',…]}
        # print(f"{mode}: {params}")
        if not mode:
            return self.send_error(HTTPStatus.BAD_REQUEST, f"No request provided. Try 'start', 'status' or 'play'.")
        if not found and mode != 'list':
            if mode == 'start':
                params = {'name': ['']}  # výchozí jméno
            else:
                return self.send_error(HTTPStatus.BAD_REQUEST, f"No params were provided for request '{mode}'.")
        try:
            request = getattr(self, mode)  # get the function with 'mode' name
            request(params)
        except AttributeError:
            self.send_error(HTTPStatus.BAD_REQUEST, f"Asking for a non-existent request '{mode}'.")

    def start(self, params):
        try:
            if 'name' not in params:
                raise KeyError
            name = params['name'][0]
            new_game = {'name': name,
                        'board': [[0, 0, 0],
                                  [0, 0, 0],
                                  [0, 0, 0]],
                        'next': 1,
                        'winner': None}
            TicTacToeHandler.index += 1  # Zvýšit index pro vytvoření další hry
            TicTacToeHandler.games[TicTacToeHandler.index] = new_game
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', self.mimetype)
            self.end_headers()
            self.wfile.write(bytes(json.dumps({'id': TicTacToeHandler.index}), 'utf-8'))
        except KeyError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Unknown parameter, expecting 'name'.")

    def status(self, params):
        try:
            if 'game' not in params:
                raise KeyError
            try:
                idx = int(params['game'][0])
                game = self.games[idx]
                # print(game)
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', self.mimetype)
                self.end_headers()
                if game['winner']:
                    result = {'board': game['board'], 'winner': game['winner']}
                else:
                    result = {'board': game['board'], 'next': game['next']}
                self.wfile.write(bytes(json.dumps(result), 'utf-8'))
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST, "The game parameter expects its value ID to be numeric.")
            except (KeyError, IndexError):
                self.send_error(HTTPStatus.NOT_FOUND, "Entered an ID of a non-existent game.")
        except KeyError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Unknown parameter, expecting 'game'.")

    def play(self, params):
        try:
            idx = int(params['game'][0])
            player = int(params['player'][0])
            row = int(params['y'][0])  # vertikálně jsou řádky
            col = int(params['x'][0])  # horizontálně jsou sloupce
            game = TicTacToeHandler.games[idx]

            result = dict()
            result['status'] = 'bad'  # Výchozí: špatně
            result['message'] = 'Unknown state.'
            # Ověření
            if game['winner'] is not None:
                # print(f"Winner: Player {game['winner']}")
                result['message'] = "The game already has a winner."
            elif game['next'] != player:
                result['message'] = f"It's not currently player {player}'s turn.'"
            elif not (0 <= row <= 2 and 0 <= col <= 2):
                result['message'] = "The given zero-based coordinates are out of the 3x3 game board."
            elif game['board'][row][col] != 0:
                result['message'] = f"The required field is not blank."
            else:
                # Validní tah
                result['status'] = 'ok'
                result['message'] = f"Player {player} made a valid move at {col}x{row}."
                game['board'][row][col] = player
                game['next'] = 1 if player == 2 else 2  # předpokládá správnost
                game['winner'] = self.decide_winner(game['board'])

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', self.mimetype)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(result), 'utf-8'))
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Some of the passed parameters aren't numeric.")
        except TypeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Some of the required parameters for 'play' are missing.")
        except (KeyError, IndexError):
            # game = self.games[idx]
            self.send_error(HTTPStatus.NOT_FOUND, "Entered an ID of a non-existent game.")

    def list(self, params):
        gamelist = []
        for key, value in self.games.items():
            gamelist.append({'id': key, 'name': value['name']})
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', self.mimetype)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(gamelist), 'utf-8'))

    @staticmethod
    def decide_winner(board):
        """Zjistí vítěze hry z pole 3x3 – nebo remízu."""
        # Řádky
        for row in board:
            if 0 in row:
                continue
            player = row[0]  # první pole řádku
            if row[1] == player and row[2] == player:
                # print('row win')
                return player  # zbylá dvě pole se shodují
        # Sloupce
        for i in range(3):
            col = [board[0][i], board[1][i], board[2][i]]
            if 0 in col:
                continue
            player = col[0]  # první pole sloupce
            if col[1] == player and col[2] == player:
                # print('col win')
                return player  # zbylá dvě pole se shodují
        # Diagonály
        dia1 = [board[0][0], board[1][1], board[2][2]]
        dia2 = [board[0][2], board[1][1], board[2][0]]
        for dia in [dia1, dia2]:
            if 0 in dia:
                continue
            player = dia[0]  # první pole diagonály
            if dia[1] == player and dia[2] == player:
                # print('dia win')
                return player  # zbylá dvě pole se shodují
        # Remíza
        flatten = lambda l: [item for sublist in l for item in sublist]
        if 0 in flatten(board):  # [[0,1,0],[2,0,0],[0,0,1]] --> [0,1,0,2,0,0,0,0,1]
            return None  # Zbývají volná pole
        else:
            # print('draw')
            return 0  # Remíza


def run():
    if len(argv) != 2:
        exit("The program expects to be called with one command-line argument:\n"
             "./ttt.py 9001")
    PORT = argv[1]
    try:
        PORT = int(PORT)
    except ValueError:
        exit("The PORT number must be a valid integer.")

    server = ThreadedHTTPServer(('', PORT), TicTacToeHandler)  # "multiple games may run in parallel"
    try:
        # print(f'Started httpserver on port {PORT}.')
        server.serve_forever()  # odpovídat na příchozí požadavky
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()


if __name__ == "__main__":
    run()
