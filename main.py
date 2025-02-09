import numpy as np
from instances.hospital import Hospital
from instances.patient import Patient
from instances.occupant import Occupant
from instances.surgeon import Surgeon
from instances.nurse import Nurse
from solvers import *
import json 
import random

random.seed(min(341965, 343316, 284817))

######### part to eliminate

#n_rooms = 10
#hospital = Hospital(n_rooms)
#print(hospital.occupation)

#hospital.add_patient(3)
#hospital.add_patient(3)

#print(hospital.occupation)
#hospital.remove_patient(3)
#print(hospital.occupation)

#with open("./settings/solver_setting.json") as f:
#    solver_setting = json.load(
#        f
 #   )
#ga = Ga_Solver(solver_setting)
#ga.solve()



######### part to keep


def main():

    ############################ PREPROCESSING ########################################

    # reading the json file from the test set

    # we'll start easy by reading the first one

    #  reading

    filename = 'test01.json'

    with open('test_data/'+filename, 'r') as file:
        data = json.load(file)

    # creating the data structures

    total_days= data['days']
    total_shifts = data['shift_types']
    skill_levels = data['skill_levels']
    age_groups = data['age_groups']

    age_to_number = {age: i + 1 for i, age in enumerate(age_groups)}   # dic
    list_age = [age_to_number[age] for age in age_groups]    # list

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

    # saving the weights

    weights = data['weights']


    rooms_id = [room_data['id'] for room_data in rooms_data]    
    occupants_id = [occupant_data['id'] for occupant_data in occupants_data]
    patients_id = [patient_data['id'] for patient_data in patients_data]
    surgeons_id = [surgeon_data['id'] for surgeon_data in surgeons_data]
    nurses_id = [nurse_data['id'] for nurse_data in nurses_data]
    theaters_id = [theater_data['id'] for theater_data in operating_theaters_data]

    # modifying the id to be a list of integers

    rooms_mapping = {room["id"]: i for i, room in enumerate(rooms_data)}   # map of the id

    for i,room_data in enumerate(rooms_data):
         room_data['id'] = rooms_mapping[room_data['id']]   # modifying the id 
    
    for i,occupant_data in enumerate(occupants_data):
        occupant_data['id'] = i
        occupant_data['room_id'] = rooms_mapping[occupant_data['room_id']]   # modifying the id

    for i,patient_data in enumerate(patients_data):
        patient_data['id'] = i

    # modifying the gender using 0 and 1

    for occupant_data in occupants_data:
        if occupant_data['gender'] == 'A':
            occupant_data['gender'] = 0
        else:
            occupant_data['gender'] = 1

        occupant_data['age_group'] = age_to_number.get(occupant_data['age_group'])
    

    for patient_data in patients_data:
        if patient_data['gender'] == 'A':
            patient_data['gender'] = 0
        else:
            patient_data['gender'] = 1

        if patient_data['mandatory'] == False:
            patient_data['mandatory'] = 0
        else:
            patient_data['mandatory'] = 1

        patient_data['age_group'] = age_to_number.get(patient_data['age_group'])


    for patient_data in patients_data:
        patient_data['compatible_rooms_ids'] = [room_id for room_id in rooms_id if room_id not in patient_data['incompatible_room_ids']]




    ############################ CLASSES ########################################

    # creating the hospital

    Hosp = Hospital(rooms_data, operating_theaters_data, total_days)

    # creating the patients

    patients = [Patient(patient_data) for patient_data in patients_data]

    # creating the occupants 

    occupants = [Occupant(occupant_data) for occupant_data in occupants_data]

    # creating the surgeons

    surgeons = [Surgeon(surgeon_data) for surgeon_data in surgeons_data]

    # creating the nurses

    nurses = [Nurse(nurse_data) for nurse_data in nurses_data]

    # adding the occupants to the hospital

    for occupant in occupants:
        Hosp.add_occupant(occupant)

    print(Hosp.rooms_people_inside)

    


if __name__ == "__main__":
    main()
