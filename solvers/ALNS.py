import random
import time

from time import sleep
import time
import numpy as np
from colorama import Fore,Style

import copy

from solvers.Destroy import destroy
from solvers.Repair import repair
from solvers import initial_solution

from instances.solution import Solution
from instances.hospital import Times
from instances.problem import Problem

class ALNS:

    def __init__ (self, problem, starting_point):

        self.starting_problem = problem
        self.starting_point = starting_point

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
        starting_problem = self.starting_problem
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

        # ************************ init the destroy e repair
        times = Times(T,shifts)
        point_destroyed = Solution(times, rooms, patients, surgeons, nurses)
        new_point = Solution(times, rooms, patients, surgeons, nurses )
        #******************************

        # **************** things for the plot
        x_data, y_data = [], []

        x_data.append(0)
        current_value, dic = starting_problem.objective_function(current_point, occupants, surgeons, nurses,  rooms, T, shifts, weights)
        y_data.append(current_value)
        # ********************

        for t in range(number_of_iterations):   # iterating

            show_progress(p_iteration[t])
            time.sleep(0.001)


            # ********** for the plot **********
            x_data.append(t+1)
            # **********************************

            point_destroyed,new_rooms = destroy('A',current_point,starting_problem)

            new_problem = Problem(occupants, patients, surgeons, nurses, new_rooms, theaters, T, shifts, weights)

            new_point = repair('A', current_point, point_destroyed, new_problem)    # in this case point_destroyed and new_point HAVE THE SAME POINTER

            if not new_problem.constraints( new_point, patients, surgeons, new_rooms, theaters, T, shifts):
                print("")
                print(Fore.YELLOW + f"Destroy and repair have failed" + Style.RESET_ALL)
                print("")
                result = new_problem.constraints( new_point, patients, surgeons, rooms, theaters, T, shifts,True)
                print("")
                return 0

            new_value, dic = new_problem.objective_function(new_point, occupants, surgeons, nurses,  new_rooms, T, shifts, weights) 
            #print("new_value", new_value, "current_value", current_value)
            if new_value <= current_value:
                current_point = copy.deepcopy(new_point)
                starting_problem = copy.deepcopy(new_problem)
                current_value = new_value
                # ************ for the plot *********
                y_data.append(new_value)
                # ************************************
            else:
                y_data.append(current_value)

            #if t == 1:
                #break

            

        return (current_point,x_data,y_data)


def show_progress(percent=0, width=30):   # function made only for printing the progress bar
    left = int(width * percent // 100)
    right = width - left
    
    print('\r[', '#' * left, '' * right, ']',
          f' {percent: .0f}%', sep='', end='', flush=True)


