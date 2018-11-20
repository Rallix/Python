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
    csv = csv.drop(['student'], axis=1)  # Nepotřebujeme hodnoty studenta
    output = {}
    for key in csv.keys():
        data = {
            'mean': csv.mean()[key],
            'median': csv.median()[key],
            'first': quartiles(csv)[0][key],
            'last': quartiles(csv)[1][key],
            'passed': len(csv[(csv[key] > 0)])
        }
        output[globals()[mode](key)] = data
    return output


def dates(key: str) -> str:
    """Změní formát z deadlines na dates (YYYY-MM-DD)."""
    return key.strip().split('/')[0]


def exercises(key: str) -> str:
    """Změní formát z deadlines na exercises (NN)."""
    return key.strip().split('/')[1]


def deadlines(key: str) -> str:
    """Změní formát z deadlines na deadlines (YYYY-MM-DD/NN)."""
    return key


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./stat.py file.csv dates|deadlines|exercises")
filename = argv[1]

mode = argv[2]
modes = ["dates", "deadlines", "exercises"]

if mode not in modes:
    exit(f"Incorrect mode: must be one of: #{', '.join(modes)}")

try:
    CSV = pd.read_csv(filename)
    json_data = json.dumps(get_stats(CSV), sort_keys=False, indent=2)
    stdout.write(json_data)
except pd.errors.EmptyDataError:
    exit(f"The CSV file '#{filename}' contains no data.")
except FileNotFoundError:
    exit(f"Could not find the CSV file: #{filename}")
