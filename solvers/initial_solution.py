from instances.hospital import Times
from instances.hospital import Rooms
from instances.hospital import Theaters
from instances.patient import Patient
from instances.occupant import Occupant
from instances.surgeon import Surgeon
from instances.nurse import Nurse
from instances.problem import Problem

from instances.solution import Solution

# the objective of this function is to find an initial solution to the scheduling problem.
#  We have to generate a solution that is compatible with the hard constraints

def initial_solution(solution , occupants, patients, surgeons, nurses, rooms, theaters, T, shifts):

   # for PATIENT_SCHEDULE we have to find ROOM and DAY for EACH PATIENT

   # for SURGEONS_OPERATIONS we have to find the couple (THEATER, PATIENT) knowing that a patient can be operated only in one theater
   #                         we have to find this couple for EACH SURGEON and PATIENT 

   # for NURSE_SCHEDULE we have to find the triad (ROOM, DAY, SHIFT) for EACH DAY, SHIFT and ROOM

   ############################### ADD THE OCCUPANTS ###################################################

   # first of all we have to add the occupants to the hospital

   for occupant in occupants:
      rooms.add_occupant(occupant,T)


   ############################### PATIENT_SCHEDULE + SURGEONS_OPERATIONS #######################################

   mandatory_patients = []
   for patient in patients:
      if patient.mandatory == 0:   # for a first initial solution we kick off the not mandatory patients
         solution.patient_schedule[patient.id] = {'patient': patient,
                                                  'room': None,     # no room
                                                  'day': None}      # no admission day
      else:
         # the idea is to order by the delay between the release day and the due day 
         mandatory_patients.append({'patient': patient,
                                    'delay': patient.surgery_due_day - patient.surgery_release_day})
         
   mandatory_patients.sort(key=lambda x: x['delay']) # sort over delay

   # create a variable that stores the surgeons + the time that they invest during a day for an operation

   surgeons_workload = [[0 for t in range(T)] for surgeon in surgeons]

   # create a variable that stores the theaters + the time of the operation of the patient 

   theaters_workload = [[0 for t in range(T)] for theater_id in theaters.theaters_id]
   
   for patient_dic in mandatory_patients:
      patient = patient_dic['patient']
      
      # we have to find a room for this patient,
      # the room must be
      # 1) compatible
      # 2) of the same sex of the patient
      # 3) the there must be capacity for all his stay in the hospital

      # also check that
      # 4) there must be a surgeon for the patient in their admission date 
      # 5) there must be a theater where the patient can be operated

      compatible_room_ids = patient.compatible_room_ids
      found_solution = False    

      for admission_day in range(patient.surgery_release_day, patient.surgery_due_day+1):   # selecting the admission date

         there_is_surgeon = False
         there_is_theater = False

         for idx,surgeon in enumerate(surgeons):
            if surgeons_workload[idx][admission_day] + patient.surgery_duration <= surgeon.max_surgery_time[admission_day]:    # if a surgeon can operate in the admission date 
               there_is_surgeon = True
               break
         
         for theater_id in theaters.theaters_id:
            if theaters_workload[theater_id][admission_day] + patient.surgery_duration <= theaters.theaters_capacity[theater_id][admission_day]: # if there is a theater in the admission date
               there_is_theater = True
               break

         if there_is_surgeon and there_is_theater:  # i do all the for only if there is a theater and a surgeon
            for room_id in compatible_room_ids:
               there_is_place = True
               same_gender = True
               for t in range(admission_day, min(admission_day+patient.length_of_stay, T)):    # I take the min, because the admis + length can go over T, and i don't want to know nothing after T
                  room_gender = rooms.rooms_gender[t][room_id] 
                  room_count_people = rooms.rooms_count_people[t][room_id]
                  if room_gender is not None and room_gender != patient.gender:    # room gender is None when a room is empty
                     same_gender = False
                  if room_count_people >= rooms.rooms_capacity[room_id]:   # if there's no place during the schedule for a patient 
                     there_is_place = False
               if there_is_place and same_gender:        # if all the constraints are ok add the solution
                  solution.patient_schedule[patient.id] = {'patient': patient,
                                                         'room': room_id,    
                                                         'day': admission_day}
                  solution.surgeons_operations[patient.id][surgeon.id]  = {'surgeon': surgeon,
                                                                     'theater': theater_id,
                                                                     'patient': patient}
                  
                  # add the time to the surgeons and theaters

                  surgeons_workload[idx][admission_day] += patient.surgery_duration
                  theaters_workload[theater_id][admission_day] += patient.surgery_duration

                  found_solution = True
                  break   # close the for that is running over rooms_ids
            if found_solution:
               break # close the for that is running over the admission date
      # now we add the patient to the hospital
      if found_solution:
         rooms.add_patient(room_id, patient, admission_day, T)



   #################################### NURSE SCHEDULE #######################################

   # for the nurse we have to check that during each day and each shift there is almost a nurse in each room
   # the idea is to assign for each day and shift a nurse to a room, he/she can work on that day and shift

   for day in range(T):
      for shift in shifts:
         nurse_that_can_work = [nurse for nurse in nurses if nurse.possible_turns[day][shift] > 0]
         counter = 0
         while counter < rooms.n_rooms:
            room_id = rooms.rooms_id[counter]
            nurse = nurse_that_can_work[counter % len(nurse_that_can_work)]
            solution.nurses_schedule[day][shift][room_id].append( {'nurse': nurse,
                                                            'room': room_id})
            counter += 1
             
            
   return solution
