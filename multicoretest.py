from csvreader import read_patient_csv
from patient_solver import solve_for_patient
from patient_solver import (
    solve_for_schnider,
    solve_for_marsh,
    solve_for_custom,
    solve_for_kataria,
)
from patient_state import PatientState

import math
import statistics
import time

from multiprocessing import Pool
import numpy as np

def multi_core_test(cores, maxpt, params):
    # TODO change this so params can be any size

    step_size = round(maxpt / cores)

    jobs = []

    for idx in range(cores):
        a = step_size * idx + 1
        b = step_size * (idx + 1)
        if idx == (cores-1):
            b = maxpt
        thing = (a, b, params)
        jobs.append(thing)

    
    results = pool.map(test_with_schnider, jobs)

    MDPE = []
    MDAPE = []
    wobble = []
    divergence = []

    for result in results:

        MDAPE += result[0]
        MDPE += result[1]
        wobble += result[2]
        divergence += result[3]
        
    MDPE = statistics.median(MDPE)
    MDAPE = statistics.median(MDAPE)
    wobble = statistics.median(wobble)
    divergence = statistics.median(divergence)

    #calculate euclidian norm
    euclid_norm = np.linalg.norm(np.array[MDPE, MDAPE, wobble, divergence])
    
    data = (euclid_norm, MDAPE, MDPE, wobble, divergence)
    print(data)

if __name__ == "__main__":
    pool = Pool(4)