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
               f"'Authors': '{[str(author) for author in self.authors] if self.authors else ''}'}}"


class Edition:
    def __init__(self, composition: Composition, authors: List[Person], name: Optional[str] = None):
        self.composition = composition  # instance of Composition
        self.authors = authors  # a list of Person instances
        self.name = name.strip()  # from the Edition: field, or None

    def __str__(self):
        return f"Edition >> {{'Composition': '{self.composition is not None}', " \
                            f"'Authors': {len(self.authors)}, " \
                            f"'Name': '{self.name}'}}"


class Print:
    def __init__(self, edition: Edition, print_id: int, partiture: bool):
        self.edition = edition  # instance of Edition
        self.print_id = print_id  # from Print Number
        self.partiture = partiture

    def format(self):
        return f"{str(self)}"

    def composition(self):
        return self.edition.composition

    def __str__(self) -> str:
        # TODO: Vytvořit původní
        """
        Print Number: 1
        Composer: Weber, Carl Maria
        Title: Concerto for bassoon and orchestra op. 75
        Genre: solo concerto
        Key: Bes
        Composition Year:
        Publication Year:
        Edition: modern
        Editor:
        Voice 1: Bes1--d2, bassoon, part
        Partiture: no
        Incipit: treble 4/4 f'2 c8. a16 f8. a16 |
        """
        print_number = f"Print Number: {self.print_id}\n"
        composer = f"Composer: {'; '.join([str(author) for author in self.composition().authors]) if self.composition().authors else ''}\n"
        title = f"Title: {self.edition.composition.name}\n"
        genre = f"Genre: {xstr(self.edition.composition.genre)}\n"
        key = f"Key: {xstr(self.edition.composition.key)}\n"
        comp_year = f"Composition Year: {self.edition.composition.year if self.edition.composition.year else ''}\n"
        pub_year = f"Publication Year: \n"  # není třeba uvádět
        edition = f"Edition: {xstr(self.edition.name) if self.edition else ''}\n"
        editor = f"Editor: {'; '.join([author.name for author in self.edition.authors]) if self.edition.authors else ''}\n"
        partiture = f"Partiture: {'yes' if self.partiture else 'no'}\n"
        voice = '\n'.join([f"Voice {i+1}: {str(self.edition.composition.voices[i]).strip()}"
                           for i in range(len(self.edition.composition.voices))])\
                + "\n" if len(self.edition.composition.voices) > 0 else ''
        incipit = f"Incipit: {xstr(self.edition.composition.incipit)}\n"

        return f"{print_number}{composer}{title}{genre}{key}{comp_year}" \
               f"{pub_year}{edition}{editor}{partiture}{voice}{incipit}"


def extract_record(record):
    """Z řetězce obsahujícího informace skladbě vytvoří slovník s konkrétními informacemi pod konkrétními klíči."""
    keys = ["Print Number", "Composer", "Title", "Genre", "Key", "Composition Year", "Publication Year", "Edition",
            "Editor", "Partiture", "Incipit"]
    full_record = {key: None for key in keys}  # Voice + Incipit can be multiple
    full_record["Composer"] = []
    full_record["Editor"] = []
    full_record["Voice"] = []
    for line in record.split('\n'):
        # Regular keys
        for key in keys:
            regex = re.compile(f"{key}: (.*)")
            found = regex.match(line)
            if found:
                capture = found.group(1).strip()
                if key == "Composer" or key == "Editor":
                    full_record[key] = parse_composers(capture)
                else:
                    full_record[key] = capture
                continue
        # Numbered keys
        found = re.match(r"Voice \d+: (\S.*)", line)
        if found:
            full_record["Voice"].append(found.group(1).strip())
            continue
        found = re.match(r"Incipit( \d)*: (\S.*)", line)
        if found:
            full_record["Incipit"] = found.group(2).strip()
    return full_record


def xstr(s):
    """Metoda, co vrací prázdný řetězec v případě, že předaná hodnota je None."""
    return '' if s is None else str(s)


def parse_composers(comp):
    """Rozdělí řetězec se jmény skladatelů na seznam obsahující jednotlivé skladatele."""
    composers = comp.split(';')  # rozdělit podle středníků
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
    found = re.match(r"(.*?)(\S+?--\S+(, | )?)(.*)", raw)
    if not found:
        return Voice(raw, None)
    else:
        range = found.group(2).strip().rstrip(',')
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
    print_id = int(record["Print Number"].strip())
    composition = Composition(name=try_get(record, "Title"),
                              incipit=try_get(record, "Incipit"),
                              key=try_get(record, "Key"),
                              genre=try_get(record, "Genre"),
                              year=try_int(record["Composition Year"]) if try_get(record, "Composition Year") else None,
                              voices=[parse_voice_string(voice) for voice in record["Voice"]] if record["Voice"] else [],
                              authors=[parse_author_string(author) for author in record["Composer"]] if record["Composer"] else [])
    edition = Edition(composition=composition,
                      authors=[parse_author_string(author) for author in record["Editor"]] if record["Editor"] else [],
                      name=try_get(record, "Edition"))
    partiture = True if any(word in record["Partiture"] for word in ['yes', 'incomplete', 'piano']) else False

    return Print(edition, print_id, partiture)


def records_to_prints(records) -> List[Print]:
    """Zpracuje seznam záznamů pro vytvoření seznamu instancí třídy 'Print'"""
    return [record_to_print(r) for r in records]


def load(filename: str) -> List[Print]:
    """Funkce, která načte zadaný soubor, projde jej a vrátí seřazený seznam instancí 'Print'"""
    all_records = []
    try:
        with open(filename, 'r', encoding='utf-8') as FILE:
            contents = FILE.read()
            plain_records = filter(None, contents.split('\n\n'))
            for plain_record in plain_records:
                record_dict = extract_record(plain_record)
                all_records.append(record_dict)
        unsorted_prints = records_to_prints(all_records)
        return sorted(unsorted_prints, key=lambda p: int(p.print_id))
    except FileNotFoundError:
        sys.exit(f"The file '{filename}' couldn't be found.")
