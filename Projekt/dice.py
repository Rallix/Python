from shuffle_bag import ShuffleBag
from collections import Counter


class Dice(ShuffleBag):
    """Hrací kostka s náhodným výběrem metodou 'shuffle bag' (~ tahání žetonů z pytlíku)."""
    def __init__(self, sides: int, amount: int = 1):
        """Vytvoří hrací kostku.

        Keyword arguments:
        sides -- počet stran kostky (> 1)
        amount -- kolikrát se má každé číslo na kostce ve výběru opakovat (zvyšuje náhodnost, > 1)"""
        dice_values = list(range(1, sides + 1))
        super(Dice, self).__init__(dice_values * amount)

    def roll(self) -> int:
        """Hod kostkou."""
        return self.next()

    def __str__(self):
        counter = Counter(self.list)
        result = f"Dice ({len(counter.items())}): "
        numbers = []
        for key, value in sorted(counter.items()):
            numbers.append(f"{value}× {key}")
        print(numbers)
        return str(result + ', '.join(numbers))

