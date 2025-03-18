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



    # creating a function for checking the Hard constraints

    def constraints(self, solution, patients, surgeons, nurses, rooms, theaters, T, shifts):      # THERE'S NO NURSES AND OCCUPANTS

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

            if assigned_room is None and patient.mandatory == 1:  # if a patient that must be in the hospital has no room assigned 
                print(Fore.YELLOW + f"H2 FAILED: Patient {patient.id} has no assigned room")
                counter += 1
            elif assigned_room not in patient.compatible_room_ids and patient.mandatory == 1:  # if the room is not compatible
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
                if number_of_patients[t][room_id] > capacity[room_id]:
                    counter += 1
                    print(Fore.YELLOW +  f"H7 FAILED: Exceed maximal capacity of the room {room_id} at time {t}" )
        
        if counter != 0:
            check = False
                

        # H3: do not exceed the daily maximal time of a surgeon
            # remember that the arriving day is also the operation day

        counter = 0
        for surgeon in surgeons:
            operated_patients_by_surgeon = [patient for patient in patients if patient.surgeon_id == surgeon.id]     # get the patient operated by the surgeon
            
            arrival_times = {entry['patient']: entry['day'] for entry in solution.patient_schedule}  # it is a dic that contains the arriving day for each patient

            for t in range(T):
                total_time_of_operation = 0
                for operated_patient_by_surgeon in operated_patients_by_surgeon:   #cycle over the patient operated by the surgeon
                    if t == arrival_times.get(operated_patient_by_surgeon):  # for the arriving day
                        total_time_of_operation += operated_patient_by_surgeon.surgery_duration

                if total_time_of_operation > surgeon.max_surgery_time[t]:
                    print(Fore.YELLOW + f"H3 FAILED: Exceed maximal operation capacity for surgeon {surgeon.id} at time {t}, requested: {total_time_of_operation} | maximal: {surgeon.max_surgery_time[t]}" )
                    counter += 1
            
        if counter != 0:
            check = False



        # H4: the duration of all the surgery at time t must not exceed the maximal daily capacity of the theater

        counter = 0
        theaters_usage =  [ [0 for theater_id in theaters.theaters_id] for t in range(T)]    # time of daily operations

        for t in range(T):
            for patient in patients:
                if solution.surgeons_operations[patient.id]['theater'] is not None:
                    if solution.patient_schedule[patient.id]['day'] == t:    # if the patient is in the hospital
                        theaters_usage[t][solution.surgeons_operations[patient.id]['theater']] += patient.surgery_duration

        for t in range(T):
            for theater_id in theaters.theaters_id:
                if theaters_usage[t][theater_id] > theaters.theaters_capacity[theater_id][t]:
                    counter += 1
                    print(Fore.YELLOW +  f"H4 FAILED: Exceed maximal operation capacity for the theater {theater_id} at time {t}, requested: {theaters_usage[t][theater_id]} | maximal: {theaters.theaters_capacity[theater_id][t]}" )  
        if counter != 0:
            check = False

                    

        # H5: All the mandatory patients must be admitted 
        # H6: They must be admitted in their schedule period

        counter = 0
        for row in solution.patient_schedule:
            patient = row['patient']
            day = row['day']
            if day is None:
                if patient.mandatory == 1:
                    print(Fore.YELLOW + f"H5 FAILED: Patient {patient.id} is mandatory and must be admitted into the hospital.")
                    counter += 1
                continue  # If the patient is optional and not admitted, it's fine

            # H6: Check that mandatory patients are admitted within their allowed period
            if patient.mandatory == 1 and (day < patient.surgery_release_day or day > patient.surgery_due_day):
                counter += 1
                print(Fore.YELLOW + f"H6 FAILED: Patient {patient.id} is mandatory and must be admitted within the scheduling period.")

            # General rule: No patient can be admitted before their release day
            if day < patient.surgery_release_day:
                counter += 1
                print(Fore.YELLOW + f"H6 FAILED: Patient {patient.id} has an admission day ({day}) that is earlier than their release day ({patient.surgery_release_day}).")

        if counter != 0:
            check = False

        """
        # H8|A; added new constraint, for each day and shift, if a room is not empty a nurse must be there

        for day in range(T):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if rooms.rooms_count_people[t][room_id] > 0 and len(solution.nurses_schedule[day][shift][room_id]) == 0: # if there somebody and there isn't a nurse
                        check = False
                        print(Fore.YELLOW + f"H7|A FAILED: room {room_id} during day ({day}) and shift ({shifts}) has no nurse assigned, also if there are ({rooms.rooms_count_people[t][room_id]}) people")
        """

        # H8|A: Added a new constraint, all the rooms that are not empty should be viewed by a nurse 

        for day in range(T):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    counter = 0
                    for nurse in solution.nurses_schedule[day][shift][room_id]:   # nurse is a list dic
                        if nurse['room'] is not None:  
                            counter += 1     # count the number of nurses in the room
                    if counter == 0 and rooms.rooms_count_people[t][room_id]>0:   # if there is no nurse and the room is not empty
                        print(Fore.YELLOW + f"H7|B FAILED: Room {room_id} has no nurse in day {day} during the shift {shift}")
                        check = False
                    if counter > 1 and rooms.rooms_count_people[t][room_id]>0:    # i can put nurses in empty rooms
                        print(Fore.YELLOW + f"H7|B FAILED: more then one nurse in the room {room_id} in day {day} in shift {shift}")
                        check = False

        """

        # H8|B: Add a new constraint, all the nurse should work in their working shifts

        for nurse in nurses:
            for day in range(T):
                for shift in shifts:
                    if nurse.possible_turns[day][shift] > 0: # if the nurse work on that day
                        counter = 0
                        for room_id in rooms.rooms_id:
                            nurse_list_dic = solution.nurses_schedule[day][shift][room_id]   # list of dic
                            for nurse_dic in nurse_list_dic:
                                if nurse_dic['nurse'].id == nurse.id:
                                    counter += 1
                        if counter == 0:
                            print(Fore.YELLOW + f"H8|B FAILED: Nurse {nurse.id} is not working in the shift {shift} in day {day}")
                            check = False"
        """


        return check  # end value
    

    def objective_function(self, solution, occupants, surgeons, nurses,  rooms, T, shifts, weights):   # THERE'S NO PATIENTS,NURSES AND THEATERS, AGE MAP

        # firstly we are gonna extract all the parte that should be minimize, each part is defined by S soft constraints


        # S1: minimize the age difference in each room for each time 

        S1 = 0     # it represents a part of the objective function the we should minimize

        for t in range(T):
            for room_id in rooms.rooms_id:
                patients_in_room_in_day = [entry['patient'] for entry in solution.patient_schedule
                                            if entry['room'] == room_id and t >= entry['day'] and t < entry['day'] + entry['patient'].length_of_stay] 

                occupants_age = [ ]      # it is a list that contains the age of all the occupants in the room
                for occupant in occupants:   # just remember the occupants in the room
                    if occupant.room_id == room_id and occupant.length_of_stay > t:
                        occupants_age.append(occupant.age_group)

                patients_age = [] # it is a list that contains the age of all the patients in the room
                for patient in patients_in_room_in_day:
                    patients_age.append(patient.age_group)

                age = occupants_age + patients_age   # it is a list that contains all the age of the occupants and the patients in the room

                if age:    # if the list is not empty
                    max_age = max(age)  
                    min_age = min(age)  
                    S1 += max_age - min_age  
                else:
                    S1 += 0 
        
        # S2: we shouldn't have a nurse with a skill level X working in a room where there is a patient with a skill level Y with Y > X

        S2 = 0         # the sum that we should minimize
        for room_id in rooms.rooms_id:
            for shift in shifts:
                for day in range(T):
                    nurse_dic_working_in_room = solution.nurses_schedule[day][shift][room_id] # this is a list of dic

                    list_skills = [nurse['nurse'].skill_level for nurse in nurse_dic_working_in_room]   # list of the skill level of the nurses in the room

                    print("nurse", nurse_dic_working_in_room[0]['nurse'].id, "skill", list_skills)

                    nurse_skill = max(list_skills)   # the skill level is maximum skill level in the rooms

                    patients_in_room = [entry['patient'] for entry in solution.patient_schedule
                                        if entry['room'] == room_id and day >= entry['day'] and day < entry['day'] + entry['patient'].length_of_stay]  # get the patients in the room
                    
                    for patient in patients_in_room:       # delay for the patients

                        admission_day = solution.patient_schedule[patient.id]['day']   # the day in which the patient arrives  
                        print("patient", patient.id, "skill", patient.skill_level_required[day-admission_day][shift], "nurse id: ", nurse_dic_working_in_room[0]['nurse'].id,"nurse skill", nurse_skill, "day: ", day, "shift: ", shift, "room: ", room_id) 

                        if patient.skill_level_required[day-admission_day][shift] > nurse_skill:
                            S2 += patient.skill_level_required[day-admission_day][shift] - nurse_skill
                            print("***************** look up *****************")
                            print(S2)
                        
                    for occupant in occupants:    # delay for the occupants
                        if occupant.room_id == room_id and occupant.length_of_stay < day:    # check if the occupant is in the room
                            print("occupant", occupant.id, "skill", occupant.skill_level_required[day][shift], "nurse id:",nurse_dic_working_in_room[0]['nurse'].id, "nurse skill", nurse_skill, "day: ", day, "shift: ", shift, "room: ", room_id)
                            if occupant.skill_level_required[day][shift] > nurse_skill:
                                S2 += occupant.skill_level_required[day][shift] - nurse_skill
                                print("***************** look up *****************")
                                print(S2)

        
        # S3: minimize the total number of nurses that provide a care to a single patient,
        # we know each patient stays in only one room during their recovery (H2)

        S3 = 0

        # observe that each patient has at least 3 nurses, one for each shift 

        for occupant in occupants: # for the occupants
            room_id = occupant.room_id
            arriving_time = 0
            exit_time = occupant.length_of_stay
            total_nurses = set()   # set with all the nurses for the occupant
            for day in range(arriving_time, exit_time):
                for shift in shifts:
                    nurses_in_the_room = solution.nurses_schedule[day][shift][room_id]
                    for nurse in nurses_in_the_room:
                        total_nurses.add(nurse['nurse'])   # this is a dic
            S3 += (len(total_nurses))   # changed for the last update of the competition  # -3 because we want 0 to be the minimum value of the function

        for patient_s in solution.patient_schedule:  # for the patient
            room_id = patient_s['room']      # this is not a patient object but a dic
            arriving_time = patient_s['day']
            if arriving_time is not None:  # it means that the patient is in the hospital
                exit_time = patient_s['patient'].length_of_stay + arriving_time
                total_nurses = set()   # create a set where store all the nurses that take care of the patient
                for day in range(arriving_time, min(T,exit_time)):    # +1 because range does'nt take the last element
                    for shift in shifts:
                        nurses_in_the_room = solution.nurses_schedule[day][shift][room_id]
                        for nurse in nurses_in_the_room:
                            total_nurses.add(nurse['nurse'])    # update the set with nurse
                S3 += (len(total_nurses))     # changed in the last update of the competition : # -3 because we want 0 to be the minimum value of the function

        
        # S4: for all the shifts, the workload of all the patient in a room can't exceed the workload of the nurse in that turn

        S4 = 0
        
        for nurse in nurses:
            for day in range(T):
                for shift in shifts:
                    if nurse.possible_turns[day][shift] > 0:   # check if the nurse can work
                        nurse_load = nurse.possible_turns[day][shift]   # the workload of the nurse
                        room_load = 0
                        for room_id in rooms.rooms_id:
                            if solution.nurses_schedule[day][shift][room_id]:   # check if the list is not empty,
                                for nurse_dic in solution.nurses_schedule[day][shift][room_id]:
                                    if nurse_dic['nurse'].id == nurse.id and nurse_dic['room'] == room_id:        # check if the nurse is in the room
                                        # FOR THE PATIENTS
                                        for patient_s in solution.patient_schedule:     # it is not a patient object but a dic
                                            if patient_s['room'] == room_id:   # check if it is in the room
                                                patient = patient_s['patient']
                                                arriving_time = patient_s['day']
                                                exit_time = patient_s['patient'].length_of_stay + arriving_time  # the next check is not essential because workload = 0 if the patient is not in the Hospital
                                                if arriving_time <= day and exit_time > day: # check if the patient is in the hospital in that day
                                                    room_load += patient.workload_produced[day-arriving_time][shift] 
                                                    #print("patient id: ", patient.id, "patient load: ", patient.workload_produced[day][shift])
                                        # FOR THE OCCUPANTS    
                                        for occupant in occupants: # just remember that there's also the occupants in the room
                                            if occupant.room_id == room_id:  # if he/she is in the room
                                                arriving_time = 0
                                                exit_time = occupant.length_of_stay + arriving_time
                                                if arriving_time <= day and exit_time > day: # check if the occupant is in the hospital in that day
                                                    room_load += occupant.workload_produced[day][shift]
                                                    #print("occupant id: ", occupant.id, "occupant load: ", occupant.workload_produced[day][shift])
                        #print("day: ", day, "shift: ", shift, "nurse id: n",nurse.id , "nurse load: ", nurse_load, "room load: ", room_load)
                        if nurse_load < room_load:   # check if the load of a nurse is not sufficient for the room
                            S4 += room_load-nurse_load
                            #print(" ****************** look up *****************")
    


        

        # S5: the number of theaters opened per day should be minimized

        S5 = 0

        for day in range(T):
            theaters_per_day = {patient_ops['theater'] for patient_ops in solution.surgeons_operations 
                                if patient_ops['patient'] in [p['patient'] for p in solution.patient_schedule if p['day'] == day]}
            S5 += len(theaters_per_day)

        
        # S6: the number of different theaters assigned to a surgeon per day should be minimize

        S6 = 0

        for day in range(T):
            for surgeon in surgeons:
                theaters_to_surgeon = {patient_ops['theater'] for patient_ops in solution.surgeons_operations     # get the theaters
                                       if patient_ops['patient'] in [p['patient'] for p in solution.patient_schedule if p['day'] == day] # if there is a patient that is under surgeon on that day
                                       and patient_ops['theater'] is not None and patient_ops['patient'].surgeon_id == surgeon.id} # if the theater is not None and the patient is operated by that surgeon
                if len(theaters_to_surgeon) > 0:   
                    S6 += len(theaters_to_surgeon)-1   # I dont have to count it if the surgeon stays in the same theater for all the day, that's because -1

    
        # S7: the number of days between the admission date and the release date should be minimize

        S7 = 0

        for p_schedule in solution.patient_schedule:
            patient = p_schedule['patient']
            release = patient.surgery_release_day   # it's the day in which the patient should arrive
            admission = p_schedule['day']          # it's the day in which the patient arrives
            if admission is not None:
                S7 += admission - release


        # S8: the number of optional patients that are not admitted should be minimize

        S8 = 0

        for p_schedule in solution.patient_schedule:
            patient = p_schedule['patient']
            if patient.mandatory == 0 and p_schedule['day'] is None:    # if a not mandatory patient doesn't enter in the Hospital
                S8 += 1


        # Now we can construct the objective function:

        Objective_function_1 = weights['room_mixed_age']*S1 + weights['room_nurse_skill']*S2 + weights['continuity_of_care']*S3
        Objective_function_2 = weights['nurse_eccessive_workload']*S4 + weights['open_operating_theater']*S5 + weights['surgeon_transfer']*S6
        Objective_function_3 = weights['patient_delay']*S7 + weights['unscheduled_optional']*S8

        Cost_dic = {
                   'S1': weights['room_mixed_age']*S1 ,
                   'S2': weights['room_nurse_skill']*S2 ,
                   'S3': weights['continuity_of_care']*S3 ,
                   'S4': weights['nurse_eccessive_workload']*S4 ,
                   'S5': weights['open_operating_theater']*S5 ,
                   'S6': weights['surgeon_transfer']*S6 ,
                   'S7': weights['patient_delay']*S7 ,
                   'S8': weights['unscheduled_optional']*S8
                }
    

        return (Objective_function_1 + Objective_function_2 + Objective_function_3, Cost_dic)







                    







        


