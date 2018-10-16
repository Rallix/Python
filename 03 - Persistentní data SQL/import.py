import os
import sqlite3
import scorelib
import sys
from scorelib import Person, Score, Voice, Edition, Print
from typing import List, Optional


def insert_people(p: Print):
    """ person(born, died, name) """
    people = p.get_people()  # Autoři ze 'score' a editoři z 'edition'
    for person in people:
        cursor.execute('SELECT * FROM person WHERE name=?', (person.name,))  # Je už uvnitř osoba stejného jména?
        found = cursor.fetchone()  # nalezený řádek
        if not found:
            cursor.execute('INSERT INTO person(born, died, name) VALUES (?, ?, ?)',
                           (person.born, person.died, person.name))
        else:
            # Již existující autor --> případně doplnit údaje
            if not found[1] and person.born:
                cursor.execute('UPDATE person SET born=? WHERE name=?', (person.born, person.name))
            if not found[2] and person.died:
                cursor.execute('UPDATE person SET died=? WHERE name=?', (person.died, person.name))
        db_connection.commit()


def compare_voices(s_id, score: Score):
    return False


def compare_authors(s_id, score: Score):
    return False


def find_matching_id(score: Score) -> Optional[int]:
    """Najde záznam v databázi s odpovídajícími hodnotami. Pokud se někde shodují, vrátí id – jinak nic."""
    cursor.execute('SELECT * FROM score WHERE name=? AND genre=? AND key=? AND incipit=? AND year=?',
                   (score.name, score.genre, score.key, "".join(score.incipit), score.year))
    results = cursor.fetchall()  # Najít všechny záznamy se shodnými základními atributy
    if results:
        for s in results:
            s_id = s[0]
            # TODO: Stejní autoři a hlasy → vrátit ID
            if compare_voices(s_id, score) and compare_authors(s_id, score):
                return s_id
    return None


def insert_score(p: Print) -> Optional[int]:
    """ score(name, genre, key, incipit, year) """
    score = p.score()
    score_id = find_matching_id(score)
    if not score_id:
        # Chybí záznam -> přidat do tabulky
        cursor.execute('INSERT INTO score(name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)',
                       (score.name, score.genre, score.key, "".join(score.incipit), score.year))  # TODO: Smazat *join*
        score_id = cursor.lastrowid
        db_connection.commit()
        # TODO: Vložit hlasy do 'voice' + commit
        # TODO: Vložit autory do 'score_authors' + commit
    return score_id


def insert_edition(p: Print):
    """ edition(score, name, year) """
    pass


def insert_print(p: Print):
    """ print(print_id, partiture, edition) """
    pass


def insert_into_db(prints: List[Print]):
    """Vloží data z textového souboru do databáze."""
    for p in prints:
        # print(f"Inserting data from Print #{p.print_id} to the database.")
        insert_people(p)
        score_id = insert_score(p)  # Pro použití v 'edition'
        insert_edition(p)  # TODO: Vrátit 'edition_id'
        insert_print(p)


if len(sys.argv) != 3:
    raise NotImplementedError(f"Import.py is supposed to be called with two additional parameters, "
                              f"was called with {len(sys.argv)} instead:\n"
                              "'./import.py scorelib.txt scorelib.dat'")

filename = sys.argv[1]
database = sys.argv[2]

# Removes the old file. DELETE AFTER TESTING!
if os.path.exists(database):
    os.remove(database)

all_prints = scorelib.load(filename)

try:
    with open("scorelib.sql", 'r', encoding='utf-8') as FILE:
        sql_script = FILE.read()

        # Vytvořit tabulky
        db_connection = sqlite3.connect(database)  # scorelib.dat
        cursor = db_connection.cursor()
        cursor.executescript(sql_script)

        # Vložit data do tabulek
        insert_into_db(all_prints)
        db_connection.commit()
        db_connection.close()
except FileNotFoundError:
    sys.exit(f"The file '{filename}' couldn't be found.")
