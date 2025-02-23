import math 
import numpy as np


class Occupant():

    def __init__(self, occupant_data, Tempo):
        self.id = occupant_data['id']
        self.age_group = occupant_data['age_group']
        self.gender = occupant_data['gender']
        self.length_of_stay = occupant_data['length_of_stay']

        T = Tempo.T
        shifts = Tempo.shifts

        self.skill_level_required = [[0 for _ in shifts] for _ in range(T)]
        self.workload_produced =  [[0 for _ in shifts] for _ in range(T)]

        for x in range(len(occupant_data['workload_produced'])):
            day = x//len(shifts)
            shift = x%len(shifts)
            self.workload_produced[day][shift] = occupant_data['workload_produced'][x]

        for x in range(len(occupant_data['skill_level_required'])):
            day = x//len(shifts)
            shift = x%len(shifts)
            self.skill_level_required[day][shift] = occupant_data['skill_level_required'][x]

        self.room_id = occupant_data['room_id']

    def __str__(self):
        return f"Occupant ID: {self.id}, Age Group: {self.age_group}, Gender: {self.gender}"
            
        
        