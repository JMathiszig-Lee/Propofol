import numpy as np
import cProfile

from scipy.optimize import least_squares

from patient_state import PatientState
from patient_solver import solve_for_patient

from csvreader import read_patient_csv


def solve():
    starting_params = PatientState.schnider_params()

    params_array = convert_params_structure_to_vector(starting_params)

    result = least_squares(get_residuals_for_all_patients, params_array, bounds=[-1000, 1000], ftol=1e-001, xtol=1e-001, gtol=1e-001, x_scale=1.0, max_nfev=1000, verbose=0)
    return result.x


def get_patients():
    # TODO: Memoize
    patients = read_patient_csv()
    return patients


def convert_vector_to_params_structure(params_vector):
    """Convert numpy array of parameters to a parameters dictionary"""
    params = {
        'k10a': params_vector[0],
        'k10b': params_vector[1],
        'k10c': params_vector[2],
        'k10d': params_vector[3],
        'k12a': params_vector[4],
        'k12b': params_vector[5],
        'k13':  params_vector[6],
        'k21a': params_vector[7],
        'k21b': params_vector[8],
        'k21c': params_vector[9],
        'k21d': params_vector[10],
        'k31':  params_vector[11],
        'v1':   params_vector[12],
        'v3':   params_vector[13],
        'age_offset': params_vector[14],
        'weight_offset': params_vector[15],
        'lbm_offset': params_vector[16],
        'height_offset': params_vector[17]
    }
    return params


def convert_params_structure_to_vector(params):
    """Convert parameters dictionary to a numpy array of parameters, so it can be used in a solver"""

    return np.array([
        params['k10a'], #0
        params['k10b'], #1
        params['k10c'], #2
        params['k10d'], #3
        params['k12a'], #4
        params['k12b'], #5
        params['k13'],  #6
        params['k21a'], #7
        params['k21b'], #8
        params['k21c'], #9
        params['k21d'], #10
        params['k31'],  #11
        params['v1'],   #12
        params['v3'],   #13
        params['age_offset'], #14,
        params['weight_offset'], #15
        params['lbm_offset'], #16
        params['height_offset'] #17
    ])


def find_lsq_for_all_patients(params_vector):
    residuals = get_residuals_for_all_patients(params_vector)
    total_lsq = 0.0
    for residual in residuals:
        total_lsq += residual
    return total_lsq / len(residuals)


def get_residuals_for_all_patients(params_vector):
    params = convert_vector_to_params_structure(params_vector.tolist())
    residuals = []
    patient_list = get_patients()
    for patient in patient_list:
        patient_error = solve_for_patient(patient, params)["error"]
        residuals.append(patient_error)
    return residuals


def test():
    solve_result = solve()
    solved_params = convert_vector_to_params_structure(solve_result)

    schnider_params = PatientState.schnider_params()
    print "Schneider params:"
    print schnider_params

    print "Solution params:"
    print solved_params

    sample_patient = get_patients()[0]

    schnider_solution = solve_for_patient(sample_patient, schnider_params)["cps"]
    solved_solution = solve_for_patient(sample_patient, solved_params)["cps"]

    print "Schnider solution:"
    print schnider_solution

    print "Solved solution:"
    print solved_solution

    # print "Expected solution:"
    # print sample_patient['expected_result']


def profile_test():
    params_vector = PatientState.schnider_params()
    find_lsq_for_all_patients(convert_params_structure_to_vector(params_vector))

if __name__ == "__main__":
    test()
