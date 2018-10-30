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
        for i in range(len(equations)):
            for var in equations[i].variables:
                self.variables[var[1]].append(var[0])  # {'x': [2, 1], 'y': [3, -1]}
            for name in self.unique_names():
                if len(self.variables[name]) != (i+1):
                    self.variables[name].append(0)  # Přidat nulu, pokud se v rovnici něco nevyskytuje

    def unique_names(self):
        """Získat unikátní názvy proměnných napříč rovnicemi."""
        variable_names = []
        for eq in self.equations:
            unique_names = eq.get_variable_names()
            for name in unique_names:
                if name not in variable_names:
                    variable_names.append(name)
        return sorted(variable_names)

    def solve(self) -> np.ndarray:
        variables = np.column_stack(list(self.variables.values()))  # [[3,1], [1,2]]
        constants = np.array(self.constants)  # [9,8]
        return np.linalg.solve(variables, constants,)  # [ 2.,  3.]

    def has_solution(self) -> bool:
        # Ranks must be equal
        augmented_matrix = np.column_stack(list(self.variables.values()) + list((self.constants,)))
        return self.rank() == np.linalg.matrix_rank(augmented_matrix)

    def is_solution_unique(self) -> bool:
        # Number of rows is equal to the rank of the coefficient matrix
        return len(self.unique_names()) == self.rank()

    def solution_space_dimension(self) -> int:
        return len(self.unique_names()) - self.rank()

    def rank(self):
        """Vrátí hodnost matice koeficientů."""
        coefficient_matrix = np.column_stack(list(self.variables.values()))
        return np.linalg.matrix_rank(coefficient_matrix)

    def solution(self) -> str:
        if not self.has_solution():
            return "no solution"
        elif not self.is_solution_unique():
            return f"solution space dimension: {self.solution_space_dimension()}"
        # ↓ Existuje unikátní řešení
        solved = self.solve()
        names = self.unique_names()
        solution = list(zip(names, solved))
        return "solution: " + ", ".join([f"{x[0]} = {x[1]}" for x in solution])


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
