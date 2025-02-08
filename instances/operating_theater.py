import math 
import numpy as np


class Operating_theater():

    def __init__(self, theater_data):
        self.id = theater_data['id']
        self.availability = theater_data['availability']

    def __str__(self):
        return f"Theater ID: {self.id}"