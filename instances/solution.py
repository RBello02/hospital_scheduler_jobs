import math 
import numpy as np


# in this class we are going to store the current solution of the problem, this class represents the variables of the problem

class Solution():

    def __init__(self, Tempo, occupants, patients, surgeons, nurses):

        # matrix patient x room x arriving time

        T = Tempo.T

        self.patient_schedule = [{'patient': patient,
                                  'room': None,
                                  'day': None} for patient in patients]


        # matrix surgeons x patients x theater

        self.surgeons_operations = [[{'surgeon': surgeon,
                                     'theater': None,
                                     'patient': None} for surgeon in surgeons] for patient in patients]


        # for the nurses we are going to create two variables, one for the occupants and the other for the patients 

        # matrix nurses x occupants x rooms  x shift x time

        shifts = Tempo.shifts

        self.nurses_schedule_occupant = [[[[{'nurse': nurse,
                                          'occupant': None,
                                          'shift': None,
                                          'day': None} for nurse in nurses] for occupant in occupants] for shift in shifts] for day in range(T)]
        
        self.nurses_schedule_patient = [[[[{'nurse': nurse,
                                          'patient': None,
                                          'shift': None,
                                          'day': None} for nurse in nurses] for patient in patients] for shift in shifts] for day in range(T)]





