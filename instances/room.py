import math 
import numpy as np


class Room():

    def __init__(self, room_data):
        self.id = room_data['id']
        self.capacity= room_data['capacity']

    def __str__(self):
        return f"Room ID: {self.id}, Capacity: {self.capacity}"