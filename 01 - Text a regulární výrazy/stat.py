"""Input and output."""

import re, sys
from collections import Counter
from operator import itemgetter

def extract_record(record):
    """Z řetězce obsahujícího informace skladbě vytvoří slovník s konkrétními informacemi pod konkrétními klíči."""
    full_record = { } # Voice + Incipit can be multiple
    keys = [ "Print Number", "Composer", "Title", "Genre", "Key", "Composition Year", "Publication Year", "Edition", "Editor", 
            "Voice 1", "Voice 2", "Voice 3", "Voice 4", "Partiture", "Incipit", "Incipit 2", "Incipit 3" ] 
    for line in record.split('\n'):
        for key in keys:
            rString = f"{key}: (.*)"
            regex = re.compile(rString)
            found = regex.match(line)
            if (found is None): continue
            else: 
                composer = found.group(1)
                if (key == "Composer"): full_record[key] = parse_composers(composer)
                else: full_record[key] = composer
                
    return full_record

def parse_composers(comp):
    """Rozdělí řetězec se jmény skladatelů na seznam obsahující jednotlivé skladatele."""
    composers = re.sub(r" \(.*?(--?|\+).*?\)", "", comp).split(';') # odstranit závorku s lety a rozdělit podle středníků
    composers = list(map(str.strip, composers)) # odstranit nadbytečné mezery 
    unknown = [None, '', 'Anonym', 'Anonymous', 'Various', 'Unknown']
    known_composers = list(filter(lambda c: c not in unknown, composers)) # vyloučit neznámé skladatele
    return known_composers

def count_composers(all_records):
    """Ze seznamu všech záznamů vytvoří uspořádaný seznam dvojic seřazený podle počtu výskytů jednotlivých skladatelů."""
    composersCounter = Counter()
    for record in all_records:    
        composers = []
        for k, v in record.items():
            if (k == "Composer"):
                composersCounter.update(record[k])
    return composersCounter.most_common()


def yearToCentury(year):
    """Vypočítá století ze zadaného roku."""
    return 1 + (year - 1) // 100

def count_centuries(all_records):
    """Ze seznamu všech záznamů vytvoří uspořádaný seznam dvojic seřazený podle počtu výskytů skladeb v jednotlivých stoletích."""
    centuriesCounter = Counter()
    for record in all_records:
        for k, v in record.items():
            if (k == "Composition Year"):                             
                m = re.match(r"(\d+)\D*?$", v.strip())
                if not m: continue
                else:
                    year = int(m.group(1).strip())
                    if (year < 25 and 'century' in v): century = year # v záznamu bylo už přímo století
                    else: century = yearToCentury(year)
                    centuriesCounter[century] += 1               
    return centuriesCounter.most_common()

def get_ordinal_suffix_en(number):
    """Vrátí anglickou koncovku řadové číslovky."""
    if number % 10 == 1: th = 'st'
    elif number % 10 == 2: th = 'nd'
    elif number % 10 == 3: th = 'rd'
    else: th = 'th'
    return th

"""-= Main =-"""

# Kontrola argumentů

allowed_arguments = ['composer', 'century']

if (len(sys.argv) != 3):
    thisScript = sys.argv[0].split('\\')[-1];
    message = "The program expects to be called with two command-line arguments:\n" + \
    f"\t./{thisScript} ./(SCORE_LIB_FILE) (composer|century)\n" + \
    "with SCORE_LIB_FILE being the path to the score library file cointaining the records\n" + \
    "followed by either 'composer' or 'century' to output wanted information.\n"    
    sys.exit(message)
elif sys.argv[2] not in allowed_arguments:    
    message = f"The command line argument '{sys.argv[2]}' is wrong – please choose one of the following:\n{allowed_arguments}"
    sys.exit(message)

filename = sys.argv[1]
argument = sys.argv[2]
all_records = []
with open(filename, 'r', encoding='utf-8') as FILE:
    contents = FILE.read()
    for plainRecord in contents.split('\n\n'):
        all_records.append(extract_record(plainRecord))

# Composer
if (argument == 'composer'):
    composersCounter = count_composers(all_records) # seřazený seznam dvojic
    for entry in composersCounter:    
        print(f"{entry[0]}: {entry[1]}")
# Century
elif (argument == 'century'):
    centuriesCounter = count_centuries(all_records) # seřazený seznam dvojic
    for entry in centuriesCounter:
        th = get_ordinal_suffix_en(entry[0])
        print(f"{entry[0]}{th} century: {entry[1]}")