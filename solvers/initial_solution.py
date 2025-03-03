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

def initial_solution(solution , occupants, patients, surgeons, nurses, rooms, theaters, T, shifts , weights):

   # for PATIENT_SCHEDULE we have to find ROOM and DAY for EACH PATIENT

   # for SURGEONS_OPERATIONS we have to find the couple (THEATER, PATIENT) knowing that a patient can be operated only in one theater
   #                         we have to find this couple for EACH SURGEON and PATIENT 

   # for NURSE_SCHEDULE we have to find the triad (ROOM, DAY, SHIFT)