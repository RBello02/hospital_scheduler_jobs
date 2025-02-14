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

    def __init__(self, rooms, tempo):

        self.rooms_id = [room['id'] for room in rooms]  # Save the id of the room 
        self.n_rooms = len(rooms)
        self.rooms_capacity = [{room['id']: room['capacity'] for room in rooms} for t in tempo] # Maps the capacity of a single room
        self.rooms_count_people =[{room['id']:0  for room in rooms} for t in tempo] # Tracks people inside a room for each day
        self.rooms_gender = [{room['id']:None for room in rooms} for t in tempo] # Gender in rooms for each day

    def add_patient(self, room_index, patient, starting_time):   # add a patient in time t
        for t in range(starting_time, starting_time + patient.length_of_stay):
            if self.rooms_count_people[t][room_index] == 0:       #if the room is empty add the gender
                self.rooms_gender[t][room_index] = patient.gender
            self.rooms_count_people[t][room_index] +=1 

    def add_occupant(self, occupant):        # add an occupant in a room at time t
        room_index = self.rooms_id.index(occupant.room_id)
        for t in range(occupant.length_of_stay):
            if self.rooms_count_people[t][room_index] == 0:       #if the room is empty add the gender
                self.rooms_gender[t][room_index] = occupant.gender
            self.rooms_count_people[t][room_index] +=1 
    

        
class Theaters():

    def __init__(self, theaters):
        # For theaters
        self.theaters_id = [i for i, theater in enumerate(theaters)]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = [theater['availability'] for theater in theaters]  # Tracks the capacity of a single theater

        

