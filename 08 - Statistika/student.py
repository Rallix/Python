import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime
from sys import argv, stdout


def is_int(val):
    """Zjistí, zda je hodnota celé číslo."""
    if type(val) == int:
        return True
    elif type(val) == str:
        try:
            is_int(int(val))
            return True
        except ValueError:
            return False
    else:
        if val.is_integer():
            return True
        else:
            return False


def date(deadline):
    return deadline.strip().split('/')[0]


def date_prediction(beginning, slope, points_total):
    if np.isclose(slope, 0):
        return 'inf'
    else:
        ord_date = datetime.fromordinal(beginning + points_total / slope)
        return str(ord_date.date())


def lingress(s_data, beginning):
    dates = [date(key) for key in s_data.keys()]  # TODO: Using ordinal on dates
    dates = [(datetime.strptime(d, '%Y-%m-%d') - datetime.fromordinal(beginning)).days for d in dates]
    x = np.array(dates, dtype='float')  # dates
    y = np.array(list(s_data), dtype='float')  # points

    # Our model is y = a * x, so things are quite simple, in this case...
    # x needs to be a column vector instead of a 1D vector for this, however.
    x = x[:, np.newaxis]
    a, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return a


def get_stats(csv: pd.DataFrame) -> Dict[str, object]:
    BEGINNING = datetime.strptime("2018-09-17", "%Y-%m-%d").toordinal()  # Konstanta začátku semestru
    student = {}
    slope = 0
    if sid == 'average':
        student_data = csv.drop(['student'], axis=1).mean(axis=0)
        student = {
            'mean': student_data.mean(),
            'median': student_data.median(),
            'total': student_data.sum(),
            'passed': student_data[student_data > 0].count()
        }
        slope = lingress(student_data, BEGINNING)
        student['regression slope'] = float(slope)
        student['date 16'] = date_prediction(BEGINNING, slope, 16)
        student['date 20'] = date_prediction(BEGINNING, slope, 20)
    elif is_int(sid):
        student_data = csv[(csv['student'] == int(sid))].drop(['student'], axis=1)
        student = {
            'mean': float(student_data.mean(axis=1)),
            'median': float(student_data.median(axis=1)),
            'total': float(student_data.sum(axis=1)),
            'passed': int(student_data[student_data > 0].count(axis=1))
        }
        student_data = pd.DataFrame.transpose(student_data)
        slope = lingress(student_data, BEGINNING)
        student['regression slope'] = float(slope)
        student['date 16'] = date_prediction(BEGINNING, slope, 16)
        student['date 20'] = date_prediction(BEGINNING, slope, 20)
    else:
        raise AttributeError("Unsupported ID format – expecting an integer or 'average'.")
    return student


if len(argv) != 3:
    exit("The program expects to be called with two command-line arguments:\n"
         "./student.py file.csv <id>")
filename = argv[1]
sid = argv[2]

try:
    CSV = pd.read_csv(filename)
    stdout.write(str(get_stats(CSV)))
except pd.errors.EmptyDataError:
    exit(f"The CSV file '#{filename}' contains no data.")
except FileNotFoundError:
    exit(f"Could not find the CSV file: #{filename}")
