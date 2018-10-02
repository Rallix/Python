import sys
import re


class Person:
    def __init__(self, name: str, born: int, died: int):
        self.name = name
        self.born = born
        self.died = died


class Voice:
    def __init__(self, name: str, range: str):
        self.name = name
        self.range = range


class Composition:
    def __init__(self, name: str, incipit: str, key: str, genre: str, year: int, voices: list, authors: list):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors


class Edition:
    def __init__(self, composition: Composition, authors: list, name: str):
        self.composition = composition  # instance of Composition
        self.authors = authors  # a list of Person instances
        self.name = name  # from the Edition: field, or None


class Print:
    def __init__(self, edition: Edition, print_id: int, partiture: bool):
        self.edition = edition  # instance of Edition
        self.print_id = print_id  # from Print Number
        self.partiture = partiture

    def format(self):
        # TODO: reconstructs and prints the original stanza
        pass

    def composition(self):
        return self.edition.composition


def extract_record(record):
    """Z řetězce obsahujícího informace skladbě vytvoří slovník s konkrétními informacemi pod konkrétními klíči."""
    full_record = {}  # Voice + Incipit can be multiple
    keys = ["Print Number", "Composer", "Title", "Genre", "Key", "Composition Year", "Publication Year", "Edition",
            "Editor", "Voice 1", "Voice 2", "Voice 3", "Voice 4", "Partiture", "Incipit", "Incipit 2", "Incipit 3"]
    for line in record.split('\n'):
        for key in keys:
            r_string = f"{key}: (.*)"
            regex = re.compile(r_string)
            found = regex.match(line)
            if found is None:
                continue
            else:
                composer = found.group(1)
                if key == "Composer":
                    full_record[key] = parse_composers(composer)
                else:
                    full_record[key] = composer

    return full_record


def parse_composers(comp):
    """Rozdělí řetězec se jmény skladatelů na seznam obsahující jednotlivé skladatele."""
    composers = re.sub(r" \(.*?(--?|\+).*?\)", "", comp).split(
        ';')  # odstranit závorku s lety a rozdělit podle středníků
    composers = list(map(str.strip, composers))  # odstranit nadbytečné mezery
    unknown = [None, '', 'Anonym', 'Anonymous', 'Various', 'Unknown']
    known_composers = list(filter(lambda c: c not in unknown, composers))  # vyloučit neznámé skladatele
    return known_composers


def records_to_prints(records):
    """Zpracuje seznam záznamů pro vytvoření seznamu instancí 'Print'"""
    # TODO: the function returns a list of Print instances
    return []


def load(filename: str):
    all_records = []
    try:
        with open(filename, 'r', encoding='utf-8') as FILE:
            contents = FILE.read()
            for plainRecord in contents.split('\n\n'):
                all_records.append(extract_record(plainRecord))
        return records_to_prints(all_records)
    except FileNotFoundError:
        sys.exit(f"The file '{filename}' couldn't be found.")


records = load("./scorelib.txt")
print(records)
