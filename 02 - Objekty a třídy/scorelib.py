import re
import sys
from typing import List, Set, Optional


class Person:
    def __init__(self, name: str, born: Optional[int] = None, died: Optional[int] = None):
        self.name = name
        self.born = born
        self.died = died

    def __str__(self):
        if self.born or self.died:
            return f"{self.name} ({xstr(self.born)}--{xstr(self.died)})"
        else:
            return f"{self.name}"


class Voice:
    def __init__(self, name: Optional[str] = None, range: Optional[str] = None):
        self.name = name
        self.range = range

    def __str__(self):
        value = ""
        if self.range:
            value += f"{self.range}"
            if self.name:
                value += ", "
        if self.name:
            value += f"{self.name}"
        return value


class Composition:
    def __init__(self, name: Optional[str], incipit: Optional[str], key: Optional[str], genre: Optional[str],
                 year: Optional[int], voices: List[Voice], authors: List[Person]):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def __str__(self):
        return f"Composition >> {{'Name': '{self.name}', 'Incipit': '{self.incipit}', 'Key': '{self.key}', " \
               f"'Genre': '{self.genre}', 'Year': '{self.year}', " \
               f"'Voices': '{[str(voice) for voice in self.voices]}', " \
               f"'Authors': '{[str(author) for author in self.authors]}'}}"


class Edition:
    def __init__(self, composition: Composition, authors: List[Person], name: Optional[str] = None):
        self.composition = composition  # instance of Composition
        self.authors = authors  # a list of Person instances
        self.name = name  # from the Edition: field, or None


class Print:
    def __init__(self, edition: Edition, print_id: int, partiture: bool):
        self.edition = edition  # instance of Edition
        self.print_id = print_id  # from Print Number
        self.partiture = partiture

    def format(self) -> str:
        # TODO: Vytvořit původní
        return str(self)

    def composition(self):
        return self.edition.composition


def extract_record(record):
    """Z řetězce obsahujícího informace skladbě vytvoří slovník s konkrétními informacemi pod konkrétními klíči."""
    keys = ["Print Number", "Composer", "Title", "Genre", "Key", "Composition Year", "Publication Year", "Edition",
            "Editor", "Partiture"]
    full_record = {key: None for key in keys}  # Voice + Incipit can be multiple
    full_record["Voice"] = full_record["Incipit"] = []
    for line in record.split('\n'):
        # Regular keys
        for key in keys:
            regex = re.compile(f"{key}: (.*)")
            found = regex.match(line)
            if found:
                capture = found.group(1)
                if key == "Composer":
                    full_record[key] = parse_composers(capture)
                else:
                    full_record[key] = capture
                continue
        # Numbered keys
        found = re.match(r"Voice \d+: (\S.*)", line)
        if found:
            full_record["Voice"].append(found.group(1))
            continue
        found = re.match(r"Incipit( \d)*: (\S.*)", line)
        if found:
            full_record["Incipit"].append(found.group(2))
    return full_record


def xstr(s):
    """Metoda, co vrací prázdný řetězec v případě, že předaná hodnota je None."""
    return '' if s is None else str(s)


def parse_composers(comp):
    """Rozdělí řetězec se jmény skladatelů na seznam obsahující jednotlivé skladatele."""
    composers = comp.split(';') # rozdělit podle středníků
    # re.sub(r" \(.*?(--?|\+).*?\)", "", comp)  # odstranit závorku s lety
    composers = list(map(str.strip, composers))  # odstranit nadbytečné mezery
    unknown = [None, '', 'Anonym', 'Anonymous', 'Various', 'Unknown']
    known_composers = list(filter(lambda c: c not in unknown, composers))  # vyloučit neznámé skladatele
    return known_composers


def parse_author_string(raw: str) -> Person:
    """Vytvoří instanci autora z řetězce obsahujícího relevantní informace."""
    name = re.sub(r"( \(.*?\))", "", raw)
    found = re.match(r".*?\((\d{4})?--(\d{4})?\).*?", raw)
    if found:
        born = found.group(1) if found.group(1) else None
        died = found.group(2) if found.group(2) else None
        return Person(name, born, died)
    else:
        return Person(name, None, None)


def parse_voice_string(raw: str) -> Voice:
    """Vytvoří hlas z řetězce obsahujícího hlasové informace."""
    found = re.match(r"(.*?)(\S+?--\S+?)(, )?(.*)", raw)
    if not found:
        return Voice(raw, None)
    else:
        range = found.group(2)
        name = found.group(1) + found.group(4)
        if name:
            return Voice(name, range)
        else:
            return Voice(None, range)


def get_unique_values(records, key: str) -> Set:
    """Ze všech záznamů vytáhne pouze unikátní hodnoty pro konkrétní klíč."""
    values = [record[key] for record in records]
    return set(values)


def try_int(s: str) -> Optional[int]:
    """Zkusí převést řetězec na číslo, přičemž vrátí 'None', pokud je ve špatném formátu."""
    try:
        number = int(s)
        return number
    except ValueError:
        return None


def try_get(record, key: str) -> Optional[str]:
    """Zkusí ze záznamu vzít hodnotu pod určitým klíčem, je-li klíč přítomen."""
    return record[key] if key in record else None


def record_to_print(record) -> Print:
    """Z jednoho záznamu vytvoří instanci Print"""
    # print(record)
    composition = Composition(name=try_get(record, "Title"),
                              incipit=try_get(record, "Incipit"),
                              key=try_get(record, "Key"),
                              genre=try_get(record, "Genre"),
                              year=try_int(record["Composition Year"]) if try_get(record, "Composition Year") else None,
                              voices=[parse_voice_string(voice) for voice in record["Voice"]],
                              authors=[parse_author_string(author) for author in record["Composer"]])
    # print(str(composition) + "\n")
    edition = Edition(composition=composition,
                      authors=[],
                      name=try_get(record, "Edition"))
    partiture = True if any(word in record["Partiture"] for word in ['yes', 'incomplete', 'piano']) else False

    return Print(edition, record["Print Number"], partiture)


def records_to_prints(records) -> List[Print]:
    """Zpracuje seznam záznamů pro vytvoření seznamu instancí třídy 'Print'"""
    return [record_to_print(r) for r in records]


def load(filename: str) -> List[Print]:
    """Funkce, která načte zadaný soubor, projde jej a vrátí seřazený seznam instancí 'Print'"""
    all_records = []
    try:
        with open(filename, 'r', encoding='utf-8') as FILE:
            contents = FILE.read()
            for plainRecord in contents.split('\n\n'):
                all_records.append(extract_record(plainRecord))
        unsorted_prints = records_to_prints(all_records)
        return sorted(unsorted_prints, key=lambda p: p.print_id)
    except FileNotFoundError:
        sys.exit(f"The file '{filename}' couldn't be found.")


prints = load("./scorelib.txt")  # TODO: Smazat po testování
