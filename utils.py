
def preprocess (data, rooms_mapping, patients_mapping, occupants_mapping ,surgeons_mapping, nurses_mapping, theaters_mapping ):
    
    total_days= data['days']
    total_shifts = data['shift_types']
    #skill_levels = data['skill_levels']
    age_groups = data['age_groups']

    age_to_number = {age: i + 1 for i, age in enumerate(age_groups)}   # dic

    shift_to_number = {shift: i for i, shift in enumerate(total_shifts)} 

    shifts = [shift_to_number[shift] for shift in total_shifts]

     # create a dic for occupants

    occupants_data = data['occupants']

    # create a dic for patients

    patients_data = data['patients']

    # create a dic for surgeons

    surgeons_data = data['surgeons']

    # create a dic for operating theaters

    operating_theaters_data = data['operating_theaters']

    # create a dic for the nurses

    nurses_data = data['nurses']

    # create a dic for rooms

    rooms_data = data['rooms']

    rooms_id = [room_data['id'] for room_data in rooms_data]

    # modifying the id to be a list of integers

    for room_data in rooms_data:
         room_data['id'] = rooms_mapping[room_data['id']]   # modifying the id 
    

    for occupant_data in occupants_data:
        occupant_data['id'] = occupants_mapping[occupant_data['id']]   # change the id
        occupant_data['room_id'] = rooms_mapping[occupant_data['room_id']]   # change the id
        if occupant_data['gender'] == 'A':
            occupant_data['gender'] = 0
        else:
            occupant_data['gender'] = 1

        occupant_data['age_group'] = age_to_number.get(occupant_data['age_group'])

    for nurse_data in nurses_data:
        nurse_data['id'] = nurses_mapping[nurse_data['id']]

    for surgeon_data in surgeons_data:
        surgeon_data['id'] = surgeons_mapping[surgeon_data['id']]
    
    for theater_data in operating_theaters_data:
        theater_data['id'] = theaters_mapping[theater_data['id']]

    for patient_data in patients_data:
        patient_data['id'] = patients_mapping[patient_data['id']]   # change the id
        if patient_data['gender'] == 'A':
            patient_data['gender'] = 0
        else:
            patient_data['gender'] = 1

        if patient_data['mandatory'] == False:
            patient_data['mandatory'] = 0
        else:
            patient_data['mandatory'] = 1

        patient_data['age_group'] = age_to_number.get(patient_data['age_group'])

        patient_data['compatible_rooms_ids'] = [room_id for room_id in rooms_id if room_id not in patient_data['incompatible_room_ids']]
        patient_data['compatible_rooms_ids'] = [rooms_mapping[c_room] for c_room in patient_data['compatible_rooms_ids']]    # creating a feature with compatible rooms

        



    return {'T': total_days,'shifts': shifts ,'age_mapping': age_to_number,'shift_mapping': shift_to_number ,'occupants': occupants_data, 'patients':patients_data, 'surgeons': surgeons_data, 'nurses': nurses_data ,'rooms': rooms_data, 'theaters': operating_theaters_data, 'weights': data['weights'] }



def postprocess (solution, patients, surgeons, nurses, rooms, theaters, T, shifts, shift_mapping):

    # this function produces the json file for the validation of the solution

    # get the number of patients
    n_patients = len(patients)
    num_digits_for_patient = len(str(n_patients))

    # get the number of theaters
    n_theaters = theaters.n_theaters
    num_digits_for_theater = len(str(n_theaters))

    # get the number of rooms
    n_rooms = rooms.n_rooms
    num_digits_for_room = len(str(n_rooms))

    # starting from the patients
    patients_solution = []

    for patient in patients:
        patient_dic = solution.patient_schedule[patient.id]
        if patient_dic['day'] is None:          # it means that the patient is not in the hospital
            patients_solution.append({"id": f"p{patient.id:0{num_digits_for_patient}d}",
                                      "admission_day": "none"})
        else:
            # get the operating theater where the patient is
            operating = solution.surgeons_operations[patient.id]
            for surgeon in surgeons:
                if operating[surgeon.id]['patient'] == patient and operating[surgeon.id]['theater'] is not None:
                    theater_id = operating[surgeon.id]['theater']   # found the theater
                    break
            
            patients_solution.append({"id": f"p{patient.id:0{num_digits_for_patient}d}",
                                      "admission_day": patient_dic['day'],
                                      "room": f"r{patient_dic['room']:0{num_digits_for_room}d}",
                                      "operating_theater": f"t{theater_id:0{num_digits_for_theater}d}"})
            
    
    # now we go for the nurses

    # get the number of nurses
    n_nurses = len(nurses)
    num_digits_for_nurse = len(str(n_nurses))

    nurses_solution = []

    for nurse in nurses:
        nurse_assignment= []
        for day in range(T):
            for shift in shifts:
                if nurse.possible_turns[day][shift] > 0:   # check if the nurse can work on that day
                    rooms_set = set()   # is the set of the rooms where the nurse is working
                    for room_id in rooms.rooms_id:
                        nurse_list = solution.nurses_schedule[day][shift][room_id]   # get the nurses that work in that particular room
                        for nurse_dic in nurse_list:
                            if nurse_dic['nurse'] == nurse:
                                rooms_set.add(f"r{room_id:0{num_digits_for_room}d}")
                    
                    rooms_list = list(rooms_set) # rooms_set becomes a list
                    rooms_list.sort()
                    nurse_assignment.append({"day": day, "shift": next((k for k, v in shift_mapping.items() if v == shift), None), "rooms": rooms_list})
        nurses_solution.append({"id": f"n{nurse.id:0{num_digits_for_nurse}d}", "assignment": nurse_assignment})
                            

    # return the json file

    return {"patients": patients_solution, "nurses": nurses_solution}




