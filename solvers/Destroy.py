def destroy(self, CASE ,current_point, problem):  #main function for the destroy phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    Tempo = problem.T
    shifts = problem.shifts

    print (current_point)

    # we have different CASE of destroyers

    if CASE == 'A':

        # in this case we select one room, one day and one shift randomly and we keep the nurses working on that room, day and shift

        pass
