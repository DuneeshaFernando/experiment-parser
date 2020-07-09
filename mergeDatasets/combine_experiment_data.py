from os import walk
import pandas as pd
import numpy as np

from Utilities.parse_strings import parse_experiment_name

DIRECTORY_PATH = '/Users/duneesha/Documents/2020work@wso2/experiment-parser/experimentFolder/experiment2'
# DIRECTORY_PATH = '/Users/isuru/PycharmProjects/Deployment_optimization/Data/choreo_experiment_1/Echo/'


def summarise_experiments(experiment_data):
    averaging_data = experiment_data[
        ['throughput(req/s)', 'avg_latency(ms)', 'concurrency', 'cpu_level', 'memory_level']]
    summary_line = pd.DataFrame()
    summary_line['Experiment'] = [experiment_data['Experiment'][0]]
    for column_name in averaging_data.columns:
        if column_name != 'Experiment':
            summary_line[column_name + '_average'] = np.round(np.average(experiment_data[column_name]), 2)
            summary_line[column_name + '_90th'] = np.round(np.percentile(experiment_data[column_name], 90), 2)
            summary_line[column_name + '_99th'] = np.round(np.percentile(experiment_data[column_name], 99), 2)
            summary_line[column_name + '_std'] = np.round(np.std(experiment_data[column_name]), 2)

    return summary_line


def find_all_files():
    all_dirs = []
    experiment_data = []
    for (dirpath, dirnames, filenames) in walk(DIRECTORY_PATH):
        if "application_metrics.csv" in filenames and "CPU_and_memory_data.csv" in filenames:
            experiment_data.append([dirpath.split('/')[-1],
                                    dirpath + "/application_metrics.csv",
                                    dirpath + "/system_metrics.csv"])
        all_dirs.append(dirpath.split('/')[-1])
    failed_experiments = list(set(all_dirs) - set([v[0] for v in experiment_data]))
    return experiment_data, failed_experiments


def merge_dfs(basedf, rest, merge_feild):
    for df in rest:
        basedf = pd.merge(basedf, df, on=merge_feild, how="left")
    return basedf


def process_resource_data(resource_data, time_stamps):
    cpu_data = list(resource_data['cpu_level'])
    memory_data = list(resource_data['memory_level'])
    resource_time_stamp = list(resource_data['time_elp(s)'])
    metrics_time_stamp = list(time_stamps)

    end_location = 1
    cpu_chunk = []
    memory_chunk = []

    for time_instance in metrics_time_stamp:
        cpu_temp = []
        memory_temp = []

        if time_instance == 0:
            cpu_temp.append(cpu_data[0])
            memory_temp.append(memory_data[0])
        else:
            while resource_time_stamp[end_location] < time_instance:
                cpu_temp.append(cpu_data[end_location])
                memory_temp.append(memory_data[end_location])
                end_location = end_location + 1

        cpu_chunk.append(np.round(np.average(cpu_temp), 2))
        memory_chunk.append(np.round(np.average(memory_temp), 2))

    return_data_df = pd.DataFrame()
    return_data_df['time_elp(s)'] = metrics_time_stamp
    return_data_df['cpu_level'] = cpu_chunk
    return_data_df['memory_level'] = memory_chunk

    return return_data_df


def read_experiment(files):
    th_la_df = pd.read_csv(files[0], index_col="Unnamed: 0")

    cpu_memory_df = pd.read_csv(files[1])
    cpu_memory_df = process_resource_data(cpu_memory_df, th_la_df["time_elp(s)"])

    merged = merge_dfs(th_la_df, [cpu_memory_df], merge_feild="time_elp(s)")
    merged = merged.sort_values(by=["time_elp(s)"], ascending=True)
    merged = merged.fillna(value=0)

    return merged


def process_merged_data(merged_data, folder_name):
    configuration_data = np.array([parse_experiment_name(v) for v in merged_data["Experiment"].values])
    merged_data["cpu_mcore_second"] = configuration_data[:, 0]
    merged_data["max_memory"] = configuration_data[:, 1]
    merged_data["think_time"] = configuration_data[:, 2]
    merged_data["jMeter_users"] = configuration_data[:, 3]

    merged_data["%cpu_utilization"] = np.round(merged_data["cpu_level"] * 100 / merged_data["cpu_mcore_second"], 2)
    merged_data["%memory_utilization"] = np.round(
        merged_data["memory_level"] * 100 / (merged_data["max_memory"] * 1000), 2)

    merged_data.to_csv(DIRECTORY_PATH + '/' + folder_name + '/merged_data.csv')

    return merged_data


def load_all_data():
    experiment_data, failed_experiments = find_all_files()

    # save experiment sucess data
    experiment_names = [v[0] for v in experiment_data] + failed_experiments
    experiment_success_df = pd.DataFrame()
    experiment_success_df["Experiment"] = experiment_names
    experiment_success_df["isSuccessFul"] = [1 for i in range(len(experiment_data))] + [0 for i in
                                                                                        range(len(failed_experiments))]
    experiment_success_df.to_csv(DIRECTORY_PATH + "experiment_success_df.csv")

    experiment_dfs = []
    summary = []
    for f in experiment_data:
        experiment_df = read_experiment(f[1:])
        experiment_df.insert(0, "Experiment", f[0])
        summary.append(summarise_experiments(experiment_df))
        experiment_df = process_merged_data(experiment_df, f[0])
        experiment_dfs.append(experiment_df)

    summary = pd.concat(summary)
    all_data = pd.concat(experiment_dfs)
    return all_data, summary


if __name__ == '__main__':
    all_data, summary_data = load_all_data()

    all_data.to_csv(DIRECTORY_PATH + "combined.csv")
    summary_data.to_csv(DIRECTORY_PATH + "experiment_summary.csv")
