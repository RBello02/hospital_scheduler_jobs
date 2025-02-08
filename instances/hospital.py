import math

class Hospital():

    def __init__(self, rooms, theaters, T):
        # For the time
        self.T = T   

        # For rooms
        self.rooms_id = [i for i, room in enumerate(rooms)]  # Save the id of the room as a number
        self.n_rooms = len(rooms)
        self.rooms_capacity = [room['capacity'] for room in rooms]  # Maps the capacity of a single room
        self.rooms_people_inside = [[0 for _ in range(len(rooms))] for t in range(T)]  # Tracks people inside a room for each day
        self.rooms_gender = [[None for _ in range(len(rooms))] for t in range(T)]  # Gender in rooms for each day

        # For theaters
        self.theaters_id = [i for i, theater in enumerate(theaters)]  # Save the id of the theater as a number
        self.n_theaters = len(theaters)
        self.theaters_capacity = [[theater['availability'] for theater in theaters] for t in range(T)]  # Tracks the capacity of a single theater

        # Add occupation tracking
        self.occupation = [0] * self.n_rooms  # Keeps track of the current number of patients in each room

    def add_patient(self, idx_room, start_day, duration, gender):
        for t in range(start_day, start_day + duration):
            self.rooms_people_inside[t][idx_room] += 1
        self.occupation[idx_room] += 1

    def remove_patient(self, idx_room):
        self.occupation[idx_room] -= 1

    def fitness(self):
        return abs(sum(self.occupation) - 2 * self.n_rooms)
