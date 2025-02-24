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
            compatible_rooms_for_patient = set(patient.compatible_room_ids)

            assigned_room = next((entry['room'] for entry in solution.patient_schedule 
                          if entry['patient'] == patient), None)

            if assigned_room is None:  # if a patient has no room assigned 
                print(Fore.YELLOW + f"H2 FAILED: Patient {patient.id} has no assigned room")
                counter += 1
            elif assigned_room not in patient.compatible_room_ids:  # if the room is not compatible
                print(Fore.YELLOW + f"H2 FAILED: The patient {patient.id} is assigned to an incompatible room")
                counter += 1
        
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
            
            arrival_times = {entry['patient']: entry['day'] for entry in solution.patient_schedule}

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
                print(Fore.YELLOW + f"H6 FAILED: Patient {patient.id} has an admission day ({day}) that is earlier than their release day ({patient.surgery_release_day}).")

            if check != 0:
                check = False


        # H7: Added a new constraint, all the rooms should be viewed by a nurse 

        for day in range(T):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    counter = 0
                    for nurse in solution.nurses_schedule[day][shift][room_id]:
                        if nurse['room'] is not None:  
                            counter += 1
                    if counter == 0:
                        print(Fore.YELLOW + f"H7 FAILED: Room {room_id} has no nurse in day {day} during the shift {shift}")
                        check = False
                    if counter > 1:
                        print(Fore.YELLOW + f"H7 FAILED: more then one nurse in the room {room_id} in day {day} in shift {shift}")
                        check = False


        return check  # end value
    

    def objective_function(self, age_map, solution, occupants, patients, surgeons, nurses, rooms, theaters, T, shifts, weights):

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

        
        # S2: we shouldn't have a nurse with a skill level X working in a room where there is a patient with a skill level Y with Y > X

        S2 = 0         # the sum that we should minimize
        for day in range(T):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    nurse_working_in_room = solution.nurses_schedule[day][shift][room_id]['nurse']
                    nurse_skill = nurse_working_in_room.skill_level    

                    patients_in_room = [entry['patient'] for entry in solution.patient_schedule
                                        if entry['room'] == room_id and entry['day'] == day]
                    
                    for patient in patients_in_room:       # delay for the patients
                        if patient.skill_level_required[day][shift] > nurse_skill:
                            S2 += patient.skill_level_required[day][shift] - nurse_skill
                        
                    for occupant in occupants:    # delay for the occupants
                        if occupant.room_id == room_id:    # check if the occupant is in the room
                            if occupant.skill_level_required[day][shift] > nurse_skill:
                                S2 += occupant.skill_level_required[day][shift] - nurse_skill

        
        # S3: minimize the total number of nurses that provide a care to a single patient,
        # we know each patient stays in only one room during their recovery (H2)

        S3 = 0

        # observe that each patient has at least 3 nurses, one for each shift 

        for occupant in occupants: # for the occupants
            room_id = occupant.room_id
            arriving_time = 0
            exit_time = occupant.length_of_stay
            total_nurses = set()   # set with all the nurses for the occupant
            for day in range(arriving_time, exit_time + 1):
                for shift in shifts:
                    nurse = solution.nurse_schedule[day][shift][room_id]
                    total_nurses.add(nurse)
            S3 += (len(total_nurses) - 3)     # -3 because we want 0 to be the minimum value of the function

        for patient_s in solution.patient_schedule:  # for the patient
            room_id = patient_s['room']      # this is not a patient object but a dic
            arriving_time = patient_s['day']
            exit_time = patient_s['patient'].length_of_stay + arriving_time
            total_nurses = set()   # create a set where store all the nurses that take care of the patient
            for day in range(arriving_time, exit_time + 1):    # +1 because range does'nt take the last element
                for shift in shifts:
                    nurse = solution.nurse_schedule[day][shift][room_id]
                    total_nurses.add(nurse)    # update the set with nurse
            S3 += (len(total_nurses) - 3)     # -3 because we want 0 to be the minimum value of the function

        
        # S4: for all the shifts, the workload of all the patient in a room can't exceed the workload of the nurse in that turn

        S4 = 0

        for day in range(T):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    nurse = solution.nurse_schedule[day][shift][room_id]    # get the nurse that work in that time
                    max_load = nurse.possible_turns[day][shift]
                    room_load = 0
                    for patient_s in solution.patient_schedule:     # it is not a patient object but a dic
                        if patient_s['room'] == room_id:   # check if it is in the room
                            patient = patient_s['patient']
                            arriving_time = patient_s['day']
                            exit_time = patient_s['patient'].length_of_stay + arriving_time  # the next check is not essential because workload = 0 if the patient is not in the Hospital
                            if arriving_time <= day and exit_time >= day: # check if the patient is in the hospital in that day
                                room_load += patient.workload_produced[day][shift]    
                    
                    for occupant in occupants: # just remember that there's also the occupants in the room
                        if occupant.room_id == room_id:  # if he/she is in the room
                            arriving_time = 0
                            exit_time = occupant.length_of_stay + arriving_time
                            if arriving_time <= day and exit_time >= day: # check if the occupant is in the hospital in that day
                                room_load += occupant.workload_produced[day][shift]  

                    if max_load < room_load:   # check if the load of a nurse is not sufficient for the room
                        S4 += room_load-max_load
                    

                





                    







        


