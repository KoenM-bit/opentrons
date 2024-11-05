

def sense_labware(axis, raw_data, baseline):
    clean_data = [raw_value - baseline_value for raw_value, baseline_value in zip(raw_data, baseline)]
    if axis == 'x':
        # Zone 6: If any bins 25 - 40 are positive, we see labware,  have the script say “labware!”
        for bin in range(25, 41):
            if clean_data[bin] > 0:
                return True
    elif axis == 'z':
        # Zone1: If any bin lower than 54 is positive, we see labware, have the script say “labware!”
        for bin in range(54):
            if clean_data[bin] > 0:
                return True