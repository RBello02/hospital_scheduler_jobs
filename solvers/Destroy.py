import random
import copy

def destroy(CASE_DESTROY, point, problem):  #main function for the destroy phase

    #nurses = problem.nurses
    #surgeons = problem.surgeons
    patients = problem.patients
    #occupants = problem.occupants
    old_rooms = problem.rooms
    #theaters = problem.theaters
    Tempo = problem.T
    shifts = problem.shifts

    tot_room_id = old_rooms.rooms_id

    rooms = copy.deepcopy(old_rooms)    # we need to copy the rooms because we need to modify the schedule of the rooms

    current_point = copy.deepcopy(point)

    # we have different CASE of destroyers

    if CASE_DESTROY == 'A':

        # in this case we select one room, one day and one shift randomly and we keep the nurses working on that room, day and shift, we give away the other
        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day != random_day and shift != random_shift and room_id != random_room:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list


    if CASE_DESTROY == 'B':

        # in this case we select one room, one day and one shift randomly and we kick off the nurse that is working on that room, day and shift
        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        #print(random_room)
        #print(random_day)
        #print(random_shift)

        current_point.nurses_schedule[random_day][random_shift][random_room] = []


    if CASE_DESTROY == 'C':
        
        # in this case we select randomly a list of rooms, some days and some shift, and we do like in B but with more combination

        n_random_rooms = random.choice(range(1,rooms.n_rooms-1))    # the number of random rooms to select
        random_rooms = random.sample(tot_room_id, n_random_rooms)   # sample the rooms

        n_random_shifts = random.choice(range(1,len(shifts)-1))
        random_shifts = random.sample(shifts, n_random_shifts)

        n_random_days = random.choice(range(1,Tempo-1))
        random_days = random.sample(range(Tempo), n_random_days)

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day in random_days and shift in random_shifts and room_id in random_rooms:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list

    if CASE_DESTROY == 'D':

        # in this case we select one patient randomly and kick off all the other from the hospital

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        #print(random_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id != random_patient_id:
                #print(patient_dic['patient'].id)
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'],  patient_dic['patient'], patient_dic['day'], Tempo)
                        
    if CASE_DESTROY == 'E':

        # the same thing we did above but we kick off that random patient

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        #start = current_point.patient_schedule[random_patient_id]['day']
        #end = min(current_point.patient_schedule[random_patient_id]['day']+current_point.patient_schedule[random_patient_id]['patient'].length_of_stay, Tempo)
        #room_index = current_point.patient_schedule[random_patient_id]['room']

        #for t in range(start, end):
        #    print("rooms before", rooms.rooms_count_people[t][room_index])


        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id == random_patient_id:
                #print(random_patient_id)
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)

        #for t in range(start, end):
        #    print("rooms after", rooms.rooms_count_people[t][room_index])

                        
                        
    if CASE_DESTROY == 'F':

        # we select n random number of patients and we kick off n random patients

        all_patient_id = [patient.id for patient in patients]
        n_random_patients = random.choice(range(1,len(all_patient_id)-1))
        random_patients_id = random.sample(all_patient_id, n_random_patients)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id in random_patients_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
                        
    if CASE_DESTROY == 'G':

        # mix of case A and D
        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day != random_day and shift != random_shift and room_id != random_room:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id != random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)

                        
    if CASE_DESTROY == 'H':

        # mix of A and E
                        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day != random_day and shift != random_shift and room_id != random_room:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id == random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
    
    if CASE_DESTROY == 'I':

        # mix of A and F

        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day != random_day and shift != random_shift and room_id != random_room:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list

        all_patient_id = [patient.id for patient in patients]
        n_random_patients = random.choice(range(1,len(all_patient_id)-1))
        random_patients_id = random.sample(all_patient_id, n_random_patients)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id in random_patients_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
                        
    if CASE_DESTROY == 'L':

        # mix of B and D

        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        current_point.nurses_schedule[random_day][random_shift][random_room] = []

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id != random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
    if CASE_DESTROY == 'M':

        # mix of B and E

        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        current_point.nurses_schedule[random_day][random_shift][random_room] = []

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id == random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
                        
    if CASE_DESTROY == 'N':
        
        # mix of B and F

        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        current_point.nurses_schedule[random_day][random_shift][random_room] = []

        all_patient_id = [patient.id for patient in patients]
        n_random_patients = random.choice(range(1,len(all_patient_id)-1))
        random_patients_id = random.sample(all_patient_id, n_random_patients)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id in random_patients_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
    
    if CASE_DESTROY == 'O':

        # mix of C and D

        n_random_rooms = random.choice(range(1,rooms.n_rooms-1))    # the number of random rooms to select
        random_rooms = random.sample(tot_room_id, n_random_rooms)   # sample the rooms

        n_random_shifts = random.choice(range(1,len(shifts)-1))
        random_shifts = random.sample(shifts, n_random_shifts)

        n_random_days = random.choice(range(1,Tempo-1))
        random_days = random.sample(range(Tempo), n_random_days)

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day in random_days and shift in random_shifts and room_id in random_rooms:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list
        
        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id != random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                             'room': None,
                                                                              'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                        
                        
    if CASE_DESTROY == 'P':

        # mix of C and E

        n_random_rooms = random.choice(range(1,rooms.n_rooms-1))    # the number of random rooms to select
        random_rooms = random.sample(tot_room_id, n_random_rooms)   # sample the rooms

        n_random_shifts = random.choice(range(1,len(shifts)-1))
        random_shifts = random.sample(shifts, n_random_shifts)

        n_random_days = random.choice(range(1,Tempo-1))
        random_days = random.sample(range(Tempo), n_random_days)

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day in random_days and shift in random_shifts and room_id in random_rooms:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list

        all_patient_id = [patient.id for patient in patients]
        random_patient_id = random.choice(all_patient_id)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id == random_patient_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                            'room': None,
                                                                            'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                    
                        
    if CASE_DESTROY == 'Q':

        # mix of C and F

        n_random_rooms = random.choice(range(1,rooms.n_rooms-1))    # the number of random rooms to select
        random_rooms = random.sample(tot_room_id, n_random_rooms)   # sample the rooms

        n_random_shifts = random.choice(range(1,len(shifts)-1))
        random_shifts = random.sample(shifts, n_random_shifts)

        n_random_days = random.choice(range(1,Tempo-1))
        random_days = random.sample(range(Tempo), n_random_days)

        for day in range(Tempo):
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day in random_days and shift in random_shifts and room_id in random_rooms:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list          
                        
        all_patient_id = [patient.id for patient in patients]
        n_random_patients = random.choice(range(1,len(all_patient_id)-1))
        random_patients_id = random.sample(all_patient_id, n_random_patients)

        for patient_dic in current_point.patient_schedule:
            if patient_dic['patient'].id in random_patients_id:
                current_point.patient_schedule[patient_dic['patient'].id] = {'patient': patient_dic['patient'],
                                                                            'room': None,
                                                                            'day': None}     # kick off from the hospital
                for theater_dic in current_point.surgeons_operations:
                    if theater_dic['patient'].id == patient_dic['patient'].id:   # do not operate that patient
                        current_point.surgeons_operations[patient_dic['patient'].id] = {'theater': None,
                                                                                        'patient': patient_dic['patient']}
                # remove the patient from the hospital:
                if patient_dic['day'] is not None:
                    rooms.remove_patient(patient_dic['room'], patient_dic['patient'], patient_dic['day'], Tempo)
                    
                                                        

    return current_point,rooms

