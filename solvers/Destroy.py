import random

def destroy(CASE_DESTROY ,current_point, problem):  #main function for the destroy phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    Tempo = problem.T
    shifts = problem.shifts

    tot_room_id = rooms.rooms_id

    # we have different CASE of destroyers

    if CASE_DESTROY == 'A':

        # in this case we select one room, one day and one shift randomly and we keep the nurses working on that room, day and shift, we give away the other
        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        for day in Tempo:
            for shift in shifts:
                for room_id in rooms.rooms_id:
                    if day != random_day and shift != random_shift and room_id != random_room:    # we change all the other schedule
                        current_point.nurses_schedule[day][shift][room_id] = []    # empty list


    if CASE_DESTROY == 'B':

        # in this case we select one room, one day and one shift randomly and we kick off the nurse that is working on that room, day and shift
        
        random_room = random.choice(tot_room_id)    # select a random room
        random_shift = random.choice(shifts)
        random_day = random.choice(range(Tempo))

        current_point.nurses_schedule[random_day][random_shift][random_room] = []


    if CASE_DESTROY == 'C':
        
        # in this case we select randomly a list of rooms, some days and some shift, and we do like in B but with more combination

        n_random_rooms = random.choice(range(rooms.n_rooms))    # the number of random rooms to select
        




    return current_point

