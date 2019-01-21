# -*- coding: utf-8 -*-
import sys

from console import fg, fx
from console.utils import cls, set_title

from board import Board

MAIN_MENU = {1: "Nová hra (15 kamenů)", 2: "Nová hra (3 kameny)", 3: "Pravidla", 4: "Konec"}
DEFAULT_PIECES = 15  # pro zrychlenou hru např. 3


def display_main_menu() -> int:
    """Zobrazí hlavní herní nabídku."""
    print(fg.lightgreen, 'Ludus duodecim scriptorum', fx.end)
    print()
    for key, value in MAIN_MENU.items():
        print(f"{fg.lightcyan}{key}{fx.end}   {fx.bold}{value}{fx.end}")
    print()
    option = None
    options = list(MAIN_MENU.keys())
    while not option or option not in options:
        try:
            option = int(input(f'Zvolte {", ".join([f"{fg.lightcyan}{i}{fx.end}" for i in options])}: '))
        except ValueError:
            pass
    return option


''' Hlavní menu '''
cls()
set_title('Ludus duodecim scriptorum')
menu_option = None
while menu_option != 4:
    menu_option = display_main_menu()
    if menu_option == 1 or menu_option == 2:
        ''' Průběh hry'''
        pieces = DEFAULT_PIECES if menu_option == 1 else 3
        board = Board(pieces)
        winner = board.play()
        print(f"\n{winner.piece_color}{winner}{fx.end} se stává vítězem!")
        print(f"\n\nStiskněte {fg.lightgreen}Enter{fx.end} pro návrat do menu.")
        sys.stdin.readline()
    elif menu_option == 3:
        ''' Pravidla '''
        cls()
        print(fg.lightgreen, fx.underline, "Pravidla", fx.end)
        print()
        print(f'{fg.lightyellow}1.{fx.end}', "Ludus duodecim scriptorum je hra pro dva hráče na desce o třech řádcích o dvanácti polích, přičemž každá řada je rozdělená v půlce.")
        print(f'{fg.lightyellow}2.{fx.end}', "Každý hráč má patnáct kamenů své vlastní barvy, žluté nebo zelené. Na začátku hry jsou všechny kameny mimo hrací desku.")
        print(f'{fg.lightyellow}3.{fx.end}', "Pohyb kamenů určují tři šestistranné kostky.")
        print(f'{fg.lightyellow}4.{fx.end}', "Začínající hráč je vybrán náhodně.")
        print(f'{fg.lightyellow}5.{fx.end}', "Hráč započne svůj tah hozením kostkami. Ty může použít v libovolném pořadí, a s každou hozenou číslicí provést jedno z následujícího:")
        print("  ", fg.lightgreen, "i.", fx.end, "kámen čekající na vložení do hry lze umístit na odpovídající pozici 1-6 na začátku své trasy (prostřední řádek vlevo)")
        print("  ", fg.lightgreen, "ii.", fx.end, "kámen na hrací desce se může pohnout o odpovídající počet míst podél trasy")
        print("  ", fg.lightgreen, "iii.", fx.end, "pokud se všechny aktivní kameny hráče nachází na konci trasy (I-VI), může se odpovídající kámen ze hry odebrat")
        print("  ", fg.lightgreen, "iv.", fx.end, "pokud byl kámen sebrán, musí být opět uveden do hry na pozici 1-6, dřív než bude možné hýbat s jiným kamenem.")
        print(f'{fg.lightyellow}6.{fx.end}', "Kameny stejné barvy lze skládat na sebe, do libovolné výšky.")
        print(f'{fg.lightyellow}7.{fx.end}', "Kámen nelze přesunout na pozici, kde se již nachází dva a více kamenů protihráče.")
        print(f'{fg.lightyellow}8.{fx.end}', "Osamocený kámen na poli je sebrán, pokud na něj protihráč přesune ten svůj. Sebraný kámen je odebrán ze hrací desky a jeho majitel jej musí na začátku svého tahu umístit do hry dřív, než pohne jiným kamenem.")
        print(f'{fg.lightyellow}9.{fx.end}', "Hra končí ve chvíli, kdy jeden z hráčů odebere všech patnáct kamenů z hrací desky. Tím se stává vítězem.")
        print(f"\n\nStiskněte {fg.lightgreen}Enter{fx.end} pro návrat do menu.")
        sys.stdin.readline()
    cls()
