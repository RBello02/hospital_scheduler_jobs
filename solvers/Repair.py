import random
import copy


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

    if CASE_REPAIR == 'A':

        # we have to find the patients that have been destroyed:


        destroyed_mandatory = []
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
                #print(patient_dic['patient'].id)
                if patient_dic['patient'].mandatory == 1:
                    destroyed_mandatory.append({'patient': patient_dic['patient'],
                                                'delay': patient_dic['patient'].surgery_due_day-patient_dic['patient'].surgery_release_day})
                    #print(patient_dic['patient'].id)
                else:
                    not_mandatory_patients_not_in_the_hosp.append({'patient': patient_dic['patient'],
                                                    'delay': T-patient_dic['patient'].surgery_release_day})
                    
            if patient_dic['day'] is not None and destroyed_patient_dic['day'] is not None and patient_dic['patient'].mandatory == 0: 
                not_mandatory_patients_in_the_hosp.append({'patient': patient_dic['patient'],
                                                               'delay': T-patient_dic['patient'].surgery_release_day})
                
            
        #print(destroyed_mandatory)
        #print(current_destroyed_point.patient_schedule[19])

        
        #mandatory_patients.sort(key=lambda x: x['delay']) # sort over delay
        #not_mandatory_patients.sort(key=lambda x: x['delay'])
        destroyed_mandatory.sort(key=lambda x: x['delay'])
        #destroyed_not_mandatory.sort(key=lambda x: x['delay'])

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

        print("not_mandatory_patients_not_in_the_hosp")
        print("")
        if not_mandatory_patients_not_in_the_hosp:
            for pat_dic in not_mandatory_patients_not_in_the_hosp:
                print(pat_dic['patient'].id)

        # surgeons and theaters workload

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

        for patient_dic in destroyed_mandatory:
            patient = patient_dic['patient']
            surgeon_id = patient.surgeon_id
            for surgeon in surgeons:
                if surgeon.id == surgeon_id:
                    break                   # found the surgeon

            found_solution = False   # until we dont find a place for the patient we kick off not mandatory patients

            while not found_solution:
                compatible_room_ids = patient.compatible_room_ids

                for admission_day in range(patient.surgery_release_day, patient.surgery_due_day+1):   # selecting the admission date

                    there_is_surgeon = False
                    there_is_theater = False
                    
                    if surgeons_workload[surgeon_id][admission_day] + patient.surgery_duration <= surgeon.max_surgery_time[admission_day]:    # if a surgeon can operate in the admission date 
                        there_is_surgeon = True
                    
                    for theater_id in theaters.theaters_id:
                        if theaters_workload[theater_id][admission_day] + patient.surgery_duration <= theaters.theaters_capacity[theater_id][admission_day]: # if there is a theater in the admission date
                            there_is_theater = True
                            break
                    
                    if there_is_surgeon and there_is_theater:  # i do all the for only if there is a theater and a surgeon
                        for room_id in compatible_room_ids:
                            there_is_place = True
                            same_gender = True
                            for t in range(admission_day, min(admission_day+patient.length_of_stay, T)):    # I take the min, because the admis + length can go over T, and i don't want to know nothing after T
                                room_gender = rooms.rooms_gender[t][room_id] 
                                room_count_people = rooms.rooms_count_people[t][room_id]
                                if room_gender is not None and room_gender != patient.gender:    # room gender is None when a room is empty
                                    same_gender = False
                                if room_count_people >= rooms.rooms_capacity[room_id]:   # if there's no place during the schedule for a patient 
                                    there_is_place = False
                            if there_is_place and same_gender:        # if all the constraints are ok add the solution
                                current_destroyed_point.patient_schedule[patient.id] = {'patient': patient,
                                                                        'room': room_id,    
                                                                        'day': admission_day}
                                current_destroyed_point.surgeons_operations[patient.id]  = {'theater': theater_id,
                                                                            'patient': patient}
                                
                                # add the time to the surgeons and theaters

                                surgeons_workload[surgeon_id][admission_day] += patient.surgery_duration
                                theaters_workload[theater_id][admission_day] += patient.surgery_duration

                                found_solution = True
                                break   # close the for that is running over rooms_ids
                        if found_solution:
                            break # close the for that is running over the admission date
                # now we add the patient to the hospital
                if found_solution:
                    rooms.add_patient(room_id, patient, admission_day, T)
                else:  
                    # if we have not found a solution we try to kick off a not mandatory patient
                    not_mandatory_patients_in_the_hosp.sort(key=lambda x: abs(x['day']-patient_dic['patient'].surgery_release_day)) # find the closest one to the patient
                    not_mandatory_patient_in_the_hosp = not_mandatory_patients_in_the_hosp[0]  # I'll take the first one
                    not_mandatory_patients_in_the_hosp.remove(not_mandatory_patient_in_the_hosp)
                    patient_to_delete = not_mandatory_patient_in_the_hosp['patient']
                    #print(patient_to_delete.id)
                    for schedule in current_destroyed_point.patient_schedule:
                        if schedule['patient'].id == patient_to_delete.id:
                            old_room = schedule['room']
                            current_destroyed_point.patient_schedule[patient_to_delete.id] = {'patient': patient_to_delete,
                                                                                              'room': None,
                                                                                              'day': None}
                        for theater_dic in current_destroyed_point.surgeons_operations:
                            if theater_dic['patient'].id == patient_to_delete.id:
                                current_destroyed_point.surgeons_operations[patient_to_delete] = {'patient': patient_to_delete,
                                                                                                  'theater': None}
                                break
                    rooms.remove_patient(old_room, patient_to_delete, not_mandatory_patient_in_the_hosp['day'])
                    not_mandatory_patients_not_in_the_hosp.append({'patient'})

        for patient_dic in not_mandatory_patients_not_in_the_hosp:   # also for not mandatory patients
            patient = patient_dic['patient']
            surgeon_id = patient.surgeon_id
            for surgeon in surgeons:
                if surgeon.id == surgeon_id:
                    break                   # find the surgeon
        
            # we have to find a room for this patient,
            # the room must be
            # 1) compatible
            # 2) of the same sex of the patient
            # 3) the there must be capacity for all his stay in the hospital

            # also check that
            # 4) there must be a surgeon for the patient in their admission date 
            # 5) there must be a theater where the patient can be operated

            compatible_room_ids = patient.compatible_room_ids
            found_solution = False    

            for admission_day in range(patient.surgery_release_day, T):   # selecting the admission date

                there_is_surgeon = False
                there_is_theater = False

            
                if surgeons_workload[surgeon_id][admission_day] + patient.surgery_duration <= surgeon.max_surgery_time[admission_day]:    # if a surgeon can operate in the admission date 
                    there_is_surgeon = True
            
                for theater_id in theaters.theaters_id:
                    if theaters_workload[theater_id][admission_day] + patient.surgery_duration <= theaters.theaters_capacity[theater_id][admission_day]: # if there is a theater in the admission date
                        there_is_theater = True
                        break

                if there_is_surgeon and there_is_theater:  # i do all the for only if there is a theater and a surgeon
                    for room_id in compatible_room_ids:
                        there_is_place = True
                        same_gender = True
                        for t in range(admission_day, min(admission_day+patient.length_of_stay, T)):    # I take the min, because the admis + length can go over T, and i don't want to know nothing after T
                            room_gender = rooms.rooms_gender[t][room_id] 
                            room_count_people = rooms.rooms_count_people[t][room_id]
                            if room_gender is not None and room_gender != patient.gender:    # room gender is None when a room is empty
                                same_gender = False
                            if room_count_people >= rooms.rooms_capacity[room_id]:   # if there's no place during the schedule for a patient 
                                there_is_place = False
                        if there_is_place and same_gender:        # if all the constraints are ok add the solution
                            current_destroyed_point.patient_schedule[patient.id] = {'patient': patient,
                                                            'room': room_id,    
                                                            'day': admission_day}
                            current_destroyed_point.surgeons_operations[patient.id]  = {'theater': theater_id,
                                                                'patient': patient}
                    
                            # add the time to the surgeons and theaters

                            surgeons_workload[surgeon_id][admission_day] += patient.surgery_duration
                            theaters_workload[theater_id][admission_day] += patient.surgery_duration

                            found_solution = True
                            break   # close the for that is running over rooms_ids
                    if found_solution:
                        break # close the for that is running over the admission date
            # now we add the patient to the hospital
            if found_solution:
                rooms.add_patient(room_id, patient, admission_day, T)
            else:
                continue # if it doesn't fit amen
                    

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

    
    return current_destroyed_point



                    
