import math
import numpy as np
from colorama import Fore
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

        # boolean variable that tells us if all the constraints are ok

        check = True

        # H1: no gender mix in the rooms

        counter = 0
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
                            counter +=1 
                            print(Fore.YELLOW + f"H1 FAILED: Gender mix in room {room_id} at time {t}: "
                                              f"Patient {patient.id} has gender {patient.gender}, "
                                              f"while the room is assigned to {room_gender}." )
        if counter != 0 : 
            check = False
                        

        # H2 : every patient must stay in their compatible rooms, we'll check also that everyone stay in one and only one room

        counter = 0
        for patient in patients:
            room_for_patient = set ()  # set where is stored the rooms of the patient during the period
            compatible_rooms_for_patient = set(patient.compatible_room_ids)
            for t in range(T):
                room_at_t ={entry['room'] for entry in solution.patient_schedule
                            if entry['patient'] == patient.id and entry['day']==t}
                room_for_patient.update(room_at_t)

            if not room_for_patient:  # if the patient has no room assigned ( in python an empty set is a boolean False )
                print(Fore.YELLOW + f"H2 FAILED: Patient {patient.id} has no assigned room")
                counter +=1
            
            if len(room_for_patient) != 1: # if he changes rooms 
                print(Fore.YELLOW + f"H2 FAILED: The patient {patient.id} changes rooms during his stay" )
                counter +=1 
            
            if not room_for_patient.issubset(compatible_rooms_for_patient): # if he stays in rooms were he can't stay
                print(Fore.YELLOW +  f"H2 FAILED: The patient {patient.id} is assigned to incompatible rooms" )
                counter +=1
        
        if counter != 0:
            check = False
            
            
        # H7: the patient in one room must not exceed the maximal capacity

        capacity = rooms.rooms_capacity
        number_of_patients = rooms.rooms_count_people

        counter = 0
        for room_id in rooms.rooms_id:
            for t in range(T):
                if number_of_patients[t][room_id] > capacity[t][room_id]:
                    counter += 1
                    print(Fore.YELLOW +  f"H7 FAILED: Exceed maximal capacity of the room {room_id} at time {t}" )
        
        if counter != 0:
            check = False
                

        # H3: do not exceed the daily maximal time of a surgeon
            # remember that the arriving day is also the operation day

        counter = 0
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
                    print(Fore.YELLOW + f"H3 FAILED: Exceed maximal operation capacity for surgeon {surgeon.id} at time {t}, requested: {total_time_of_operation} | maximal: {surgeon.max_surgery_time[t]}" )
                    counter += 1
            
        if counter != 0:
            check = False



        # H4: the duration of all the surgery at time t must not exceed the maximal daily capacity of the theater

        theaters_usage = {t: {theater_id: 0 for theater_id in theaters.theaters_id} for t in range(T)}    # time of daily operations

        counter = 0
        for t in range(T):
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
                    counter += 1
                    print(Fore.YELLOW +  f"H4 FAILED: Exceed maximal operation capacity for the theater {theater_id} at time {t}, requested: {theaters_usage[t][theater_id]} | maximal: {theaters.theaters_capacity[theater_id]}" )
                
        if counter != 0:
            check = False

        # H5: All the mandatory patients must be admitted 
        # H6: They must be admitted in their schedule period

        counter = 0
        for row in solution.patient_schedule:
            patient = row['patient']
            day = row['day']
            if day is None:
                if patient.mandatory:
                    print(Fore.YELLOW + f"H5 FAILED: Patient {patient.id} is mandatory and must be admitted into the hospital.")
                    counter += 1
                continue  # If the patient is optional and not admitted, it's fine

            # H6: Check that mandatory patients are admitted within their allowed period
            if patient.mandatory and (day < patient.surgery_release_day or day > patient.surgery_due_day):
                counter += 1
                print(Fore.YELLOW + f"H6 FAILED: Patient {patient.id} is mandatory and must be admitted within the scheduling period.")

            # General rule: No patient can be admitted before their release day
            if day < patient.surgery_release_day:
                counter += 1
                print(Fore.YELLOW + f"Patient {patient.id} has an admission day ({day}) that is earlier than their release day ({patient.surgery_release_day}).")

            if check != 0:
                check = False


        return check  # end value
    

    def objective_function(self, age_map, solution, occupants, patients, surgeons, nurses, rooms, theaters, T, shifts):

        # firstly we are gonna extract all the parte that should be minimize, each part is defined by S soft constraints


        # S1: minimize the age difference in each room for each time 

        key_max = max(age_map, key=age_map.get) # firstly we are gonna extract the minimum age end the maximum age
        max_age = age_map[key_max]

        key_min = min(age_map, key=age_map.get) 
        min_age = age_map[key_min]

        S1 = 0     # it represents a part of the objective function the we should minimize

        for t in range(T):
            for room_id in rooms.rooms_id:
                patients_in_room_in_day = [entry['patient'] for entry in solution.patient_schedule
                                            if entry['room'] == room_id and entry['day'] == t]
                
                max_room_day = min_age  # i just shifted the name for the if cases
                min_room_day = max_age

                for occupant in occupants:   # just remember the occupants in the room
                    if occupant.room_id == room_id and occupant.length_of_stay > t:
                        max_room_day = max(max_room_day, occupant.age_group)
                        min_room_day = min(min_room_day, occupant.age_group)

                for patient in patients_in_room_in_day:
                    max_room_day = max(max_room_day, patient.age_group)
                    min_room_day = min(min_room_day, patient.age_group)

                S1 += max_room_day-min_room_day     # add the difference into the variable S1


                    







        


