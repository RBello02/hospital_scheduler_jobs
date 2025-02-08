import math 
import numpy as np


class Nurse():

    def __init__(self, nurse_data):
        self.id = nurse_data['id']
        self.skill_level = nurse_data['skill_level']
        self.working_shifts = nurse_data['working_shifts']

    def __str__(self):
        return f"Nurse ID: {self.id}, Skill Level: {self.skill_level}"