import random
import copy


def repair_2(CASE_REPAIR, current_point, current_destroyed_point_not_copied,  problem): #main function for the repair phase

    nurses = problem.nurses
    surgeons = problem.surgeons
    patients = problem.patients
    occupants = problem.occupants
    rooms = problem.rooms
    theaters = problem.theaters
    T = problem.T
    shifts = problem.shifts

    current_destroyed_point= copy.deepcopy(current_destroyed_point_not_copied)

    if CASE_REPAIR == 'A':

        # we have to find the patients that have been destroyed:

        for day in range(T):
            for shift in shifts:
                nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
                random.shuffle(nurse_that_can_work)  # shuffle it to make it spicy
                counter = 0
                for room_id in rooms.rooms_id:
                    if not current_destroyed_point.nurses_schedule[day][shift][room_id]:  # if the list is empty
                        # we have to find a nurse that can work in that room
                        nurse = nurse_that_can_work[counter % len(nurse_that_can_work)]
                        counter += 1
                        current_destroyed_point.nurses_schedule[day][shift][room_id].append({'nurse': nurse,
                                                                                             'room': room_id})

    
    return current_destroyed_point



                    
