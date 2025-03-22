import random
import time
from time import sleep

class ALNS:

    def __init__ (self, problem, starting_point):
        self.problem = problem
        self.starting_point = starting_point


    def solve(self, number_of_iterations = 1000):

        starting_point = self.starting_point
        problem = self.problem

        for t in range(number_of_iterations):   # iterating
            progress(t/number_of_iterations * 100)
            sleep(0.0001)



def progress(percent=0, width=30):
    left = int(width * percent // 100)
    right = width - left
    print('\r[ ', '#' * left, ' ' * right, ']',
          f' {percent: .0f}%', sep='', end='', flush=True)


