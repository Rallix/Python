import os
import sqlite3
import scorelib
import sys
from scorelib import Score, Edition, Print
from typing import List


def insert_people(p: Print):
    """ Vloží záznamy person(born, died, name) do tabulky."""
    for person in p.get_people():
        cursor.execute('SELECT * FROM person WHERE name=?', (person.name, ))  # Je už uvnitř osoba stejného jména?
        found = cursor.fetchone()  # nalezený řádek
        if not found:
            cursor.execute('INSERT INTO person(born, died, name) VALUES(?, ?, ?)',
                           (person.born, person.died, person.name))
        else:
            # Již existující autor --> případně doplnit údaje
            if not found[1] and person.born:
                cursor.execute('UPDATE person SET born=? WHERE name=?', (person.born, person.name))
            if not found[2] and person.died:
                cursor.execute('UPDATE person SET died=? WHERE name=?', (person.died, person.name))
        db_connection.commit()


def compare_voices(score: Score, db_score_id):
    """Porovná hlasy právě zpracovávaných dat s těmi v databázi."""
    cursor.execute('SELECT * FROM voice WHERE score=?', (db_score_id, ))
    results = cursor.fetchall()
    if not score.voices:
        # Pokud nejsou k dispozici žádné hlasy, stačí jen zjistit, zda v databázi naopak nějaké jsou -> pak se liší
        return not results
    for voice in score.voices:
        name_lookup = 'name IS NULL' if not voice.name else 'name=?'
        range_lookup = 'range IS NULL' if not voice.range else 'range=?'

        get_score = f"SELECT id FROM score WHERE name=? AND genre=? AND key=? AND {name_lookup} AND {range_lookup}"
        sql_params = (voice.number, db_score_id)
        if voice.name:
            sql_params += (voice.name, )
        if voice.range:
            sql_params += (voice.range, )
        cursor.execute(get_score, sql_params)
        result = cursor.fetchone()
        if not result:
            # Chybí hlas, když tam být má
            return False
    return True


def compare_authors(score: Score, db_score_id):
    """Porovná autory právě zpracovávaných dat s těmi v databázi."""
    cursor.execute('SELECT * FROM score_author WHERE score=?', (db_score_id, ))
    results = cursor.fetchall()
    if not score.authors:
        # Pokud nejsou k dispozici žádní autoři, stačí jen zjistit, zda v databázi naopak nějací jsou -> pak se liší
        return not results
    for author in score.authors:
        cursor.execute('SELECT id FROM person WHERE name=?', (author.name, ))
        result = cursor.fetchone()
        author_id = result[0]
        # Najít danou osobu v pomocné tabulce
        cursor.execute('SELECT * FROM score_author WHERE score=? AND composer=?', (db_score_id, author_id))
        result = cursor.fetchone()
        if not result:
            # Chybí osoba, co tam má být
            return False
    return True


def compare_editors(edition: Edition, db_edition_id):
    """Porovná editory právě zpracovávaných dat s těmi v databázi."""
    cursor.execute('SELECT * FROM edition_author WHERE edition=?', (db_edition_id, ))
    results = cursor.fetchall()
    if not edition.editors:
        # Pokud nejsou k dispozici žádní editoři, stačí jen zjistit, zda v databázi naopak nějací jsou -> pak se liší
        return not results
    for editor in edition.authors:
        cursor.execute('SELECT id FROM person WHERE name=?', (editor.name, ))
        result = cursor.fetchone()
        editor_id = result[0]
        # Najít danou osobu v pomocné tabulce
        cursor.execute('SELECT * FROM edition_author WHERE edition=? AND editor=?', (db_edition_id, editor_id))
        result = cursor.fetchone()
        if not result:
            # Chybí osoba, co tam má být
            return False
    return True


