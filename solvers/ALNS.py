import random
import time
import numpy as np

from solvers import Destroy
from solvers import Repair
from solvers import initial_solution

class ALNS:

    def __init__ (self, problem, starting_point):

        self.problem = problem
        self.starting_point = starting_point

        self.solution = problem.solution
        self.nurses = problem.nurses
        self.surgeons = problem.surgeons
        self.patients = problem.patients
        self.occupants = problem.occupants
        self.rooms = problem.rooms
        self.theaters = problem.theaters
        self.Tempo = problem.T
        self.shifts = problem.shifts


    def solve(self, number_of_iterations = 1000):   # main function for the solver

        current_point = self.starting_point    # this is the starting point
        problem = self.problem
        p_iteration = np.linspace(0, 100, number_of_iterations)

        for t in range(number_of_iterations):   # iterating
            progress(p_iteration[t])


def progress(percent=0, width=30):   # function made only for printing the progress bar
    left = int(width * percent // 100)
    right = width - left
    print('\r[', '#' * left, '' * right, ']',
          f' {percent: .0f}%', sep='', end='', flush=True)


