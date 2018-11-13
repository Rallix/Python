import pandas as pd
from sys import argv


def dates(csv: pd.DataFrame):
    print("Dates:\n", csv)
    pass


def deadlines(csv: pd.DataFrame):
    print("Deadlines:\n", csv)
    pass


def exercises(csv: pd.DataFrame):
    print("Excercises:\n", csv)
    pass


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./STAT.py file.csv dates|deadlines|exercises")
filename = argv[1]

mode = argv[2]
modes = ["dates", "deadlines", "exercises"]

if mode not in modes:
    exit(f"Incorrect mode: must be  one of: #{modes.join(', ')}")

try:
    CSV = pd.read_csv(filename)
    locals()[mode](CSV)
except pd.errors.EmptyDataError:
    exit(f"The CSV file '#{filename}' contains no data.")
except FileNotFoundError:
    exit(f"Could not find the CSV file: #{filename}")
