import random
import time

from time import sleep
import time
import numpy as np

from solvers.Destroy import destroy
from solvers.Repair import repair
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
        self.weights = problem.weights


    def solve(self, number_of_iterations = 1000):   # main function for the solver

        print(" ")
        print("Solving with ALNS ...")

        current_point = self.starting_point    # this is the starting point
        problem = self.problem
        nurses = self.nurses
        surgeons = self.surgeons
        patients = self.patients
        occupants = self.occupants
        rooms = self.rooms
        theaters = self.theaters
        T = self.Tempo
        shifts = self.shifts
        weights = self.weights

        p_iteration = np.linspace(0, 100, number_of_iterations)

        # **************** things for the plot
        x_data, y_data = [], []

        x_data.append(0)
        current_value, dic = problem.objective_function(current_point, occupants, surgeons, nurses,  rooms, T, shifts, weights)
        y_data.append(current_value)

        # ********************
        

        for t in range(number_of_iterations):   # iterating

            show_progress(p_iteration[t])
            time.sleep(0.001)


            # ********** for the plot **********
            x_data.append(t+1)
            # **********************************

            point_destroyed = destroy('A',current_point,problem)
            new_point = repair('A', point_destroyed, problem)

            print(problem.constraints(new_point, patients, surgeons, rooms, theaters, T, shifts))      

            break

            new_value, dic = problem.objective_function(new_point, occupants, surgeons, nurses,  rooms, T, shifts, weights) 

            if new_value <= current_value:
                current_point = new_point
                current_value = new_value
                # ************ for the plot *********
                y_data.append(new_value)
                # ************************************

        return (new_point,x_data,y_data)


def show_progress(percent=0, width=30):   # function made only for printing the progress bar
    left = int(width * percent // 100)
    right = width - left
    
    print('\r[', '#' * left, '' * right, ']',
          f' {percent: .0f}%', sep='', end='', flush=True)


