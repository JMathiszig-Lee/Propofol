import statistics

from scipy import stats


def solve_for_patient(patient, events):
    patient_model = patient

    results = {"cps": []}

    previous_time_mins = 0
    current_dose_mg_per_sec = 0
    infusion_seconds_remaining = 0

    errorlist = []
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
            percent_error = error / predicted_cp

            results["cps"].append(
                {
                    "time_seconds": seconds,
                    "predicted_cp": predicted_cp,
                    "measured_cp": event["cp"],
                    "performance_error": percent_error,
                }
            )

            biaslist.append(error)
            absolutelist.append(abs(percent_error))
            timeslist.append(seconds)
            errorlist.append(percent_error)

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

    results["MDPE"] = statistics.median(errorlist)
    results["MDAPE"] = statistics.median(absolutelist)
    results["Wobble"] = stats.median_absolute_deviation(errorlist)

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        timeslist, absolutelist
    )

    results["Divergence"] = slope * 3600

    return results
