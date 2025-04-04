from instances.hospital import Times
from instances.hospital import Rooms
from instances.hospital import Theaters
from instances.patient import Patient
from instances.occupant import Occupant
from instances.surgeon import Surgeon
from instances.nurse import Nurse
from instances.problem import Problem

from instances.solution import Solution

from solvers.place_patient import place_patient

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
   not_mandatory_patients = []
   for patient in patients:
      if patient.mandatory == 0:   # for a first initial solution we kick off the not mandatory patients
         solution.patient_schedule[patient.id] = {'patient': patient,
                                                  'room': None,     # no room
                                                  'day': None}      # no admission day
         not_mandatory_patients.append({'patient': patient,
                                        'delay': T-patient.surgery_release_day})
      else:
         # the idea is to order by the delay between the release day and the due day 
         mandatory_patients.append({'patient': patient,
                                    'delay': patient.surgery_due_day - patient.surgery_release_day})
         
   mandatory_patients.sort(key=lambda x: x['delay']) # sort over delay
   not_mandatory_patients.sort(key=lambda x: x['delay'])

   # create a variable that stores the surgeons + the time that they invest during a day for an operation

   surgeons_workload = [[0 for t in range(T)] for surgeon in surgeons]

   # create a variable that stores the theaters + the time of the operation of the patient 

   theaters_workload = [[0 for t in range(T)] for theater_id in theaters.theaters_id]
   
   for patient_dic in mandatory_patients:
      patient = patient_dic['patient']
      found_solution = place_patient(solution, patient, theaters_workload, surgeons_workload, rooms, theaters, surgeons, T)
      if not found_solution:
         print("patient ", patient.id, " has no place in the hospital")



   for patient_dic in not_mandatory_patients:   # also for not mandatory patients
      patient = patient_dic['patient']
      found_solution = place_patient(solution, patient, theaters_workload, surgeons_workload, rooms, theaters, surgeons, T)
      if not found_solution:
         continue   # if a not mandatory patient has no place in the hospital, we don't care about him/her

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
