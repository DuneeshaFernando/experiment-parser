import re


def parse_experiment_name(exp_str):
    m = re.search("([0-9]+)m-([0-9]+)Mi-([0-9]+)-([0-9]+)", exp_str)
    cpu_mcore_second = int(m.group(1))
    max_memory = int(m.group(2))
    think_time = int(m.group(3))
    jMeter_users = int(m.group(4))
    return [cpu_mcore_second, max_memory, think_time, jMeter_users]