# Master program to make everything run
import json
import sys
import os

import parsl
from numpy import arange
from parsl.configs.local_threads import config
from parsl.app.app import bash_app

import generate_config


# basic parsl config
parsl.load(config)


def temp_spread(t_min, t_max, T_ba, dT):
    # Stores each temp pair as a tuple
    t_s = arange(t_min, t_max, T_ba)
    count = len(t_s)
    range_list = []
    for i in range(count):
        range_list.append((t_s[i] + dT, t_s[i] + T_ba))
    return range_list


@bash_app
def run_single_temp_range(temp_pair):
    write_T_min = round(temp_pair[0], 3)
    write_T_max = round(temp_pair[1], 3)
    # Now generate:
    return "python3 {11}/{5}/Master_Codes/{12} {0} {6} {7} {2} {3} {8} {10} {11}".format(size, n, write_T_min, write_T_max, model, model_folder,
                                                                                         delta_T, measurements, y_tilde, whole_path, theta_coefficient, path, scripts[model])


def submit_all_jobs(temp_list):
    script_num = 1
    for temp_pair in temp_list:
        run_single_temp_range(temp_pair)


def setup_environment():
    # Make sure environment is set up
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)


if __name__ == '__main__':
    run_config = {}
    try:
        conf_file = sys.argv[1]
        with open(conf_file) as fh:
            run_config = json.load(fh)
    except Exception as e:
        run_config = generate_config.ask_user_for_info()
    setup_environment()
    temp_list = array(temp_spread(T_start, T_end, T_batch, delta_T))
    submit_all_jobs(temp_list)
