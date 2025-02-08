import math 
import numpy as np


class Occupant():

    def __init__(self, occupant_data):
        self.id = occupant_data['id']
        self.age_group = occupant_data['age_group']
        self.gender = occupant_data['gender']
        self.length_of_stay = occupant_data['length_of_stay']
        self.workload_produced = occupant_data['workload_produced']
        self.skill_level_required = occupant_data['skill_level_required']
        self.room_id = occupant_data['room_id']

    def __str__(self):
        return f"Occupant ID: {self.id}, Age Group: {self.age_group}, Gender: {self.gender}"
            
        
        