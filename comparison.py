import statistics
import numpy as np

from PyTCI.models import propofol
from patient_solver import solve_for_patient
from tqdm import tqdm

def compare_models(patients: list, model: str = "Marsh"):
    """
    Function to make comapring exisiting models easier.

    Valid options for model:
    - Marsh
    - Schnider
    - Eleveld

    All will test against all other valid options

    Returns:
    Dictionary of the type
    "model": model
    "results": {
        "norm": euclidian norm of other results
        "MDPE": median performance error
        "MDAPE": median absolute performance error
        "Wobble": wobble
        "Divergence": deviation of MDAPE over time
    }
    """

    valid_models = ["Marsh", "Schnider", "Eleveld"]

    if model not in valid_models:
        raise ValueError("Invalid model option")

    MDPE = []
    MDAPE = []
    wobble = []
    div = []
    patient_level = []
    
    with tqdm(patients) as pbar:
        for patient in patients:

            if model == "Marsh":
                patient_model = propofol.Marsh(patient["weight"])
            elif model == "Schnider":
                patient_model = propofol.Schnider(
                    patient["age"], patient["weight"], patient["height"], patient["sex"]
                )
            elif model == "Eleveld":
                patient_model = propofol.Eleveld(
                    patient["age"], patient["weight"], patient["height"], patient["sex"]
                )
            else:
                raise ValueError("Invalid model option")

            res = solve_for_patient(patient_model, patient["events"])

            patient_level.append(
                {
                    "patient": patient["id"],
                    "results": {
                        "MDPE": res["MDPE"],
                        "MDAPE": res["MDAPE"],
                        "Wobble": res["Wobble"],
                        "Divergence": res["Divergence"],
                    },
                }
            )

            MDPE.append(res["MDPE"])
            MDAPE.append(res["MDAPE"])
            wobble.append(res["Wobble"])
            div.append(res["Divergence"])

            pbar.update(1)       

    MDPE = statistics.median(MDPE)
    MDAPE = statistics.median(MDAPE)
    wobble = statistics.median(wobble)
    divergence = statistics.median(div)

    # calculate euclidian norm
    euclid_norm = np.linalg.norm([MDPE, MDAPE, wobble, divergence])

    result_dict = {
        "set": model,
        "results": {
            "Norm": abs(euclid_norm),
            "MDPE": MDPE,
            "MDAPE": MDAPE,
            "Wobble": wobble,
            "Divergence": divergence,
        },
        "patient_level": patient_level,
    }

    return result_dict