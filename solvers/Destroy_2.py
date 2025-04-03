import random
import copy

def destroy_2(CASE_DESTROY, point, problem):  #main function for the destroy phase

    #nurses = problem.nurses
    #surgeons = problem.surgeons
    patients = problem.patients
    #occupants = problem.occupants
    rooms = problem.rooms
    #theaters = problem.theaters
    Tempo = problem.T
    shifts = problem.shifts

    tot_room_id = rooms.rooms_id

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

    return current_point