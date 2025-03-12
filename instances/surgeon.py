import math 
import numpy as np


class Surgeon():

    def __init__(self, surgeon_data):
        self.id = surgeon_data['id']
        self.max_surgery_time = surgeon_data['max_surgery_time']

    def __str__(self):
        return f"Surgeon ID: {self.id}"
    
    
            