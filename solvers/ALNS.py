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


    def solve(self, number_of_iterations = 1000, Gamma = 1, rho = 1, Delta = [4,3,2,1]):   # main function for the solver

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
        repair_prob_vec, destroy_prob_vec = [], []
        x_data.append(0)
        current_value, dic = starting_problem.objective_function(current_point, occupants, surgeons, nurses,  rooms, T, shifts, weights)
        y_data.append(current_value)
        # ********************

        # *************** defining the weights for the destroy and repair
        destroy_weights = [1]*15
        repair_weights = [1]*4

        destroy_weights_dic = {'A': destroy_weights[0], 'B': destroy_weights[1], 'C': destroy_weights[2], 
                               'D': destroy_weights[3], 'E': destroy_weights[4], 'F': destroy_weights[5], 
                               'G': destroy_weights[6], 'H': destroy_weights[7], 'I': destroy_weights[8], 
                               'L': destroy_weights[9], 'M': destroy_weights[10], 'N': destroy_weights[11], 
                               'O': destroy_weights[12], 'P': destroy_weights[13], 'Q': destroy_weights[14]}

        repair_weights_dic = {'A': repair_weights[0], 'B': repair_weights[1], 'C': repair_weights[2], 'D': repair_weights[3]}

        destroy_probabilities = [weights/sum(destroy_weights) for weights in destroy_weights]
        repair_probabilities = [weights/sum(repair_weights) for weights in repair_weights]

        destroy_prob_dic = {'A': destroy_probabilities[0], 'B': destroy_probabilities[1], 'C': destroy_probabilities[2], 
                            'D': destroy_probabilities[3], 'E': destroy_probabilities[4], 'F': destroy_probabilities[5], 
                            'G': destroy_probabilities[6], 'H': destroy_probabilities[7], 'I': destroy_probabilities[8], 
                            'L': destroy_probabilities[9], 'M': destroy_probabilities[10], 'N': destroy_probabilities[11], 
                            'O': destroy_probabilities[12], 'P': destroy_probabilities[13], 'Q': destroy_probabilities[14]}
        
        destroy_prob_vec.append(destroy_prob_dic)
        
        repair_prob_dic = {'A': repair_probabilities[0], 'B': repair_probabilities[1], 'C': repair_probabilities[2], 'D': repair_probabilities[3]}

        repair_prob_vec.append(repair_prob_dic)

        used_destroy = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0, 
                        'H': 0, 'I': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0, 'P': 0, 'Q': 0}   # it is a dic containing the number of times each destroy method is used
        used_repair = {'A': 0, 'B': 0, 'C': 0, 'D': 0}   # it is a dic containing the number of times each repair me
        
        success_destroy = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0, 'G': 0,
                            'H': 0, 'I': 0, 'L': 0, 'M': 0, 'N': 0, 'O': 0, 'P': 0, 'Q': 0}   # it is a dic containing the number of times each destroy method is used successfully
        success_repair = {'A': 0, 'B': 0, 'C': 0, 'D': 0}   # it is a dic containing the number of times each repair method is used successfully
        # ********************

        

        for t in range(number_of_iterations):   # iterating

            show_progress(p_iteration[t])
            time.sleep(0.0001)

            #********************* init*********
            What_happened= [False, False, False, False]   # in this vector we save the result of the destroy and repair methods (its the delta at slide 34)
            #************************************

            # ********** for the plot **********
            x_data.append(t+1)
            # **********************************

            # sampling the destroy and repair
            sampled_destroy = random.choices(list(destroy_prob_dic.keys()), weights=destroy_probabilities, k=1)[0]
            sampled_repair = random.choices(list(repair_prob_dic.keys()), weights=repair_probabilities, k=1)[0]

            point_destroyed,new_rooms = destroy(sampled_destroy,current_point,starting_problem)

            new_problem = Problem(occupants, patients, surgeons, nurses, new_rooms, theaters, T, shifts, weights)

            new_point = repair(sampled_repair, current_point, point_destroyed, new_problem)    # in this case point_destroyed and new_point HAVE THE SAME POINTER

            if not new_problem.constraints( new_point, patients, surgeons, new_rooms, theaters, T, shifts):
                print("")
                print(Fore.YELLOW + f"Destroy and repair have failed" + Style.RESET_ALL)
                print("")
                result = new_problem.constraints( new_point, patients, surgeons, rooms, theaters, T, shifts,True)
                print("")
                return 0

            new_value, dic = new_problem.objective_function(new_point, occupants, surgeons, nurses,  new_rooms, T, shifts, weights) 
            
            if new_value <= current_value or bernoulli(np.exp(-Gamma*(t+1))):

                current_point = copy.deepcopy(new_point)
                starting_problem = copy.deepcopy(new_problem)
                current_value = new_value

                # ************ find what happened *********
                if new_value < min(y_data): # if the new value is the best one so far
                    What_happened[0] = True
                elif new_value <= current_value and not What_happened[0]:   # if we improve the current solution but not the best one so far
                    What_happened[1] = True
                else: # in this case the bernoulli is true
                    What_happened[2] = True

                # ************ for the plot *********
                y_data.append(new_value)
                # ************************************

            else:
                y_data.append(current_value)
                What_happened[3] = True

            destroy_weights, destroy_probabilities, repair_weights, repair_probabilities, destroy_prob_dic, repair_prob_dic, destroy_weights_dic, repair_weights_dic, used_destroy, used_repair, success_destroy, success_repair=adjust_weights(used_destroy, used_repair, success_destroy, success_repair, destroy_weights, destroy_weights_dic,
                                                                                                                                                                                                                                                destroy_probabilities, repair_weights,repair_weights_dic, repair_probabilities, destroy_prob_dic, 
                                                                                                                                                                                                                                                repair_prob_dic, sampled_destroy, sampled_repair, What_happened, Delta, rho)
            destroy_prob_vec.append(destroy_prob_dic)
            repair_prob_vec.append(repair_prob_dic)
            
        return (current_point, starting_problem, x_data,y_data, destroy_prob_vec, repair_prob_vec)   # returning the final solution and the plot data


