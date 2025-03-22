import math 
import numpy as np


class Patient :

    def __init__(self, patient_data, Tempo):
        self.id = patient_data['id']
        self.age_group = patient_data['age_group']
        self.gender = patient_data['gender']
        self.compatible_room_ids = patient_data['compatible_rooms_ids']
        self.length_of_stay = patient_data['length_of_stay']
        self.mandatory = patient_data['mandatory']
        self.surgeon_id = patient_data['surgeon_id']
        self.surgery_duration = patient_data['surgery_duration']
        self.surgery_release_day = patient_data['surgery_release_day']
        self.surgery_due_day = patient_data.get('surgery_due_day', None)  # not all patients have a surgery due day

        T = Tempo.T
        shifts = Tempo.shifts

        self.skill_level_required = [[0 for _ in shifts] for _ in range(self.length_of_stay)]
        self.workload_produced =  [[0 for _ in shifts] for _ in range(self.length_of_stay)]

        for x in range(len(patient_data['workload_produced'])):
            day = x//len(shifts)
            shift = x%len(shifts)
            self.workload_produced[day][shift] = patient_data['workload_produced'][x]

        for x in range(len(patient_data['skill_level_required'])):
            day = x//len(shifts)
            shift = x%len(shifts)
            self.skill_level_required[day][shift] = patient_data['skill_level_required'][x]
        
    def __str__(self):
        return f"Patient ID: {self.id}, Age Group: {self.age_group}, Gender: {self.gender}"
            
        
        