import numpy as np
import re
from sys import argv, exit, stdout
from typing import List, Tuple


class Equation:
    def __init__(self, raw: str):
        self.raw = raw.strip()
        left_right = self.parse_equation(raw.strip())
        self.constant = left_right[1]
        self.variables = sorted(left_right[0], key=lambda t: t[1])  # seřadit proměnné podle abecedy

    def __str__(self):
        print(self.raw)

    def get_variable_names(self):
        """[(-2, 'x'), (-3, 'y'), (2, 'z')] --> ['x', 'y', 'z']"""
        return [var[1] for var in self.variables]

    def parse_equation(self, raw: str) -> Tuple[List[Tuple[int, str]], int]:
        # 2x + 3y = 5
        parts: str = raw.split(" = ")
        variables = self.split_variables(parts[0])
        constant: int = int(parts[1])
        return variables, constant

    @staticmethod
    def split_variables(left_side: str) -> List[Tuple[int, str]]:
        fragments = list(filter(
            None,
            re.split("([+-])", left_side.replace(" ", ""))))  # ['-2x', '+', '3y', '-', '2z']
        variables = []
        sign = 1
        for var in fragments:
            # Mínus -> další bude záporné
            if var == '+':
                sign = 1
                continue
            elif var == '-':
                sign = -1
                continue
            else:
                var_coef = 1 * sign  # Případ: samotná proměnná ~ 'x'
                if var[:-1]:
                    var_coef *= int(var[:-1])  # ~ '2x'
                varname = var[-1]
            variables.append((var_coef, varname))
        return variables


class EquationSystem:
    def __init__(self, equations: List[Equation]):
        self.equations = equations
        self.constants = [eq.constant for eq in equations]
        self.variables = {var: [] for var in self.unique_names()}
        for equation in equations:
            for var in equation.variables:
                self.variables[var[1]].append(var[0])  # {'x': [2, 1], 'y': [3, -1]}

    def unique_names(self):
        """Získat unikátní názvy proměnných napříč rovnicemi."""
        variable_names = []
        for eq in self.equations:
            unique_names = eq.get_variable_names()
            for name in unique_names:
                if name not in variable_names:
                    variable_names.append(name)
        return sorted(variable_names)

    def get_matix(self):
        names = self.unique_names()
        matrix = np.zeros(len(names), len(self.equations))
        print(matrix)
        # for eq in self.equations:
        #     for name in names:
        #         if eq.variables


    def solve(self) -> np.ndarray:
        variables = np.array(list(self.variables.values()))  # [[3,1], [1,2]]
        constants = np.array(self.constants)  # [9,8]
        print(variables)
        print(constants)
        return np.linalg.solve(variables, constants)

    def rank(self):
        return np.linalg.matrix_rank(self.variables)  # TODO: Check + fix

    def solution(self) -> str:
        print(self.solve())
        return str(self.constants) + " " + str(self.variables)


if len(argv) != 2:
    exit("The program expects to be called with a single command-line argument:\n"
         "./eqn.py input.txt")
filename = argv[1]

try:
    with open(filename, 'r', encoding='utf-8') as FILE:
        raw_equations = FILE.read().splitlines()
        system = EquationSystem([Equation(raw) for raw in raw_equations])
        stdout.write(system.solution() + "\n")
except FileNotFoundError:
    exit(f"The file '{filename}' couldn't be found.")
