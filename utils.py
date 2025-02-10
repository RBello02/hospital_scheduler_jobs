
def preprocess (data, rooms_mapping, patients_mapping, occupants_mapping ,surgeons_mapping, nurses_mapping, theaters_mapping ):
    
    total_days= data['days']
    total_shifts = data['shift_types']
    #skill_levels = data['skill_levels']
    age_groups = data['age_groups']

    age_to_number = {age: i + 1 for i, age in enumerate(age_groups)}   # dic

    shift_to_number = {shift: i for i, shift in enumerate(total_shifts)} 

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



    return {'T': total_days, 'age_mapping': age_to_number,'shift_mapping': shift_to_number ,'occupants': occupants_data, 'patients':patients_data, 'surgeons': surgeons_data, 'nurses': nurses_data ,'rooms': rooms_data, 'theaters': operating_theaters_data }
