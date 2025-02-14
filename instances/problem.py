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

    def constraints(self, solution, occupants, patients, surgeons, nurses, rooms, theaters, T, shifts):

        # H1: no gender mix in the rooms

        for room_id in rooms.rooms_id:
            for t in range(T):
                patients_in_room_at_time_t = [entry['patient'] for entry in solution.patient_schedule
                                                if entry['room'] == room_id and entry['day'] == t]
                
                if not patients_in_room_at_time_t:   # if the room is empty
                    continue       
                
                room_gender = rooms.rooms_gender[t].get(room_id) # get the gender of the room at time t
                if room_gender is not None:
                    for patient in patients_in_room_at_time_t:
                        if patient.gender != room_gender:
                            raise ValueError( f"H1 FAILED: Gender mix in room {room_id} at time {t}: "
                                              f"Patient {patient.id} has gender {patient.gender}, "
                                              f"while the room is assigned to {room_gender}." )
                        

        # H2 : every patient must stay in their compatible rooms, we'll check also that everyone stay in one and only one room

        
        for patient in patients:
            room_for_patient = set ()  # set where is stored the rooms of the patient during the period
            compatible_rooms_for_patient = set(patient.compatible_room_ids)
            for t in range(T):
                room_at_t ={entry['room'] for entry in solution.patient_schedule
                            if entry['patient'] == patient.id and entry['day']==t}
                room_for_patient.update(room_at_t)

            if not room_for_patient:  # if the patient has no room assigned ( in python an empty set is a boolean False )
                raise ValueError(f"H2 FAILED: Patient {patient.id} has no assigned room")
            
            if len(room_for_patient) != 1: # if he changes rooms 
                raise ValueError( f"H2 FAILED: The patient {patient.id} changes rooms during his stay" )
            
            if not room_for_patient.issubset(compatible_rooms_for_patient): # if he stays in rooms were he can't stay
                raise ValueError( f"H2 FAILED: The patient {patient.id} is assigned to incompatible rooms" )
            
            
        # H7: the patient in one room must not exceed the maximal capacity

        capacity = rooms.rooms_capacity
        number_of_patients = rooms.rooms_count_people

        for room_id in rooms.rooms_id:
            for t in range(T):
                if number_of_patients[t][room_id] > capacity[t][room_id]:
                    raise ValueError( f"H7 FAILED: Exceed maximal capacity of the room {room_id} at time {t}" )
                

        # H3: do not exceed the daily maximal time of a surgeon
            # remember that the arriving day is also the operation day

        for surgeon in surgeons:
            operated_patients_by_surgeon = [entry['patient'] for row in solution.surgeons_operations 
                                            for entry in row if entry['surgeon'].id == surgeon.id 
                                            and entry['patient'] is not None]
            
            arrival_times = { patient: min(entry['day'] for entry in solution.patient_schedule if entry['patient'] == patient)
                             for patient in operated_patients_by_surgeon}

            for t in range(T):
                total_time_of_operation = 0
                for operated_patient_by_surgeon in operated_patients_by_surgeon:
                    if t == arrival_times.get(operated_patient_by_surgeon):
                        total_time_of_operation += operated_patient_by_surgeon.surgery_duration
                if total_time_of_operation > surgeon.max_surgery_time[t]:
                    raise ValueError( f"H3 FAILED: Exceed maximal operation capacity for surgeon {surgeon.id} at time {t}, requested: {total_time_of_operation} | maximal: {surgeon.max_surgery_time[t]}" )



        # H4: the duration of all the surgery at time t must not exceed the maximal daily capacity of the theater

        theaters_usage = {t: {theater_id: 0 for theater_id in theaters.theaters_id} for t in T}    # time of daily operations

        for t in T:
            for row in solution.surgeons_operations:
                for entry in row:
                    if entry['patient'] is not None and entry['theater'] is not None:
                        patient = entry['patient']
                        theater = entry['theater']
                        
                        # Check if the operation is scheduled for day t
                        if patient.surgery_due_day == t:
                            # Add the surgery duration to the operating theater usage
                            if theater not in theaters_usage[t]:
                                theaters_usage[t][theater] = 0  # Initialize the usage time if it's not already present
                            theaters_usage[t][theater] += patient.surgery_duration

        for t in range(T):
            for theater_id in theaters.theaters_id:
                if theaters_usage[t][theater_id] > theaters.theaters_capacity[theater_id]:
                    raise ValueError( f"H4 FAILED: Exceed maximal operation capacity for the theater {theater_id} at time {t}, requested: {theaters_usage[t][theater_id]} | maximal: {theaters.theaters_capacity[theater_id]}" )

                    







        


