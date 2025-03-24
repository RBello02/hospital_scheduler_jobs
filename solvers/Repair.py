
def repair(CASE_REPAIR , current_destroyed_point,  problem): #main function for the repair phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    Tempo = problem.T
    shifts = problem.shifts

    mandatory_patients = [patient for patient in patients if patient.mandatory == 1]
    not_mandatory_patients = [patient for patient in patients if patient.mandatory == 0]


    if CASE_REPAIR == 'A':

        point = current_destroyed_point

        while not problem.constraints(point, patients, surgeons, rooms, theaters, Tempo, shifts):   # until we dont find a point that is ok

            pass

            
