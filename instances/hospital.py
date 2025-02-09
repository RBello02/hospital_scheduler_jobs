import math
import numpy as np
from instances import patient
from instances import occupant
from instances import surgeon

class Hospital():

    def __init__(self, rooms, theaters, T):
        # For the time
        self.T = T   

        # For rooms
        self.rooms_id = [room['id'] for room in rooms]  # Save the id of the room 
        self.n_rooms = len(rooms)
        self.rooms_capacity = [room['capacity'] for room in rooms]  # Maps the capacity of a single room
        self.rooms_count_people =[[0 for room in range(self.n_rooms)] for t in range (self.T)] # Tracks people inside a room for each day
        self.rooms_gender = [[None for _ in range(self.n_rooms)] for t in range(self.T)]  # Gender in rooms for each day

        # For theaters
        self.theaters_id = [i for i, theater in enumerate(theaters)]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = [[theater['availability'] for theater in theaters] for t in range(self.T)]  # Tracks the capacity of a single theater

        
    def add_patient(self, room_index, start_day, patient):   # add a patient in time t
        for t in range(start_day, start_day + patient.length_of_stay):
            self.rooms_count_people[t][room_index] +=1 


    def add_occupant(self, occupant):        # add an occupant in a room at time t
        exit = occupant.length_of_stay
        room_index = self.rooms_id.index(occupant.room_id)
        for t in range(exit):
            self.rooms_count_people[t][room_index] +=1 
            
            
