

def place_patient(solution, patient, theaters_workload, surgeons_workload, rooms, theaters, surgeons, T):
      


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

    if patient.mandatory == 0:
        end = T
    else:
        end = patient.surgery_due_day

    for admission_day in range(patient.surgery_release_day, end):   # selecting the admission date

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
                    solution.patient_schedule[patient.id] = {'patient': patient,
                                                         'room': room_id,    
                                                         'day': admission_day}
                    solution.surgeons_operations[patient.id]  = {'theater': theater_id,
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
      
    return found_solution