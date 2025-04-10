import random
import copy

from solvers.place_patient import place_patient
from solvers.solution_output import visual_schedule


def repair(CASE_REPAIR, current_point, current_destroyed_point_not_copied,  problem): #main function for the repair phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    T = problem.T
    shifts = problem.shifts

    current_destroyed_point= copy.deepcopy(current_destroyed_point_not_copied)

    if CASE_REPAIR in ['A','B','C', 'D']:

        # we have to find the patients that have been destroyed:


        destroyed_mandatory = []
        mandatory_in_the_hosp = []
        destroyed_not_mandatory = []
        mandatory_patients = []
        not_mandatory_patients = []

        not_mandatory_patients_in_the_hosp = []
        not_mandatory_patients_not_in_the_hosp = []


        for patient_dic, destroyed_patient_dic in zip(current_point.patient_schedule, current_destroyed_point.patient_schedule):

            
            if patient_dic['patient'].mandatory == 1:
                mandatory_patients.append({'patient': patient_dic['patient'],
                                            'delay': patient_dic['patient'].surgery_due_day-patient_dic['patient'].surgery_release_day})
            else:
                not_mandatory_patients.append({'patient': patient_dic['patient'],
                                                'delay': T-patient_dic['patient'].surgery_release_day})

            if patient_dic['day'] is not None and destroyed_patient_dic['day'] is None:
                if patient_dic['patient'].mandatory == 1:
                    destroyed_mandatory.append({'patient': patient_dic['patient'],
                                                'delay': patient_dic['patient'].surgery_due_day-patient_dic['patient'].surgery_release_day})
                else:
                    not_mandatory_patients_not_in_the_hosp.append({'patient': patient_dic['patient'],
                                                                   'delay': T-patient_dic['patient'].surgery_release_day})
                    
            if patient_dic['day'] is not None and destroyed_patient_dic['day'] is not None and patient_dic['patient'].mandatory == 0: 
                not_mandatory_patients_in_the_hosp.append({'patient': patient_dic['patient'],
                                                            'length': patient_dic['patient'].length_of_stay,
                                                            'day': patient_dic['day']})
            if patient_dic['day'] is not None and destroyed_patient_dic['day'] is not None and patient_dic['patient'].mandatory == 1: 
                mandatory_in_the_hosp.append({'patient': patient_dic['patient'],
                                                            'length': patient_dic['patient'].length_of_stay,
                                                            'day': patient_dic['day']})
            if patient_dic['day'] is None and destroyed_patient_dic['day'] is None and patient_dic['patient'].mandatory == 0:
                not_mandatory_patients_not_in_the_hosp.append({'patient': patient_dic['patient'],
                                                                'delay': T-patient_dic['patient'].surgery_release_day})

                
        destroyed_mandatory.sort(key=lambda x: x['delay'])
        
        '''
        print("destroyed_mandatory")
        print("")
        if destroyed_mandatory:
            for pat_dic in destroyed_mandatory:
                print(pat_dic['patient'].id)
            
        print("not mandatory patients in the hosp")
        print("")
        if not_mandatory_patients_in_the_hosp:
            for pat_dic in not_mandatory_patients_in_the_hosp:
                print(pat_dic['patient'].id)

        print("mandatory patients in the hosp")
        print("")
        if mandatory_in_the_hosp:
            for pat_dic in mandatory_in_the_hosp:
                print(pat_dic['patient'].id)

        print("not_mandatory_patients_not_in_the_hosp")
        print("")
        if not_mandatory_patients_not_in_the_hosp:
            for pat_dic in not_mandatory_patients_not_in_the_hosp:
                print(pat_dic['patient'].id)
        '''
    
        surgeons_workload = [[0 for t in range(T)] for surgeon in surgeons]
        theaters_workload = [[0 for t in range(T)] for theater_id in theaters.theaters_id]

        for patient_schedule in current_destroyed_point.patient_schedule:   # add the workload
            surgeon_id = patient_schedule['patient'].surgeon_id
            day = patient_schedule['day']
            if day is not None:
                for theater_schedule in current_destroyed_point.surgeons_operations:
                    if theater_schedule['patient'].id == patient_schedule['patient'].id:
                        theater_id = theater_schedule['theater']
                        break
                surgeons_workload[surgeon_id][day] += patient_schedule['patient'].surgery_duration
                theaters_workload[theater_id][day] += patient_schedule['patient'].surgery_duration        
            
        # now we MUST find a place in the solution for all the destroyed_mandatory patient 

        #print("################## POINT DESTROYED ####################")

        #visual_schedule(current_destroyed_point, occupants, rooms, T) # =^.^= gattino

        for patient_dic in destroyed_mandatory:
            patient = patient_dic['patient']
            found_solution = False

            while not found_solution:

                found_solution = place_patient(current_destroyed_point, patient, theaters_workload, surgeons_workload, rooms, theaters, surgeons, T)

                if not found_solution: 
                    # if we have not found a solution we try to kick off a not mandatory patient
                    not_mandatory_patients_in_the_hosp.sort(key=lambda x: abs(x['day']-patient_dic['patient'].surgery_release_day)+abs(x['day']+x['length']-patient.surgery_release_day-patient.length_of_stay)) # find the closest one to the patient
                    for not_mandatory_patient_in_the_hosp in not_mandatory_patients_in_the_hosp:
                        if not_mandatory_patient_in_the_hosp['patient'].gender == patient.gender:  # if they have the same gender
                            not_mandatory_to_delete = not_mandatory_patient_in_the_hosp
                            break
                    not_mandatory_patients_in_the_hosp.remove(not_mandatory_to_delete)
                    patient_to_delete = not_mandatory_to_delete['patient']
                    print("delete", patient_to_delete.id)
                    for schedule in current_destroyed_point.patient_schedule:
                        if schedule['patient'].id == patient_to_delete.id:
                            day = schedule['day']
                            old_room = schedule['room']
                            surgeons_workload[patient_to_delete.surgeon_id][day] -= patient_to_delete.surgery_duration
                            current_destroyed_point.patient_schedule[patient_to_delete.id] = {'patient': patient_to_delete,
                                                                                            'room': None,
                                                                                            'day': None}
                        for theater_dic in current_destroyed_point.surgeons_operations:
                            if theater_dic['patient'].id == patient_to_delete.id:
                                theaters_workload[theater_dic['theater']][day] -= patient_to_delete.surgery_duration
                                current_destroyed_point.surgeons_operations[patient_to_delete.id] = {'patient': patient_to_delete,
                                                                                                'theater': None}
                                break

                    rooms.remove_patient(old_room, patient_to_delete, not_mandatory_patient_in_the_hosp['day'], T)
 
                    not_mandatory_patients_not_in_the_hosp.append({'patient': patient_to_delete,
                                                                   'delay': T-patient_to_delete.surgery_release_day})

        for patient_dic in not_mandatory_patients_not_in_the_hosp:   # also for not mandatory patients
            patient = patient_dic['patient']
            found_solution = place_patient(current_destroyed_point, patient, theaters_workload, surgeons_workload, rooms, theaters, surgeons, T)
            if not found_solution:
                continue   # if a not mandatory patient has no place in the hospital, we don't care about him/her

        #visual_schedule(current_destroyed_point, occupants, rooms, T,True)# =^.^= gattino

        if CASE_REPAIR == 'A':

            for day in range(T):
                for shift in shifts:
                    nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                    random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                    counter = 0
                    for room_id in rooms.rooms_id:
                        if not current_destroyed_point.nurses_schedule[day][shift][room_id]:  # if the list is empty
                            # we have to find a nurse that can work in that room
                            nurse = nurse_that_can_work[counter % len(nurse_that_can_work)]
                            counter += 1
                            current_destroyed_point.nurses_schedule[day][shift][room_id].append({'nurse': nurse,
                                                                                                'room': room_id})

        if CASE_REPAIR == 'B':
            
            for day in range(T):
                for shift in shifts:
                    nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                    random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                    nurses_still_working = []
                    for room_id in rooms.rooms_id:
                        if not current_destroyed_point.nurses_schedule[day][shift][room_id]:  # if the list is empty
                            
                            # i want to find the best nurse for that particular room, looking at the skill level

                            # find the maximum skill level of the room

                            tot_skill_for_patients = []
                            for patient_dic in current_destroyed_point.patient_schedule:
                                if patient_dic['room'] == room_id and day >= patient_dic['day'] and day < patient_dic['day']+patient_dic['patient'].length_of_stay:
                                    tot_skill_for_patients.append(patient_dic['patient'].skill_level_required[day-patient_dic['day']][shift])

                            tot_skill_for_occupants = [occupant.skill_level_required[day][shift] for occupant in occupants
                                                      if occupant.room_id == room_id and day < occupant.length_of_stay]

                            max_skill = max(list(set(tot_skill_for_patients+tot_skill_for_occupants))) if tot_skill_for_patients or tot_skill_for_occupants else 0

                            nurses_skill_dic = []
                            for nurse in list(set(nurse_that_can_work)-set(nurses_still_working)):    # because i want to find a nurse that is not still working
                                if nurse.skill_level >= max_skill: 
                                    nurses_skill_dic.append({'nurse':nurse, 
                                                             'delay': nurse.skill_level-max_skill})
                            if not nurses_skill_dic:
                                for nurse in nurse_that_can_work:    # if I dont find a free nurse, I'll take another one from the one still working
                                    nurses_skill_dic.append({'nurse':nurse, 
                                                            'delay': nurse.skill_level-max_skill})

                            nurses_skill_dic.sort(key=lambda x: -x['delay']) # -delay because i want the best one
                            best_nurse = nurses_skill_dic[0]['nurse']

                            current_destroyed_point.nurses_schedule[day][shift][room_id].append({'nurse': best_nurse,
                                                                                                 'room': room_id})
                            nurses_still_working.append(best_nurse)

        if CASE_REPAIR == 'C':

            for day in range(T):
                for shift in shifts:
                    nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                    random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                    nurses_still_working = []
                    for room_id in rooms.rooms_id:
                        if not current_destroyed_point.nurses_schedule[day][shift][room_id]:  # if the list is empty

                            # i want to find the best nurse for that particular room, looking at the workload

                            # first of all find the workload for that room

                            room_workload = 0
                            for patient_schedule in current_destroyed_point.patient_schedule: # for patients
                                if patient_schedule['room'] == room_id and day >=patient_schedule['day'] and day < patient_schedule['day']+patient_schedule['patient'].length_of_stay:
                                    room_workload += patient_schedule['patient'].workload_produced[day-patient_schedule['day']][shift]
                            
                            for occupant in occupants: # for occupants
                                if occupant.room_id == room_id and day < occupant.length_of_stay:
                                    room_workload += occupant.workload_produced[day][shift]

                            nurse_workload_dic = [] 
                            for nurse in list(set(nurse_that_can_work)-set(nurses_still_working)):
                                if nurse.possible_turns[day][shift] >= room_workload:
                                    nurse_workload_dic.append({'nurse':nurse, 
                                                               'delay': nurse.possible_turns[day][shift]-room_workload})
                            if not nurse_workload_dic:
                                for nurse in nurse_that_can_work:
                                    nurse_workload_dic.append({'nurse':nurse, 
                                                                'delay': nurse.possible_turns[day][shift]-room_workload})

                            nurse_workload_dic.sort(key=lambda x: -x['delay']) # -delay because i want the best one
                            best_nurse = nurse_workload_dic[0]['nurse']

                            current_destroyed_point.nurses_schedule[day][shift][room_id].append({'nurse': best_nurse,
                                                                                                    'room': room_id})

        if CASE_REPAIR == 'D':
            
            for day in range(T):
                for shift in shifts:
                    nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                    random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                    nurses_still_working = []
                    for room_id in rooms.rooms_id:
                        if not current_destroyed_point.nurses_schedule[day][shift][room_id]:  # if the list is empty
                            
                            # i want to find the best nurse for that particular room, looking at the skill level and the workload

                            # find the maximum skill level of the room

                            tot_skill_for_patients = []
                            for patient_dic in current_destroyed_point.patient_schedule:
                                if patient_dic['room'] == room_id and day >= patient_dic['day'] and day < patient_dic['day']+patient_dic['patient'].length_of_stay:
                                    tot_skill_for_patients.append(patient_dic['patient'].skill_level_required[day-patient_dic['day']][shift])

                            tot_skill_for_occupants = [occupant.skill_level_required[day][shift] for occupant in occupants
                                                      if occupant.room_id == room_id and day < occupant.length_of_stay]

                            max_skill = max(list(set(tot_skill_for_patients+tot_skill_for_occupants))) if tot_skill_for_patients or tot_skill_for_occupants else 0

                            # find the workload of a room

                            room_workload = 0
                            for patient_schedule in current_destroyed_point.patient_schedule: # for patients
                                if patient_schedule['room'] == room_id and day >=patient_schedule['day'] and day < patient_schedule['day']+patient_schedule['patient'].length_of_stay:
                                    room_workload += patient_schedule['patient'].workload_produced[day-patient_schedule['day']][shift]
                            
                            for occupant in occupants: # for occupants
                                if occupant.room_id == room_id and day < occupant.length_of_stay:
                                    room_workload += occupant.workload_produced[day][shift]

                            nurses_skill_dic = []
                            for nurse in list(set(nurse_that_can_work)-set(nurses_still_working)):    # because i want to find a nurse that is not still working
                                if nurse.skill_level >= max_skill and nurse.possible_turns[day][shift] >= room_workload: 
                                    nurses_skill_dic.append({'nurse':nurse, 
                                                             'delay': abs(nurse.skill_level-max_skill) + abs(nurse.possible_turns[day][shift]-room_workload)})
                            if not nurses_skill_dic:
                                for nurse in nurse_that_can_work:    # if I dont find a free nurse, I'll take another one from the one still working
                                    nurses_skill_dic.append({'nurse':nurse, 
                                                            'delay': abs(nurse.skill_level-max_skill) + abs(nurse.possible_turns[day][shift]-room_workload)})

                            nurses_skill_dic.sort(key=lambda x: -x['delay']) # -delay because i want the best one
                            best_nurse = nurses_skill_dic[0]['nurse']

                            current_destroyed_point.nurses_schedule[day][shift][room_id].append({'nurse': best_nurse,
                                                                                                 'room': room_id})
                            nurses_still_working.append(best_nurse)

    
    return current_destroyed_point



                    
