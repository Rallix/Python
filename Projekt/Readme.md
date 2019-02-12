## Ludus duodecim scriptorum 
#### XII Scripta
---

* [Wikipedie](https://en.wikipedia.org/wiki/Ludus_duodecim_scriptorum)
* [Pravidla](http://www.cyningstan.com/game/61/ludus-duodecim-scriptorum)

XII Scripta je starořímská stolní hra, pravděpodobně předchůdce vrhcábů, kterou bych se chtěl pokusit naprogramovat.
Pravidla se nedochovala, nicméně se je pokusil rekonstruovat historik H. J. R. Murray.
Zde je úplný seznam, lepší je pochopitelný s obrázky dostupnými v odkazech výše:
Pravidla jsou přístupná (v češtině) i z herního menu; lze spustit i zkrácenou hru s méně kameny.

1. Ludus duodecim scriptorum is played by two on a board consisting of three rows of twelve points, each row of twelve being divided in half.
2. Each player has fifteen pieces of his own colour, either black or white. At the start of the game these pieces are off the board.
3. Three six-sided dice control the movement of the pieces.
4. Players decide who goes first, either at random or by agreement.
5. A player begins his turn by throwing the three dice. The player can take the numbers rolled in any order he pleases, and with each number rolled, do one the following:
    1. a piece waiting to enter the board may be placed on the appropriate point 1-6 shown in the diagram
    1. a piece on the board may be moved along the course by the appropriate number of points; the diagram shows the direction that pieces move;
    1. if all of the player's pieces are on the points I-VI at the end of the course, then a piece may be borne off the board from the appropriate point I-VI as shown on the die; that piece has completed its race;
    1. if a piece has been captured as described later in rule 8, it must be re-entered on point 1-6 as in rule 5(i), before any other piece is played.
6. Pieces of the same colour may be stacked upon a point, to an unlimited height.
7. A piece may not land on a point if two or more of the opponent's pieces already occupy that point.
8. A piece sat alone on a point is captured if an opponent's piece lands on that same point. The captured piece is removed from the board, and its owner must on his turn re-enter it before he moves any other piece (see rule 5(iv)).
9. The game is finished when one of the players has borne all fifteen of his pieces off the board. He is then declared the winner.

### Skripty

**Main**: `xii_scripta.py` (hlavní menu hry)  
**Hra**: `board.py`, `player.py` (hrací deska a hráči)  
**Kostky**: `shuffle_bag.py`, `dice.py`  

### Detaily

Hra se hraje jako *hotseat*, přičemž hráči (jakoby) sedí proti sobě:

**Hráč I (žlutá)**: arabské číslice  
**Hráč II (zelená)**: písmena  

Kameny hráčů jsou odlišeny barevně, pro případ nespolupracující konzole jsem pro jistotu (a přehlednost) nechal čísla + abecedu
Víc jak patnáct kamenů (nejhorší případ) na jednom poli nikdy nebude, přesto pochybuji, že se jich někdy sejde víc než deset, aby to rozhodilo formát (I:čísla + II:písmena).

Pro zrychlení hry je přidán i mód, co má pouze 3 kameny místo patnácti (i tak je jedna hra aspoň na pět minut)

Házení kostkou je dělané metodou [shuffle bag](https://gamedevelopment.tutsplus.com/tutorials/shuffle-bags-making-random-feel-more-random--gamedev-1249):

* protože pseudonáhodné hodnoty nejsou pro hry dostatečně 'spravedlivé'; shuffle bag hody kostkou rozloží víceméně rovnoměrně
* jednoduše řečeno, pokud hráč hodí celkem 10× jedničku, musí 10× hodit i ostatní číslice, než mu bude moci zase padnout jednička

V projektu je použit modul [console](https://pypi.org/project/console/) (0.94) pro barevné a formátované výpisy.

Alternativně lze každému hráči ještě zobrazovat herní plochu zrcadlově obrácenou, jelikož sedí proti sobě.

Parametry příkazů se musí shodovat s některým hodem kostky

* `place <pole>`
    * vloží kámen do hry na pozici 1-6
* `move <kolikátý kámen> <o kolik>`
    * pohne kamenem s určitým pořadím (počítají se i ty na sobě) od startu o počet polí
* `take <pole>`
    * sebere kámen, je-li nějaký na odpovídajícím koncovém poli 1-6
* `pass`
    * přeskočí tah hráče (např. když je blokován a nemůže použít žádnou kostku)
* `yield`
    * hráč se vzdá ve prospěch protivníka
