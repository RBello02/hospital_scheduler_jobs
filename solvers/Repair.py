import random


def repair(CASE_REPAIR , current_destroyed_point,  problem): #main function for the repair phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    T = problem.T
    shifts = problem.shifts

    point = current_destroyed_point

    if CASE_REPAIR == 'A':

        # in this case the repair we sort the patient by the delay


        # select all the mandatory patient that have been destroyed 

        mandatory_patients = []
        not_mandatory_patients = []   # this is the list of all the destroyed patient 
        for patient_dic in point.patient_schedule:
            patient = patient_dic['patient']
            if patient.mandatory == 0:
                not_mandatory_patients.append({'patient': patient,
                                               'delay': T-patient.surgery_release_day})
            else:
                if patient_dic['day'] is None: #if it is a destroyed patient
                    mandatory_patients.append({'patient': patient,
                                               'delay': patient.surgery_due_day - patient.surgery_release_day})
                    
        # sort by the delay:

        mandatory_patients.sort(key=lambda x: x['delay']) # sort over delay
        not_mandatory_patients.sort(key=lambda x: x['delay'])

        # now we have to add this patient to the solution again (similar to initial solution)

        # create a variable that stores the surgeons + the time that they invest during a day for an operation

        surgeons_workload = [[0 for t in range(T)] for surgeon in surgeons]

        # create a variable that stores the theaters + the time of the operation of the patient 

        theaters_workload = [[0 for t in range(T)] for theater_id in theaters.theaters_id]

        # in this case (not like initial solution) we have to init theaters_workload and surgeons_workload

        for patient_dic in point.patient_schedule:
            if patient_dic['day'] is not None: # if it is not destroyed:
                patient = patient_dic['patient']
                admission = patient_dic['day']
                surgeon_id = patient.surgeon_id # surgeon id 
                for theater_dic in point.surgeons_operations: # find the theater
                    if theater_dic['patient'].id == patient.id:
                        theater_id = theater_dic['theater']
                surgeons_workload[surgeon_id][admission] += patient.surgery_duration
                theaters_workload[theater_id][admission] += patient.surgery_duration
            

        
        for patient_dic in mandatory_patients:
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
                            point.patient_schedule[patient.id] = {'patient': patient,
                                                                'room': room_id,    
                                                                'day': admission_day}
                            point.surgeons_operations[patient.id]  = {'theater': theater_id,
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
                print("There is no solution for the patient: ", patient.id)



        for patient_dic in not_mandatory_patients:   # also for not mandatory patients
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
                            point.patient_schedule[patient.id] = {'patient': patient,
                                                                'room': room_id,    
                                                                'day': admission_day}
                            point.surgeons_operations[patient.id]  = {'theater': theater_id,
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

        
        # now we have to select the nurses that are not scheduled, they might be nurses that are destroyed

        for day in range(T):
            for shift in shifts:
                nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                counter = 0
                for room_id in rooms.rooms_id:
                    if not point.nurses_schedule[day][shift][room_id]:  # if the list is empty
                        # we have to find a nurse that can work in that room
                        nurse = nurse_that_can_work[counter % len(nurse_that_can_work)]
                        counter += 1
                        point.nurses_schedule[day][shift][room_id].append({'nurse': nurse,
                                                                       'room': room_id})

    




    return point



                    
