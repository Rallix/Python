from console import fx, fg
from console.style import ForegroundPalette
from console.utils import cls
from typing import List, Optional
from random import randint
from player import Player
from string import ascii_uppercase

# Zobrazení abecedy, pokud v konzoli nefungují barvy
ALPHABET_MODE = True


def not_blank(string: str) -> bool:
    """Zjistí, zda je řetězec neprázdný."""
    return string and not string.isspace()


def flatten(array_of_arrays) -> List:
    """Z pole polí vytvoří jednorozměrné pole."""
    return [item for sublist in array_of_arrays for item in sublist]


def print_col(value: str, colour: Optional[ForegroundPalette] = None):
    """ Vypíše hodnotu do konzole barevně. """
    if not colour:
        print(value, sep='', end='')
    else:
        print(colour, value, fx.end, sep='', end='')


class Board:
    """Hrací deska, která obsluhuje interakci mezi hráči a schvaluje tah."""
    def __init__(self, pieces: Optional[int] = 15):
        self.player1 = Player(True, fg.lightyellow)  # Hráč I ("bílý")
        self.player2 = Player(False, fg.lightgreen)  # Hráč II ("černý")
        self.active = self.player1 if randint(1, 2) == 1 else self.player2  # Který hráč je zrovna na tahu?
        self.opponent = self.player1 if self.active == self.player2 else self.player2  # Protihráč
        self.winner = None
        if pieces < 1:
            pieces = 1  # minimum pro hru je alespoň jeden kámen
        self.player1.pieces = pieces
        self.player2.pieces = pieces

    def col_wrap(self, value: object, player: Optional[Player] = None) -> str:
        """ Obarví řetězec barvou (aktivního) hráče. """
        if not player:
            player = self.active
        return f"{player.piece_color}{value}{fx.end}"

    def display(self, player: Player = None):
        """ Vypíše stav hrací desky z pohledu aktivního (nebo vybraného) hráče. """
        if not player:
            player = self.active
        active, opponent = (self.player1, self.player2) if player == self.player1 else (self.player2, self.player1)
        active_path = active.get_path_sections(False)
        opponent_path = opponent.get_path_sections(True)
        for section in [2, 0, 4]:
            active_line = flatten(active_path[section:section+2])
            opponent_line = flatten(opponent_path[section:section+2])
            if section == 2:
                # Druhá řada (= první řádek výpisu) se prochází zprava doleva
                active_line.reverse()
                opponent_line.reverse()
            for i in range(12):
                if active_line[i] > 0:
                    if ALPHABET_MODE and not active.color:
                        print_col(list(ascii_uppercase)[active_line[i] - 1], active.piece_color)
                    else:
                        print_col(active_line[i], active.piece_color)  # počet kamenů hráče barevně
                elif opponent_line[i] > 0:
                    if ALPHABET_MODE and not opponent.color:
                        print_col(list(ascii_uppercase)[opponent_line[i] - 1], opponent.piece_color)
                    else:
                        print_col(opponent_line[i], opponent.piece_color)  # počet kamenů protihráče barevně
                else:
                    print_col("_")  # neobsazené pole
                if i != 11:
                    print_col(' ')  # mezera mezi kameny
                if i == 5:
                    print_col(' ')  # mezera v půlce pro přehlednost
            print()

    def play(self) -> Player:
        """ Celý jeden průběh hry. """
        cls()
        print("Povolené akce:\n")
        self.display_available_actions(self.active)
        print()
        while not self.winner:
            self.play_turn()
            self.end_turn()
        return self.winner

    def end_turn(self):
        """ Přepne status aktivního hráče. """
        active = self.active
        self.active = self.opponent
        self.opponent = active
        print()  # cls()

    @staticmethod
    def display_available_actions(player: Player):
        """ Vypíše možné akce. """
        # col_turn = ", ".join([f"{player.piece_color}{die}{fx.end}" for die in player.turn])
        print_col("place <startovní pole>", player.piece_color)
        print(f" umístí kámen na startovní pole")
        print_col("move <kolikátý kámen> <o kolik>", player.piece_color)
        print(f" přesune kámen s určitým pořadovým číslem od začátku")
        print_col("take <koncové pole>", player.piece_color)
        print(f" odebere kámen ze hry")
        print_col("pass", fg.lightcyan)
        print(f" přeskočí tah, není-li možné využít všechny kostky")
        print_col("yield", fg.lightred)
        print(f" vzdá současnou hru, čímž zvítězí protihráč")

    def is_square_occupied(self, square_index: int) -> int:
        """ Zjistí, zda je políčko už obsazené protihráčem. """
        return self.opponent.get_opposing_square(square_index)

    @staticmethod
    def get_piece_string(pieces: int) -> str:
        """ Vrátí gramaticky správné množné číslo počtu kamenů. """
        if pieces == 1:
            return f"{pieces} kámen"
        elif 1 < pieces < 5:
            return f"{pieces} kameny"
        else:
            return f"{pieces} kamenů"

    def play_turn(self):
        """ Kompletní tah jednoho hráče. """
        ACTIONS = ["place", "move", "take", "pass", "yield"]
        # Výpisy a příprava
        player = self.active
        print(player)
        # self.display_available_actions(player)  # výpis povolených akcí
        player.roll()
        while player.turn:

            ''' Tah jednoho hráče '''
            # Tři kostky – tři akce
            self.display(player)
            dice_rolls = ', '.join([f'{self.col_wrap(roll, player)}' for roll in player.turn])
            print(f"\nHod kostkou: {dice_rolls}")
            if player.must_reenter:
                print(f"Je nutné nejprve vložit do hry {self.col_wrap(self.get_piece_string(player.must_reenter), player)}.")
            print()

            while True:
                ''' Výběr akce '''
                if not player.turn:
                    break  # využity všechny kostky → hraje další hráč
                try:
                    action, found, rest = input(f"Zvolte akci: {player.piece_color}").strip().partition(' ')
                finally:
                    print(fx.end, sep='', end='')  # Pro případ 'KeyboardInterrupt'; ukončení barevného módu
                if action not in ACTIONS:
                    if not_blank(action):
                        print(f"\nNeplatná akce '{self.col_wrap(action, player)}'. Povolené akce jsou:\n")
                        self.display_available_actions(player)
                        print()
                    continue
                if action == "yield":
                    self.winner = self.opponent
                    return
                if action == "pass":
                    if not_blank(rest):
                        print(f"\nAkce '{self.col_wrap(action, player)}' nebere žádné další argumenty.")
                        continue
                    player.turn = []
                    break  # není možné tah dokončit (blokovaná pole apod.), tak hráč přeskočí tah
                if player.must_reenter > 0 and action != "place":
                    print(f"Je nutné nejprve vložit do hry {self.col_wrap(self.get_piece_string(player.must_reenter), player)}.")
                    continue
                if action == "place" or action == "take":
                    # Jedno číslo
                    try:
                        roll = int(rest.strip())
                    except ValueError:
                        print(f"Akce {self.col_wrap(action, player)} musí být následována jediným číslem.")
                        continue
                    if roll not in player.turn:
                        print(f"Je nutné zvolit jedno z čísel hozených na kostce: {dice_rolls}")
                        continue

                    if action == "place":
                        # Zbývají ještě nějaké?
                        if player.pieces <= 0 and player.must_reenter <= 0:
                            print("Nelze umístit další kameny, protože už žádné nezbývají.")
                            continue
                        # Je na políčku jiný hráč?
                        occupied = self.is_square_occupied(roll - 1)
                        if occupied > 1:
                            print(f"Nelze umístit kámen na dané místo, jelikož jej blokuje protihráč.")
                            continue
                        elif occupied == 1:
                            self.opponent.capture(roll - 1)  # Sebrat protihráčův kámen
                            print(f"Sebrán {self.col_wrap('kámen', self.opponent)} protihráče.")
                        player.place(roll)
                    if action == "take":
                        if not player.ready_to_take():
                            print("Před odebráním kamenů ze hry musí být všechny aktivní v závěrečné zóně.")
                            continue
                        if not player.path[-(6 - roll) - 1]:
                            print("Na uvedeném poli se nenachází žádný váš kámen.")
                            continue
                        player.take(roll)
                        print(f"Zbývá {self.col_wrap(self.get_piece_string(player.pieces), player)}.")
                        if player.is_winner():
                            # Odebrány všechny kameny ze hry, hráč vítězí
                            self.winner = player
                            return
                elif action == "move":
                    # Dvě čísla
                    try:
                        id_roll = [int(x) for x in rest.split()]
                        if len(id_roll) != 2:
                            raise ValueError
                        piece_id, roll = id_roll
                    except ValueError:
                        print(f"Akce {self.col_wrap(action, player)} musí být následována dvěma čísly.")
                        continue
                    if roll not in player.turn:
                        print(f"Je nutné zvolit jedno z čísel hozených na kostce: {dice_rolls}")
                        continue
                    # Zvolený kámen existuje
                    sum_pieces = player.count_active_pieces()
                    if piece_id > sum_pieces:
                        print(f"Nelze pohnout {self.col_wrap(f'{piece_id}. kamenem')}, "
                              f"protože na herním plánu {'jsou' if 1 < sum_pieces < 5 else 'je'} "
                              f"{'jen ' if sum_pieces else ''}{self.col_wrap(self.get_piece_string(sum_pieces), player)}.")
                        continue
                    # Mimo hrací plán
                    square_index = (player.find_piece(piece_id) - 1) + roll
                    if square_index > 35:
                        print(f"Nelze pohnout kamenem za hranice hrací desky.")
                        continue
                    # Neblokováno protihráčem?
                    occupied = self.is_square_occupied(square_index)
                    if occupied > 1:
                        print(f"Nelze umístit kámen na dané místo, jelikož jej blokuje protihráč.")
                        continue
                    elif occupied == 1:
                        self.opponent.capture(square_index)  # Sebrat protihráčův kámen
                        print(f"Sebrán {self.col_wrap('kámen', self.opponent)} protihráče.")

                    player.move(piece_id, roll)
                if not player.turn:
                    self.display(player)  # zobrazit tah
                break  # úspěšná akce – vypsat hrací plán po provedení tahu
