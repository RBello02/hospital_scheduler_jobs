import math
import numpy as np
import random

class Problem ():

    def __init__(self, solution , occupants, patients, surgeons, nurses, rooms, theaters, T, shifts , weights):

        self.occupants = occupants
        self.patients = patients
        self.surgeons = surgeons
        self.nurses = nurses
        self.rooms = rooms
        self.theaters = theaters
        self.weights = weights
        self.T = T
        self.shifts = shifts
        self.solution = solution

        # first of all we have to add the occupants to the hospital

        for occupant in occupants:
            self.rooms.add_occupant(occupant)



    # creating a function for checking the Hard constraints

    def constraints(self, solution, occupants, patients, surgeons, nurses, rooms, theaters, times):

        # H1: no gender mix in the rooms

        for room_id in self.rooms.rooms_id:
            for t in self.T:
                patients_in_room_at_time_t = [entry['patient'] for entry in self.solution.patient_schedule
                                                if entry['room'] == room_id and entry['day'] == t]
                
                room_gender = self.rooms.rooms_gender.get(room_id) # get the gender of the room
                if room_gender is not None:
                    for patient in patients_in_room_at_time_t:
                        if patient.gender != room_gender:
                            raise ValueError( f"Gender mix in room {room_id} at time {t}: "
                                              f"Patient {patient.id} has gender {patient.gender}, "
                                              f"while the room is assigned to {room_gender}." )
                        

        # H2 : every patient must stay in their compatible rooms, we'll check also that everyone stay in one and only one room

        
        for patient in self.patients:
            room_for_patient = set ()  # set where is stored the rooms of the patient during the period
            compatible_rooms_for_patient = set(patient.compatible_room_ids)
            for t in self.T:
                room_at_t ={entry['room'] for entry in self.solution.patient_schedule
                                              if entry['patient'] == patient.id and entry['day']==t}
                room_for_patient.update(room_at_t)

            if not room_for_patient:  # if the patient has no room assigned ( in python an empty set is a boolean False )
                raise ValueError(f"Patient {patient.id} has no assigned room")
            
            if len(room_for_patient) != 1: # if he changes rooms 
                raise ValueError( f"The patient {patient.id} changes rooms during his stay" )
            
            if not room_for_patient.issubset(compatible_rooms_for_patient): # if he stays in rooms were he can't stay
                raise ValueError( f"The patient {patient.id} is assigned to incompatible rooms" )
            
            
        # H7: the patient in one room must not exceed the maximal capacity

        capacity = self.rooms.rooms_capacity
        number_of_patients = self.rooms.rooms_count_people

        for room_index in self.rooms.rooms_id:
            if number_of_patients[room_index] > capacity[room_index]:
                raise ValueError( f"Exceed maximal capacity of the room {room_index}" )


                        
                







        


