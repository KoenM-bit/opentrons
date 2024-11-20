import json
import pandas as pd
import statistics
import os
import traceback
import plotly.graph_objects as go

global baseline_x, baseline_y
baseline_x = 'baseline_x'
baseline_z = 'baseline_z'

global options
options = ['Make Baseline', 'Validate Labware', 'Plot Baseline']

def plot_baseline():
    baselines = [baseline_x, baseline_z]
    bins = list(range(128))  # X-axis: Bin numbers (0 to 127)
    for baseline in baselines:
        try:
            file = open(baseline, 'r')
        except:
            raise
        baseline_dict = json.load(file)
        # Create line traces for each zone
        fig = go.Figure()
        for zone in baseline_dict:
            zone_data = baseline_dict[zone]
            fig.add_trace(go.Scatter(x=bins, y=zone_data, mode='lines', name=f'Zone {zone}'))

        # Customize layout
        fig.update_layout(
            title=f"TOF Sensor Baseline: {baseline}",
            xaxis_title="Bins",
            yaxis_title="Photon Count",
            legend_title="Zones",
            template="plotly_white",
        )

        # Show the plot
        fig.show()

def create_baseline(df_path, axis):
    df = pd.read_csv(df_path)
    print(df.shape)
    baseline_rows = df[(df['Labware Stacked'] == 0) & (df['Axis'] == axis)]
    baseline_values = baseline_rows['Values']
    bin_labels = ['Time', 'Zone'] + [str(i) for i in range(1, 129)]
    baseline_values.columns = bin_labels
    print(len(baseline_values))
    sample_df = None
    zones = {}
    return_zones = {}
    i = 0

    for entry in baseline_values:
        # Load JSON and create a DataFrame
        samples = json.loads(entry)
        sample_df = pd.DataFrame(samples)
        sample_df.columns = bin_labels

        # Iterate through each zone in the DataFrame
        for zone in sample_df['Zone'].to_list():
            # Ensure zone is a string
            zone = str(int(float(zone)))  # Convert to int, then to string
            if zone not in zones:
                zones[zone] = {}  # Initialize zone if not present

            for bin_label in bin_labels[2:]:
                bin_str = str(bin_label)  # Ensure bin_label is a string
                if bin_str not in zones[zone]:
                    zones[zone][bin_str] = []  # Initialize bin if not present

                # Extract bin values for the current zone and bin_label
                bin_vals = sample_df.loc[sample_df['Zone'] == float(zone), bin_label].tolist()
                zones[zone][bin_str].extend(bin_vals)  # Efficiently append values

    for zone in zones:   
        if zone not in return_zones:
            return_zones[zone] = []
            bin_thresholds = []
        for bin_label in zones[zone]:
            list_vals = zones[zone][bin_label]
            mean = sum(list_vals)
            std = statistics.pstdev(list_vals)
            threshold = mean+(6*std)
            bin_thresholds.append(threshold)
        return_zones[zone] = bin_thresholds
    return return_zones

def process_data(data):
    df = pd.read_csv(data, header=None)
    # print(df)

    bin_labels = ['Time', 'Zone'] + [str(i) for i in range(1, 129)]
 
    df.columns = bin_labels
    matrix = df.to_numpy()
    values = matrix.tolist()

    sample_df = None
    zones = {}
    return_zones = {}
    i = 0

    for entry in values:
        samples = values
        sample_df = pd.DataFrame(samples)
        sample_df.columns = bin_labels

        # Iterate through each zone in the DataFrame
        for zone in sample_df['Zone'].to_list():
            # Ensure zone is a string
            zone = str(int(float(zone)))  # Convert to int, then to string
            if zone not in zones:
                zones[zone] = {}  # Initialize zone if not present

            for bin_label in bin_labels[2:]:
                bin_str = str(bin_label)  # Ensure bin_label is a string
                if bin_str not in zones[zone]:
                    zones[zone][bin_str] = []  # Initialize bin if not present

                # Extract bin values for the current zone and bin_label
                bin_vals = sample_df.loc[sample_df['Zone'] == float(zone), bin_label].tolist()
                zones[zone][bin_str].extend(bin_vals)  # Efficiently append values

    for zone in zones:   
        if zone not in return_zones:
            return_zones[zone] = []
            bin_averages = []
        for bin_label in zones[zone]:
            list_vals = zones[zone][bin_label]
            mean = sum(list_vals)
            bin_averages.append(mean)
        return_zones[zone] = bin_averages
        # print(return_zones)
    return return_zones

    
def sense_labware(axis, data):
    raw_data = process_data(data)
    baseline_zones = {}
    baseline_file = baseline_z

    if axis == 'X-Axis':
        baseline_file = baseline_x
    try:
        with open(baseline_file, 'r') as file:
            baseline_zones = json.load(file)
            file.close()
    except json.JSONDecodeError:
        print("Can't read file")
    if axis == 'X-Axis':
        # Zone 6: If any bins 25 - 40 are positive, we see labware,  have the script say “labware!”
        z6_baseline = baseline_zones['6']
        z6_raw_data = raw_data['6']
        for bin in range(25, 41):
            delta = z6_raw_data[bin] - z6_baseline[bin]
            if delta > 0:
                return True
    elif axis == 'Z-Axis':
        # Zone1: If any bin lower than 54 is positive, we see labware, have the script say “labware!”
        z1_baseline = baseline_zones['1']
        # print(f"BASE: {z1_baseline}")
        z1_raw_data = raw_data['1']
        # print(f"RAW: {z1_raw_data}")
        for bin in range(54):
            delta = z1_raw_data[bin] - z1_baseline[bin]
            if delta > 0:
                return True
    return False

def menu():
    for i, option in enumerate(options):
        print(f'{i}) {option}')
    selection_int = int(input('What do you want to do?\n'))
    if options[selection_int] == 'Make Baseline':
        df_path = input("Enter path to df: ")
        z_baseline_df = create_baseline(df_path, 'Z-Axis')
        x_baseline_df = create_baseline(df_path, 'X-Axis')

        directory = os.curdir
        try:
            baseline_path_z = os.path.join(directory, baseline_z)
            baseline_path_x = os.path.join(directory, baseline_x)
            with open(baseline_path_z, 'w+')as file:
                json.dump(z_baseline_df, file)
            file.close()

            with open(baseline_path_x, 'w+')as file:
                json.dump(x_baseline_df, file)
            file.close()
        except:
            traceback.print_exc()
    elif options[selection_int] == 'Validate Labware':
        file_location = input('Enter csv file: ')
        print('x')
        print('z')
        axis = input('Which axis?: ')
        if axis == 'x':
            axis = 'X-Axis'
        elif axis == 'z':
            axis = 'Z-Axis'
        print(sense_labware(axis, file_location))
    elif options[selection_int] == 'Plot Baseline':
        try:
            plot_baseline()
        except:
            print('No baseline data, run \'Make Baseline\' first')
            sys.exit(1)

if __name__ == '__main__':
    menu()

    