def insert_score(p: Print) -> int:
    """ Vloží záznamy score(name, genre, key, incipit, year) do tabulky."""
    score = p.score()
    score.incipit = "".join(score.incipit)  # TODO: Jenom hack –> upravit formát 'incipit' pořádně

    incipit_lookup = 'incipit IS NULL' if not score.incipit else 'incipit=?'
    year_lookup = 'year IS NULL' if not score.year else 'year=?'

    # Vyhledávání v databázi v závislosti na přítomných parametrech
    get_score_id = f"SELECT id FROM score WHERE name=? AND genre=? AND key=? AND {incipit_lookup} AND {year_lookup}"
    sql_params = (score.name, score.genre, score.key)
    if score.incipit:
        sql_params += (score.incipit, )
    if score.year:
        sql_params += (score.year, )
    cursor.execute(get_score_id, sql_params)

    results = cursor.fetchall()
    if results:
        for result in results:
            if compare_authors(score, result[0]) and compare_voices(score, result[0]):
                # Existující -> vrátit ID
                return result[0]

    # Chybí záznam -> přidat do tabulky
    cursor.execute(
        'INSERT INTO score(name, genre, key, incipit, year) VALUES(?, ?, ?, ?, ?)',
        (score.name, score.genre, score.key, score.incipit, score.year)
    )
    db_connection.commit()

    score_id = cursor.lastrowid
    for voice in score.voices:
        # Vložit hlasy do 'voice' + commit
        cursor.execute(
            'INSERT INTO voice(number, score, range, name) VALUES(?, ?, ?, ?)',
            (voice.number, score_id, voice.range, voice.name,)
        )
        db_connection.commit()
    for author in score.authors:
        # Vložit autory do 'score_authors' + commit
        if not author.name:
            # Bezejmenný autor
            continue
        cursor.execute('SELECT id FROM person WHERE name=?', (author.name, ))  # Najít ID autora
        result = cursor.fetchone()
        cursor.execute('INSERT INTO score_author(score, composer) VALUES(?, ?)', (score_id, result[0]))  # Junction
        db_connection.commit()
    return score_id


def insert_edition(p: Print, score_id: int) -> int:
    """ Vloží záznamy edition(score, name, year) do tabulky."""
    edition = p.edition

    name_lookup = 'name IS NULL' if not edition.name else 'name=?'
    year_lookup = 'year IS NULL' if not p.score().year else 'year=?'

    # Vyhledávání v databázi v závislosti na přítomných parametrech
    get_edition_id = f"SELECT id FROM edition WHERE score=? AND {name_lookup} AND {year_lookup}"
    sql_params = (score_id, )
    if edition.name:
        sql_params += (edition.name, )
    if p.score().year:
        sql_params += (p.score().year, )
    cursor.execute(get_edition_id, sql_params)

    results = cursor.fetchall()
    if results:
        for result in results:
            if compare_editors(edition, result[0]):
                # Existující -> vrátit ID
                return result[0]
    # Chybí záznam -> přidat do tabulky
    cursor.execute(
        'INSERT INTO edition(score, name, year) VALUES(?, ?, ?)',
        (score_id, edition.name, p.score().year)
    )
    db_connection.commit()

    edition_id = cursor.lastrowid
    for editor in edition.authors:
        # Vložit autory do 'edition_author' + commit
        cursor.execute('SELECT id FROM person WHERE name=?', (editor.name, ))
        result = cursor.fetchone()
        cursor.execute('INSERT INTO edition_author(edition, editor) VALUES(?, ?)', (edition_id, result[0],))  # Junction
        db_connection.commit()
    return edition_id


def insert_print(p: Print, edition_id: int):
    """ Vloží záznamy print(print_id, partiture, edition) do tabulky."""
    partiture = 'Y' if p.partiture else 'N'
    cursor.execute('INSERT INTO print(id, partiture, edition) VALUES(?, ?, ?)', (p.print_id, partiture, edition_id,))
    db_connection.commit()


def insert_into_db(prints: List[Print]):
    """Vloží data z textového souboru do databáze."""
    for p in prints:
        # print(f"Inserting data from Print #{p.print_id} to the database.")
        insert_people(p)
        score_id = insert_score(p)  # Pro použití v 'edition'
        edition_id = insert_edition(p, score_id)
        insert_print(p, edition_id)


if len(sys.argv) != 3:
    raise NotImplementedError(f"Import.py is supposed to be called with two additional parameters, "
                              f"was called with {len(sys.argv)} instead:\n"
                              "'./import.py scorelib.txt scorelib.dat'")

filename = sys.argv[1]
database = sys.argv[2]

# Removes the old file.
# if os.path.exists(database):
#     os.remove(database)

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
