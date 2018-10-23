import sqlite3
import json
from sys import argv, stdout
from typing import List, Dict


class Composers:
    """Pomocná třída pro provedení všech nuntných úkonů zřetězeně za sebou."""

    def __init__(self, p_id: int = 0, composers: List = None):
        self.print_id = p_id
        self.composers = composers

    def find_print(self, p_id: int):
        """Uloží si Print ID pro pozdější hledání."""
        self.print_id = p_id
        return self

    def get_composers(self):
        """Spojí potřebné tabulky a vyloví z nich skladatele daného 'print'."""
        join_table = "person " \
                     "JOIN score_author ON person.id = score_author.composer " \
                     "JOIN edition ON score_author.score = edition.score " \
                     "JOIN print ON edition.id = print.edition"
        cursor.execute(
            f'SELECT person.name, person.born, person.died FROM {join_table} WHERE print.id=?',
            (self.print_id,)
        )
        self.composers = cursor.fetchall()
        return self

    def to_JSON(self) -> List[Dict]:
        json_data = []
        for composer in self.composers:
            data = {"name": composer[0]}
            if composer[1]:
                data["born"] = composer[1]
            if composer[2]:
                data["died"] = composer[2]
            json_data.append(data)
        return json_data


if len(argv) != 2:
    raise NotImplementedError(f"Getprint.py is supposed to be called with a single numeric parameter:\n"
                              "'./getprint.py PRINT_ID'")

database: str = 'scorelib.dat'
db_connection = sqlite3.connect(database)
cursor = db_connection.cursor()

print_id = int(argv[1])

results = Composers().find_print(print_id).get_composers()
json.dump(results.to_JSON(), stdout, indent=4, ensure_ascii=False)

db_connection.close()
