import numpy as np
import json 
import random
import copy


from colorama import Fore,Style

import matplotlib
matplotlib.use("Agg")  # Usa un backend non interattivo
import matplotlib.pyplot as plt
import os

#import sys
#sys.stdout = open('log_output.txt', 'w')

from instances.hospital import Times
from instances.hospital import Rooms
from instances.hospital import Theaters
from instances.patient import Patient
from instances.occupant import Occupant
from instances.surgeon import Surgeon
from instances.nurse import Nurse
from instances.problem import Problem
from instances.solution import Solution

from utils import *

from solvers.initial_solution import initial_solution
from solvers.ALNS import ALNS
from solvers.solution_output import *





random_seed = min(341965, 343316, 284817)

random.seed(random_seed)


def main():





    ############################ PREPROCESSING ########################################

    # reading the json file from the test set

    # we'll start easy by reading the first one

    #  reading

    filename = 'test02.json'

    with open('test_data/'+filename, 'r') as file:
        data = json.load(file)


    # create a dic for occupants

    occupants_data = data['occupants']

    # create a dic for patients

    patients_data = data['patients']

    # create a dic for surgeons

    surgeons_data = data['surgeons']

    # create a dic for operating theaters

    operating_theaters_data = data['operating_theaters']

    # create a dic for the nurses

    nurses_data = data['nurses']

    # create a dic for rooms

    rooms_data = data['rooms']

    # modifying the id to be a list of integers

    rooms_mapping = {room["id"]: i for i, room in enumerate(rooms_data)}   # map of the id
    patients_mapping = {patient_data['id']: i for i,patient_data in enumerate(patients_data)}
    occupants_mapping = {occupant_data['id']: i for i,occupant_data in enumerate(occupants_data)}
    surgeons_mapping = {surgeon_data['id']: i for i,surgeon_data in enumerate(surgeons_data)}
    nurses_mapping = {nurse_data['id']: i for i,nurse_data in enumerate(nurses_data)}
    theaters_mapping = {theater_data['id']: i for i,theater_data in enumerate(operating_theaters_data)}

    transformed_data = preprocess(data=data, 
                                  rooms_mapping=rooms_mapping, 
                                  patients_mapping=patients_mapping,
                                  occupants_mapping=occupants_mapping, 
                                  surgeons_mapping=surgeons_mapping, 
                                  nurses_mapping=nurses_mapping,
                                  theaters_mapping=theaters_mapping)
    
    time = transformed_data['T']
    t_occupants = transformed_data['occupants']
    t_patients = transformed_data['patients']
    t_surgeons = transformed_data['surgeons']
    t_nurses= transformed_data['nurses']
    t_theaters = transformed_data['theaters']
    t_rooms = transformed_data['rooms']

    shift_map = transformed_data['shift_mapping']
    #age_map = transformed_data['age_mapping']
    weights = transformed_data['weights']
    shifts = transformed_data['shifts']





    ############################ CLASSES ########################################

    # creating the hospital

    times = Times(time, shifts)
    rooms = Rooms(t_rooms, times)
    theaters = Theaters(t_theaters)

    # creating the patients

    patients = [Patient(t_patient,times) for t_patient in t_patients]

    # creating the occupants 

    occupants = [Occupant(t_occupant,times) for t_occupant in t_occupants]

    # creating the surgeons

    surgeons = [Surgeon(t_surgeon) for t_surgeon in t_surgeons]

    # creating the nurses

    nurses = [Nurse(t_nurse,time,shift_map) for t_nurse in t_nurses]
    

    ############################### SOLVING PROBLEM ##################################

    # initial solution

    #solution = Solution(times, rooms, patients, surgeons, nurses)    # initializing the class solution

    starting_point = Solution(times, rooms, patients, surgeons, nurses)    # starting point is a solution class

    init_solution = initial_solution(starting_point, occupants, patients, surgeons, nurses, rooms, theaters, time, shifts)


    problem = Problem(occupants, patients, surgeons, nurses, rooms, theaters, time, shifts , weights)

    # solving the problem

    number_of_iterations = 100

    problem.constraints(init_solution, patients, surgeons, rooms, theaters, time, shifts, True)

    #visual_schedule(init_solution, occupants, rooms, time)

    solver = ALNS(problem, init_solution)

    final_solution, final_problem, x_plot, y_plot = solver.solve(number_of_iterations)

    visual_schedule(final_solution, occupants, rooms, time)
    print("########################################################################")
    visual_nurses(final_solution, rooms, time, shifts)

    # printing the sol

    if final_problem.constraints(final_solution, patients, surgeons, final_problem.rooms, theaters, time, shifts):
        print(" ")
        print(" ")
        print(" ")
        print("**********************************")
        print(Fore.GREEN +"The solution is feasible"+ Style.RESET_ALL)
        print("**********************************")
        tot_cost, cost_dic = final_problem.objective_function(final_solution, occupants, surgeons, nurses, final_problem.rooms, time, shifts, weights)
        print("The total cost is: ", tot_cost)
        print("**********************************") 
        print("The cost of each part is")
        for key, value in cost_dic.items():
            print(key, ":", value)
    else:
        print("**********************************")
        print(" ")
        print(" ")
        print(" ")
        print("**********************************")
        print(Fore.RED +"The solution is not feasible"+ Style.RESET_ALL)
        print(" ")
        print(" ")
        print(" ")
        result = final_problem.constraints(final_solution, patients, surgeons, final_problem.rooms, theaters, time, shifts, True)
        print("")
        print("")
        print("")
        print("**********************************")

    ######################################## OUTPUT FOR VALIDATION ########################################


    out_sol = postprocess(final_solution, patients, surgeons, nurses, rooms, theaters, time, shifts, shift_map, filename, weights, tot_cost, cost_dic)

    json_object = json.dumps(out_sol, indent=4)

    with open('output_for_validation/'+"out_"+filename, 'w') as file:
        file.write(json_object)


    ######################################## FUNCTION PLOT ########################################

    ALNS_plot(x_plot, y_plot, filename)

if __name__ == "__main__":
    main()
