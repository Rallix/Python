"""Input and output."""

import re
import sys
from collections import Counter


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


def count_composers(records):
    """Ze seznamu všech záznamů vytvoří uspořádaný seznam dvojic seřazený podle počtu výskytů jednotlivých skladatelů."""
    composers_counter = Counter()
    for record in records:
        for k, v in record.items():
            if k == "Composer":
                composers_counter.update(record[k])
    return composers_counter.most_common()


def year_to_century(year):
    """Vypočítá století ze zadaného roku."""
    return 1 + (year - 1) // 100


def count_centuries(records):
    """Ze seznamu všech záznamů vytvoří uspořádaný seznam dvojic seřazený podle počtu výskytů skladeb v jednotlivých stoletích."""
    centuries_counter = Counter()
    for record in records:
        for k, v in record.items():
            if k == "Composition Year":
                m = re.match(r"(\d+)\D*?$", v.strip())
                if not m:
                    continue
                else:
                    year = int(m.group(1).strip())
                    if year < 25 and 'century' in v:
                        century = year  # v záznamu bylo už přímo století
                    else:
                        century = year_to_century(year)
                    centuries_counter[century] += 1
    return centuries_counter.most_common()


def get_ordinal_suffix_en(number):
    """Vrátí anglickou koncovku řadové číslovky."""
    if number % 10 == 1:
        suffix = 'st'
    elif number % 10 == 2:
        suffix = 'nd'
    elif number % 10 == 3:
        suffix = 'rd'
    else:
        suffix = 'th'
    return suffix


"""-= Main =-"""

# Kontrola argumentů

allowed_arguments = ['composer', 'century']

cli_arguments = sys.argv
print(f"Command line arguments ({len(sys.argv)}): {sys.argv}\n")

if len(cli_arguments) != 3:
    thisScript = sys.argv[0].split('\\')[-1]
    message = "The program expects to be called with two command-line arguments:\n" + \
              f"\t./{thisScript} ./(SCORE_LIB_FILE) (composer|century)\n" + \
              "with SCORE_LIB_FILE being the path to the score library file cointaining the records\n" + \
              "followed by either 'composer' or 'century' to output wanted information.\n"
    sys.exit(message)
elif cli_arguments[2] not in allowed_arguments:
    message = f"The command line argument '{cli_arguments[2]}' is wrong – please choose one of the following:\n" \
              f"{allowed_arguments}"
    sys.exit(message)

filename = cli_arguments[1]
stat_mode = cli_arguments[2]

# Načíst záznamy ze souboru
all_records = []
with open(filename, 'r', encoding='utf-8') as FILE:
    contents = FILE.read()
    for plainRecord in contents.split('\n\n'):
        all_records.append(extract_record(plainRecord))

# Composer
if stat_mode == 'composer':
    composersCounter = count_composers(all_records)  # seřazený seznam dvojic
    for entry in composersCounter:
        print(f"{entry[0]}: {entry[1]}")
# Century
elif stat_mode == 'century':
    centuriesCounter = count_centuries(all_records)  # seřazený seznam dvojic
    for entry in centuriesCounter:
        th = get_ordinal_suffix_en(entry[0])
        print(f"{entry[0]}{th} century: {entry[1]}")
