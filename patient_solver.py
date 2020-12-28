from patient_state import PatientState, PatientState2, MarshState

import math
import statistics
import numpy

from PyTCI.models import propofol
from sklearn.linear_model import LinearRegression

def solve_for_patient(patient, events):
    patient_model = patient

    results = {"cps": []}

    total_lsq_error = 0
    total_measurements = 0
    total_percent_error = 0

    previous_time_mins = 0
    current_dose_mg_per_sec = 0
    infusion_seconds_remaining = 0

    absolutelist = []
    timeslist = []
    biaslist = []

    for event in events:
        for t in range(int((event["time_mins"] - previous_time_mins) * 60)):
            if infusion_seconds_remaining > 0:
                patient_model.give_drug(current_dose_mg_per_sec)
                infusion_seconds_remaining -= 1

            patient_model.wait_time(1)

        if event["type"] == "measurement":
            predicted_cp = patient_model.x1
            seconds = int(previous_time_mins * 60) + t
            
            error = event["cp"] - predicted_cp
            percent_error = error / event["cp"]
            

            results["cps"].append(
                {
                    "time_seconds": seconds,
                    "predicted_cp": predicted_cp,
                    "measured_cp": event["cp"],
                    "performance_error": percent_error
                }
            )

            biaslist.append(error)
            absolutelist.append(abs(percent_error))
            timeslist.append(seconds)

        elif event["type"] == "start_infusion":
            amount_mg = event["propofol_mg"]
            current_dose_mg_per_sec = event["rate_mg_per_min"] / 60
            infusion_seconds_remaining = amount_mg / current_dose_mg_per_sec
        else:
            raise ValueError(
                "Unknown patient event type '%s'. Expected 'measurement' or 'start_infusion'"
                % event["type"]
            )

        previous_time_mins = event["time_mins"]

    results["median"] = statistics.median(absolutelist)
    results["bias"] = statistics.median(biaslist)

    #double check this before submitting for publication
    wobble = [(results["bias"] - x)/results["bias"] for x in absolutelist]
    results["wobble"] = abs(statistics.median(wobble))

    #do linear regression for divergence
    Xs = numpy.reshape(timeslist, (-1, 1))
    ys = numpy.reshape(absolutelist, (-1, 1))
    divergence = LinearRegression().fit(Xs, ys)
    results["divergence"] = divergence.coef_[0][0]

    return results


def solve_for_schnider(patient, params):

    patient_model = propofol.Schnider(
        patient["age"], patient["weight"], patient["height"], patient["sex"]
    )
    return solve_for_patient(patient_model, patient["events"])


def solve_for_marsh(patient, params):
    patient_model = propofol.Marsh(patient["weight"])
    return solve_for_patient(patient_model, patient["events"])

def solve_for_kataria(patient, params):
    patient_model = propofol.Kataria(patient["weight"], patient["age"])
def solve_for_eleveld(patient, params):
    patient_model = propofol.Eleveld(patient["age"], patient["weight"], patient["height"], patient["sex"])
    return solve_for_patient(patient_model, patient["events"])

def solve_for_custom(patient, params):
    patient_model = propofol.Marsh(patient["weight"])
    return solve_for_patient(patient_model, patient["events"])
