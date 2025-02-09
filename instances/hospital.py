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
        self.rooms_people_inside = [[[None for _ in range(next((room["capacity"] for room in rooms if room["id"] == room_id), None))] for room_id in self.rooms_id] for t in range(self.T) ]# Tracks people inside a room for each day
        self.rooms_gender = [[None for _ in range(len(rooms))] for t in range(self.T)]  # Gender in rooms for each day

        # For theaters
        self.theaters_id = [i for i, theater in enumerate(theaters)]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = [[theater['availability'] for theater in theaters] for t in range(self.T)]  # Tracks the capacity of a single theater

        
    def add_patient(self, room_index, start_day, patient):   # add a patient in time t
        for t in range(start_day, start_day + patient.length_of_stay):
            if all(x is None for x in self.rooms_people_inside[t][room_index]):  # if the room is empty we add the occupant and set the gender of the room
                self.rooms_people_inside[t][room_index][0] = patient.id
                self.rooms_gender[t][room_index] = patient.gender
            elif any(x is None for x in self.rooms_people_inside[t][room_index]):   # check if there a place in the room
                if patient.gender != self.rooms_gender[t][room_index]:   # check if they have the same gender
                    raise ValueError("The patient ", patient.id, "has incompatible gender with the room", room_index)
                else:
                    idx = next((i for i, x in enumerate(self.rooms_people_inside[t][room_index]) if x is None), None)
                    self.rooms_people_inside[t][room_index][idx] = patient.id  # add the occupant in the room
            else:
                raise ValueError("No place in the room for the occupant: ", patient.id)
            

    def add_occupant(self, occupant):        # add an occupant in a room at time t
        exit = occupant.length_of_stay
        room_index = self.rooms_id.index(occupant.room_id)
        for t in range(exit):
            if all(x is None for x in self.rooms_people_inside[t][room_index]):  # if the room is empty we add the occupant and set the gender of the room
                self.rooms_people_inside[t][room_index][0] = occupant.id
                self.rooms_gender[t][room_index] = occupant.gender
            elif any(x is None for x in self.rooms_people_inside[t][room_index]):   # check if there a place in the room
                if occupant.gender != self.rooms_gender[t][room_index]:   # check if they have the same gender
                    raise ValueError("The occupant ", occupant.id, "has incompatible gender with the room", occupant.room_id)
                else:
                    idx = next((i for i, x in enumerate(self.rooms_people_inside[t][room_index]) if x is None), None)
                    self.rooms_people_inside[t][room_index][idx] = occupant.id  # add the occupant in the room
            else:
                raise ValueError("No place in the room for the occupant: ", occupant.id)
            

    def operation(self, patient, theater, t):
            
