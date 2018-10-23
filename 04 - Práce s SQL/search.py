import sqlite3
import json
from sys import argv, stdout
from typing import List, Dict


def find_prints(name: str) -> List:
    """S pomocí jména autora najde všechny jeho 'printy'."""
    like = f'%{name}%'
    join_table = "person " \
                 "JOIN score_author ON person.id = score_author.composer " \
                 "JOIN edition ON score_author.score = edition.score " \
                 "JOIN print ON edition.id = print.edition"
    cursor.execute(
        f'SELECT print.id, print.partiture, person.name '
        f'FROM {join_table} '
        f'WHERE person.name LIKE ?',
        (like,)
    )
    return cursor.fetchall()


def fetch_composers(print_id) -> List:
    """Najde v tabulce pro určitý 'print' jeho skladatele."""
    join_table = "person " \
                 "JOIN score_author ON person.id = score_author.composer " \
                 "JOIN edition ON score_author.score = edition.score " \
                 "JOIN print ON edition.id = print.edition"
    cursor.execute(
        f'SELECT person.name, person.born, person.died '
        f'FROM {join_table} '
        f'WHERE print.id=?',
        (print_id,)
    )
    return cursor.fetchall()


def fetch_editors(print_id) -> List:
    """Najde v tabulce pro určitý 'print' jeho skladatele."""
    join_table = "print " \
                 "JOIN edition_author ON print.edition = edition_author.edition " \
                 "JOIN person ON edition_author.editor = person.id"
    cursor.execute(
        f'SELECT person.name, person.born, person.died '
        f'FROM {join_table} '
        f'WHERE print.id=?',
        (print_id,)
    )
    return cursor.fetchall()


def fetch_voices(score_id) -> List:
    """Najde v tabulce pro určitý 'print' jeho skladatele."""
    join_table = "voice " \
                 "JOIN score ON score.id = voice.score"
    cursor.execute(
        f'SELECT voice.number, voice.range, voice.name '
        f'FROM {join_table} '
        f'WHERE score.id=?',
        (score_id,)
    )
    return cursor.fetchall()


def fetch_edition(print_id):
    """Najde v tabulce pro určitý 'print' jeho edici."""
    join_table = "print " \
                 "JOIN edition ON print.edition = edition.id"
    cursor.execute(
        f'SELECT edition.name, edition.year '
        f'FROM {join_table} '
        f'WHERE print.id=?',
        (print_id,)
    )
    return cursor.fetchone()


def fetch_score(print_id):
    """Najde v tabulce pro určitý 'print' jeho kompozici."""
    join_table = "print " \
                 "JOIN edition ON print.edition = edition.id " \
                 "JOIN score ON  edition.score = score.id"
    cursor.execute(
        f'SELECT score.id, score.name, score.genre, score.key, score.incipit, score.year '
        f'FROM {join_table} '
        f'WHERE print.id=?',
        (print_id,)
    )
    return cursor.fetchone()


def print_to_JSON(print_row) -> Dict:
    """Převede jednotlivé 'printy' do JSON formátu."""
    json_print = {}

    # Najít všechna potřebná data
    composers = fetch_composers(print_row[0])
    editors = fetch_editors(print_row[0])
    edition = fetch_edition(print_row[0])
    score = fetch_score(print_row[0])

    voices = fetch_voices(score[0])

    # Využít je
    json_print["Print Number"] = print_row[0]
    json_print["Composer"] = [{"Name": composer[0],
                               "Born": composer[1],
                               "Died": composer[2]} for composer in composers]
    json_print["Title"] = score[1]
    json_print["Genre"] = score[2]
    json_print["Key"] = score[3]
    json_print["Composition Year"] = score[5]
    json_print["Publication Year"] = edition[1]
    json_print["Edition"] = edition[0]
    json_print["Editor"] = [{"Name": editor[0],
                             "Born": editor[1],
                             "Died": editor[2]} for editor in editors]
    json_print["Voices"] = {voice[0]: {"Range": voice[1],
                                       "Name": voice[2]} for voice in voices}
    json_print["Partiture"] = True if print_row[1] == 'Y' else False
    json_print["Incipit"] = score[4]

    return json_print


def convert_prints(filtered_prints) -> Dict:
    names = [p[2] for p in filtered_prints]
    output = {name: [] for name in names}  # Slovník jmen a prázdných seznamů na printy

    for p in filtered_prints:
        name = p[2]
        output[name].append(print_to_JSON(p))
    return output  # Výstupní zaplněný slovník do JSON Dump


if len(argv) != 2:
    raise NotImplementedError(f"Search.py is supposed to be called with a single-word string parameter:\n"
                              "'./getprint.py NAME'")

database: str = 'scorelib.dat'
db_connection = sqlite3.connect(database)
cursor = db_connection.cursor()

composer_name = argv[1]
composer_prints = find_prints(composer_name)
json.dump(convert_prints(composer_prints), stdout, indent=4, ensure_ascii=False)

db_connection.close()
