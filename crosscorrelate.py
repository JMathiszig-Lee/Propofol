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


def test_against_real_data(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv()

    MDPE = []
    MDAPE = []
    wobble = []
    divergence = []

    for patient in patients[pmin:pmax]:
        res = solve_for_patient(patient, params)

        MDPE += res["bias"]
        MDAPE += res["median"]
        wobble += res["wobble"]
        divergence += res["divergence"]

    # b = totalrms / count
    # c = totalmed / count
    # d = totalbias / count

    data = (b, c, d)
    return data


def test_with_schnider(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv()

    MDPE = []
    MDAPE = []
    wobble = []
    divergence = []


    for patient in patients[pmin:pmax]:
        res = solve_for_schnider(patient, params)

        MDPE.append(res["bias"])
        MDAPE.append(res["median"])
        wobble.append(res["wobble"])
        divergence.append(res["divergence"])

    data = (MDAPE, MDPE, wobble, divergence)
    print(data[0])
    return data


def test_with_kataria(stuff):
    pmin = stuff[0]
    pmax = stuff[1]
    params = stuff[2]
    patients = read_patient_csv()

    totalrms = 0
    totalmed = 0
    totalbias = 0
    count = 0

    for patient in patients:
        if patient["age"] < 10:
            res = solve_for_kataria(patient, params)
            a = res["percent"]
            med = res["median"]
            bias = res["bias"]

            # print "%-10s %-10s" % (a, med)

            totalrms += a
            totalbias += bias
            totalmed += med
            count += 1

    b = totalrms / count
    c = totalmed / count
    d = totalbias / count

    data = (b, c, d)
    return data


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

    
    results = pool.map(test_against_real_data, jobs)

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
    startTime = time.time()
    pmin = 1
    pmax = 3
    params = []

    stuff = (pmin, pmax, params)
    schnider = test_with_schnider(stuff)

    endtime = time.time()
    worktime = endtime - startTime

    print(worktime)
