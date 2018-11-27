import json
import pandas as pd
import numpy as np
from typing import Dict
from sys import argv, stdout


def quartiles(csv: pd.DataFrame):
    """Vrátí všechny tři kvartily."""
    return [csv.quantile(q) for q in list(np.linspace(0.25, 1, 3, endpoint=False))]


def get_stats(csv: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Získá všechny hledané statistické hodnoty."""
    output = {}
    for key in csv.keys():
        data = {
            'mean': csv.mean()[key],
            'median': csv.median()[key],
            'first': quartiles(csv)[0][key],
            'last': quartiles(csv)[1][key],  # TODO: Liší se
            'passed': len(csv[(csv[key] > 0)])
        }
        output[key] = data
    return output


def merge_dates(csv: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Spojí jednotlivé úseky do jednoho."""
    merged = pd.DataFrame()
    cache = {}
    for key in csv.keys():
        date, exercises = key.strip().split('/')
        column = date if MODE == 'dates' else exercises
        slice = csv.loc[:, key]
        if column not in cache:
            cache[column] = slice
        else:
            # m = cache[column] + slice
            cache[column] += slice
    for key, val in cache.items():
        merged[key] = val
    return get_stats(merged)


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./stat.py file.csv dates|deadlines|exercises")
FILENAME = argv[1]

MODE = argv[2]
modes = ["dates", "deadlines", "exercises"]

if MODE not in modes:
    exit(f"Incorrect mode: must be one of: #{', '.join(modes)}")

try:
    CSV = pd.read_csv(FILENAME).drop(['student'], axis=1)  # Nepotřebujeme ID studentů
    stats = get_stats(CSV) if MODE == 'deadlines' else merge_dates(CSV)
    json.dump(stats, sort_keys=False, indent=2, fp=stdout)

except pd.errors.EmptyDataError:
    exit(f"The CSV file '#{FILENAME}' contains no data.")
except FileNotFoundError:
    exit(f"Could not find the CSV file: #{FILENAME}")
