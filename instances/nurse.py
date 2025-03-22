import math 
import numpy as np


class Nurse :

    def __init__(self, nurse_data, Total_days, shift_map):
        self.id = nurse_data['id']
        self.skill_level = nurse_data['skill_level']
        self.working_shifts = nurse_data['working_shifts']

        # we'll create a matrix that stores the day and the shifts in witch the nurse can work ( the value in the matrix is the max workload )
        # it is a matrix Day x shift
        mat = [[0 for _ in range(3)] for t in range(Total_days)]
        for turn in self.working_shifts:
            day = turn['day']
            shift = shift_map.get(turn['shift'])
            mat[day][shift] = turn['max_load']                           # append the max load of the nurse

        self.possible_turns = mat




    def __str__(self):
        return f"Nurse ID: {self.id}, Skill Level: {self.skill_level}"