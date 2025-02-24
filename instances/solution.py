import math 
import numpy as np


# in this class we are going to store the current solution of the problem, this class represents the variables of the problem

class Solution():

    def __init__(self, Tempo, rooms, patients, surgeons, nurses):

        # matrix patient x room x arriving time

        T = Tempo.T

        self.patient_schedule = [{'patient': patient,
                                  'room': None,
                                  'day': None} for patient in patients]


        # matrix surgeons x patients x theater

        self.surgeons_operations = [[{'surgeon': surgeon,
                                     'theater': None,
                                     'patient': None} for surgeon in surgeons] for patient in patients]


        # each nurse can work on a room in a shift in a particular day, notice that a during a particular day and a particular shift the nurse can stay in different rooms

        # matrix nurses x  rooms  x shift x time

        shifts = Tempo.shifts    

        self.nurses_schedule = [[[[] for _ in rooms.rooms_id] for _ in shifts] for _ in range(T)]        
        for nurse in nurses:
            for day in range(T):
                for shift in shifts:
                    if nurse.possible_turns[day][shift] != 0:     # check if it is a working day/shift for the nurse
                        for room_id in rooms.rooms_id:
                            self.nurses_schedule[day][shift][room_id].append({'nurse': nurse,
                                                                               'room': None})
                                                                    
                                                   


