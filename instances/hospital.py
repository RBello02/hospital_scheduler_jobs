import math
import numpy as np
from instances import patient
from instances import occupant
from instances import surgeon

class Times():

    def __init__(self, T, shifts):
        # For the time
        self.T = T   

        # For the shifts
        self.shifts = shifts


        

class Rooms():

    def __init__(self, rooms):

        self.rooms_id = [room['id'] for room in rooms]  # Save the id of the room 
        self.n_rooms = len(rooms)
        self.rooms_capacity = {room['id']: room['capacity'] for room in rooms} # Maps the capacity of a single room
        self.rooms_count_people ={room['id']:0  for room in rooms} # Tracks people inside a room for each day
        self.rooms_gender = {room['id']:None for room in rooms} # Gender in rooms for each day

    def add_patient(self, room_index, patient):   # add a patient in time t
        if self.rooms_count_people[room_index] == 0:       #if the room is empty add the gender
            self.rooms_gender[room_index] = patient.gender
        self.rooms_count_people[room_index] +=1 

    def remove_patient(self, room_index):
        self.rooms_count_people[room_index] -=1 

    def add_occupant(self, occupant):        # add an occupant in a room at time t
        room_index = self.rooms_id.index(occupant.room_id)
        if self.rooms_count_people[room_index] == 0:       #if the room is empty add the gender
            self.rooms_gender[room_index] = occupant.gender
        self.rooms_count_people[room_index] +=1 

    def remove_occupant(self, occupant):
        room_index = self.rooms_id.index(occupant.room_id)
        self.rooms_count_people[room_index] -=1 

    

        
class Theaters():

    def __init__(self, theaters):
        # For theaters
        self.theaters_id = [i for i, theater in enumerate(theaters)]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = [theater['availability'] for theater in theaters]  # Tracks the capacity of a single theater

        