def show_progress(percent=0, width=30):   # function made only for printing the progress bar
    left = int(width * percent // 100)
    right = width - left
    
    print('\r[', '#' * left, '' * right, ']',
          f' {percent: .0f}%', sep='', end='', flush=True)
    
def bernoulli(p):   # function for the bernoulli distribution
    x = np.random.uniform(0, 1)
    if x <= p:
        return True
    else:
        return False

def adjust_weights(used_destroy, used_repair, success_destroy, success_repair, old_destroy_weights, destroy_weights_dic,
                    destroy_probabilities, old_repair_weights, repair_weights_dic, repair_probabilities, destroy_prob_dic, 
                    repair_prob_dic, destroy_called, repair_called, what_happened, Delta, rho):
    
    # adjust the used destroy and repair 
    used_destroy[destroy_called] += 1
    used_repair[repair_called] += 1

    for i in range(4):
        if what_happened[i]:
            result = i
            break

    win = Delta[result] # increasing value for the successful destroy and repair     

    # adjust the success destroy and repair

    success_destroy[destroy_called] += win
    success_repair[repair_called] += win

    # adjust the destroy weights:

    for i,weight_key in enumerate(destroy_weights_dic.keys()):
        if used_destroy[weight_key] == 0:
            old_destroy_weights[i] = (1-rho)*old_destroy_weights[i]
            destroy_weights_dic[weight_key] = (1-rho)*destroy_weights_dic[weight_key]
        else:
            old_destroy_weights[i] = (1-rho)*old_destroy_weights[i] + (rho*success_destroy[weight_key])/used_destroy[weight_key]
            destroy_weights_dic[weight_key] = (1-rho)*destroy_weights_dic[weight_key] + (rho*success_destroy[weight_key])/used_destroy[weight_key]

    # adjust the repair weights:

    for i,weight_key in enumerate(repair_weights_dic.keys()):
        if used_repair[weight_key] == 0:
            old_repair_weights[i] = (1-rho)*old_repair_weights[i]
            repair_weights_dic[weight_key] = (1-rho)*repair_weights_dic[weight_key]
        else:
            old_repair_weights[i] = (1-rho)*old_repair_weights[i] + (rho*success_repair[weight_key])/used_repair[weight_key]
            repair_weights_dic[weight_key] = (1-rho)*repair_weights_dic[weight_key] + (rho*success_repair[weight_key])/used_repair[weight_key]

    # adjust the probabilities:
    destroy_probabilities = [weights/sum(old_destroy_weights) for weights in old_destroy_weights]
    repair_probabilities = [weights/sum(old_repair_weights) for weights in old_repair_weights]

    # creating the new dic of probabilities:
    destroy_prob_dic = {key: destroy_probabilities[i] for i, key in enumerate(destroy_prob_dic.keys())}
    repair_prob_dic = {key: repair_probabilities[i] for i, key in enumerate(repair_prob_dic.keys())}

    return old_destroy_weights, destroy_probabilities, old_repair_weights, repair_probabilities, destroy_prob_dic, repair_prob_dic, destroy_weights_dic, repair_weights_dic, used_destroy, used_repair, success_destroy, success_repair  
