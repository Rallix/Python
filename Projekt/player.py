from console import fx
from console.style import ForegroundPalette
from dice import Dice
from typing import Optional, List


def flatten(array_of_arrays) -> List:
    """ Z pole polí vytvoří jednorozměrné pole."""
    return [item for sublist in array_of_arrays for item in sublist]


class Player:
    """Reprezentace jednoho z hráčů.
    Třída sama o sobě už příkazy nijak nekontroluje – o to by se měla starat Board."""

    def __init__(self, color: bool, piece_color: ForegroundPalette):
        self.color: bool = color  # barva hráče "černá"/"bílá"
        self.pieces = 15  # počet kamenů doposud mimo hru (tj. ty na hrací ploše jsou už odečteny)
        self.dice = Dice(6, 5)  # hráčova kostka (každé číslo 5×)
        self.must_reenter = 0  # počet kamenů, které je nutné opět vložit do hry než bude moci hrát
        self.turn = [0, 0, 0]  # hod kostkami během jednoho tahu
        self.path = [0 for _ in range(36)]  # oddělená cesta od začátku do konce pro jednoho hráče
        self.piece_color = piece_color  # barva hracích kamenů

    def get_path_sections(self, mirrored: bool, path: Optional[List[int]] = None) -> List[List[int]]:
        """
        24 _ _ _ _ 19  18 _ _ _ _ 12 ↓↓ ← ←
        01 _ _ _ _ 06  07 _ _ _ _ 12 → → ↑
        24 _ _ _ _ 30  31 _ _ _ _ 35 → → X
        """
        if not path:
            path = self.path
        if not mirrored:
            # Aktivní hráč (normální pohled)
            sections = [path[0:6],   path[6:12],
                        path[12:18], path[18:24],
                        path[24:30], path[30:36]]
        else:
            # Protihráč (sedí naproti: zrcadlově otočený 'šnek')
            ordered_sections = [path[6:12],  path[0:6],
                                path[24:30], path[30:36],
                                path[12:18], path[18:24]]
            first = ordered_sections[0]
            first.reverse()
            second = ordered_sections[1]
            second.reverse()
            sections = [first, second] + ordered_sections[2:6]
        return sections

    def get_opposing_index(self, index: int):
        """ Vrátí index toho samého pole z pohledu protihráče. """
        indices = flatten(self.get_path_sections(True, [i for i in range(36)]))
        return indices[index]

    def ready_to_take(self) -> bool:
        """ Zjistí, zda jsou všechny aktivní kameny hráče v závěrečné zóně, a lze je tedy sebrat. """
        non_ending = flatten(self.get_path_sections(False)[0:5])
        return not any(non_ending)

    def __str__(self):
        return f"{self.piece_color}Hráč {'I' if self.color else 'II'}{fx.end}"

    def count_active_pieces(self):
        """ Spočítá aktivní kameny na hrací ploše. """
        pieces_on_board = flatten(self.get_path_sections(False))
        return sum(pieces_on_board)

    def capture(self, square_index: int):
        """ Sebere tomuto hráči kámen na určité pozici (z pohledu protihráče). Pouze pokud je jeden. """
        index = self.get_opposing_index(square_index)  # převést index na vlastní
        self.path[index] -= 1
        self.must_reenter += 1

    def get_square(self, index: int):
        """ Vrátí počet kamenů hráče na daném poli. """
        return self.path[index]

    def get_opposing_square(self, index: int):
        """ Vrátí počet kamenů protihráče na daném poli. """
        opposing_path = flatten(self.get_path_sections(True))
        return opposing_path[index]

    def roll(self) -> List[int]:
        """"Hodí třemi kostkami."""
        self.turn = [self.dice.roll(), self.dice.roll(), self.dice.roll()]
        return self.turn

    def is_winner(self) -> bool:
        """ Zjistí, jestli hráč vyhrál hru – tj. nezbývají mu žádné kameny ve hře ani mimo ní."""
        pieces_on_board = flatten(self.get_path_sections(False))
        return self.pieces == 0 and self.must_reenter == 0 and not any(pieces_on_board)

    def apply_roll(self, number):
        """Využije jednu z kostek."""
        index = self.turn.index(number)
        self.turn[index] = 0

    def find_piece(self, piece: int) -> int:
        """Najde index pole kamene s určitým pořadovým číslem."""
        for i in range(len(self.path)):
            # Každý nalezený kámen se odečte od pořadí hledaného, tj. u nuly jsme našli ten správný
            piece -= self.path[i]
            if piece <= 0:
                return i + 1

    def place(self, square: int):
        """Vloží kámen do hry na zadanou počáteční pozici 1-6."""
        if self.must_reenter > 0:
            self.must_reenter -= 1
        else:
            self.pieces -= 1
        self.path[square - 1] += 1
        self.turn.remove(square)

    def move(self, piece: int, steps: int):
        """Pohne x-tým kamenem o určitý počet kroků."""
        square = self.find_piece(piece) - 1  # index pole od nuly
        self.path[square] -= 1
        self.path[square + steps] += 1
        self.turn.remove(steps)

    def take(self, square: int):
        """Sebere kámen na zadané koncové pozici 1-6."""
        self.path[-(6 - square) - 1] -= 1
        self.turn.remove(square)
