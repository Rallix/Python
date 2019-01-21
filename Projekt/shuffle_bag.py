import random
from typing import List


class ShuffleBag(object):
    """Pseudonáhodné hody kostkou nejsou ve hrách spravedlivé - shuffle bag hodnoty rozmístí víceméně rovnoměrně.
    Tj. pokud hráč hodí např. 10x jedničku, už nemůže hodit další dokud nehodí 10x všechna ostatní čísla."""
    def __init__(self, values: List):
        self.values = values
        self.list = None
        self.shuffle()

    def next(self):
        if self.list is None or len(self.list) == 0:
            self.shuffle()
        return self.list.pop()

    def shuffle(self):
        self.list = self.values[:]
        random.shuffle(self.list)
