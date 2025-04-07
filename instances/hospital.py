import math
import numpy as np
from instances import patient
from instances import occupant
from instances import surgeon

class Times :

    def __init__(self, T, shifts):
        # For the time
        self.T = T   

        # For the shifts
        self.shifts = shifts

        def __str__(self):
            return f"Time: {self.T} Shifts: {self.shifts}"

        

class Rooms:

    def __init__(self, rooms, tempo):

        self.rooms_id = [room['id'] for room in rooms]  # Save the id of the room 
        self.n_rooms = len(rooms)
        self.rooms_capacity = {room['id']: room['capacity'] for room in rooms} # Maps the capacity of a single room
        self.rooms_count_people =[{room['id']:0 for room in rooms} for _ in range(tempo.T)] # Tracks people inside a room for each day
        self.rooms_gender = [{room['id']:None for room in rooms} for _ in range(tempo.T)] # Gender in rooms for each day

    def add_patient(self, room_index, patient, starting_time, T):   # add a patient in time t
        for t in range(starting_time, min(starting_time + patient.length_of_stay, T)):         # i'll consider the min because i don't want to consider a time that exceed T
            if self.rooms_count_people[t][room_index] == 0:       #if the room is empty add the gender
                self.rooms_gender[t][room_index] = patient.gender
            self.rooms_count_people[t][room_index] +=1 

    def remove_patient(self, room_index , patient, starting_time, T):
        #print(f"Removing patient from room {room_index} starting at time {starting_time}")

        for t in range(starting_time, min(starting_time + patient.length_of_stay, T)):         # i'll consider the min because i don't want to consider a time that exceed T
            if self.rooms_count_people[t][room_index] > 0:
                if self.rooms_count_people[t][room_index] == 1:       # if we have only one patient, and we kick he off, there is no more gender in the room
                    self.rooms_gender[t][room_index] = None
                #print('before', self.rooms_count_people[t][room_index])
                self.rooms_count_people[t][room_index] = self.rooms_count_people[t][room_index] - 1
                #print('after', self.rooms_count_people[t][room_index])


    def add_occupant(self, occupant, T):        # add an occupant in a room at time t
        room_index = self.rooms_id.index(occupant.room_id)
        for t in range(min(occupant.length_of_stay,T)):  # same reason 
            if self.rooms_count_people[t][room_index] == 0:       #if the room is empty add the gender
                self.rooms_gender[t][room_index] = occupant.gender
            self.rooms_count_people[t][room_index] +=1 

    def __str__(self):
        return f"Rooms ID: {self.rooms_id} Number of Rooms: {self.n_rooms} Rooms Capacity: {self.rooms_capacity} Rooms Count People: {self.rooms_count_people}"
    

        
class Theaters :

    def __init__(self, theaters):
        # For theaters
        self.theaters_id = [theater['id'] for theater in theaters]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = {theater['id']:theater['availability'] for theater in theaters} # Tracks the capacity of a single theater

    def __str__(self):
        return f"Theaters ID: {self.theaters_id} Number of Theaters: {self.n_theaters} Theaters Capacity: {self.theaters_capacity}"

        

