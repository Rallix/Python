import numpy
from sys import argv, exit, stdout
from typing import List, Tuple


class Equation:
    def __init__(self, raw: str, variables: List[Tuple[int, str]], constant: int):
        self.raw = raw
        self.constant = constant
        self.variables = sorted(variables, key= lambda t: t[1]) # sort by variable name


def parse_equation(raw: str) -> Equation:
    # 2x + 3y = 5
    parts: str = raw.split(" = ")
    constant: int = parts[1]
    # TODO : Finish parsing
    return Equation(raw)


def solve_equation(equation: Equation) -> str:
    # TODO: Solve with 'numpy'
    pass


if len(argv) != 2:
    exit("The program expects to be called with a single command-line argument:\n"
         "./eqn.py input.txt")
filename = argv[1]

try:
    with open(filename, 'r', encoding='utf-8') as FILE:
        equations = FILE.read().splitlines()
        solution = solve_equation(equations)
        stdout.writeln(solution + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")


