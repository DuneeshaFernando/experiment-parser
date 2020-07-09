import os
import pandas as pd
import numpy as np

def mergeDatasets(experimentDirectory):
    # Read all experiment folders in experimentDirectory
    list_of_files = [f for f in os.listdir(os.path.join(os.pardir, experimentDirectory))]
    list_of_folders=[]
    for file in list_of_files:
        file_path=os.path.join(os.pardir, experimentDirectory, file)
        if os.path.isdir(file_path):
            list_of_folders.append(file)
    # # For each folder in experimentDirectory perform dataset merging
    for folder in list_of_folders:
        # Read 2 csvs and assign those to data frames
        # Dataset A - 10sec granularity
        df_A = pd.read_csv(os.path.join(os.pardir, experimentDirectory+"/"+folder+"/application_metrics.csv"),parse_dates={'datetime':['timestamp']})
        # Dataset B - 1sec granularity
        df_B = pd.read_csv(os.path.join(os.pardir, experimentDirectory+"/"+folder+"/system_metrics.csv"), parse_dates={'datetime':['timestamp']})
        # Adjust timestamp format differences - This step is already handled by parse_dates while reading csv to data frame
        # Round off Dataset A to the nearest 10 sec
        df_A['datetime'] = df_A['datetime'].dt.round('10s')
        # Round off Dataset B to the nearest 10 sec.
        df_B['datetime'] = df_B['datetime'].dt.round('10s')
        # Aggregate multiple records having the same timestamp to a single record. Get the average of values.
        df_B_column_headings = (df_B.columns.values)
        new_arr = np.delete(df_B_column_headings, np.where(df_B_column_headings == 'datetime'))
        print(new_arr)
        print(type(new_arr))
        g = {'cpu_usage':['mean'],'memory_usage':['mean']}
        df_B = df_B.groupby(['datetime']).agg(g)
        # Drop a level from multi-level column index in df_B
        df_B.columns = ['_'.join(col) for col in df_B.columns]
        # Check for multiple records having the same timestamp in df_A also
        duplicate_in_datetime = df_A.duplicated(subset=['datetime'])
        if duplicate_in_datetime.any():
            df_A = df_A.loc[~duplicate_in_datetime]
        # Merge the 2 datasets
        df_merged = pd.merge(df_A, df_B, on='datetime', how='outer')
        df_merged = df_merged.sort_values(by=['datetime'])
        # Change the index of the data frame to datetime
        df = df_merged.set_index('datetime')
        # Handle missing values
        for col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.index = pd.DatetimeIndex(df.index)
        df = df.interpolate(method='time')
        # Handle missing values which were not handled by interpolation
        df = df.fillna(0)
        print(df)
        # Write output data frame to a csv file
        # df.to_csv(os.path.join(os.pardir, experimentDirectory+"/"+folder+"/merged_system_application_metrics.csv"))

if __name__ == '__main__':
    mergeDatasets(experimentDirectory='experimentFolder')