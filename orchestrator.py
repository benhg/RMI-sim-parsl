# Master program to make everything run
import json
import sys
import os
import shutil
import glob

from numpy import arange, array, loadtxt, savetxt
import parsl
from parsl.configs.local_threads import config
from parsl.app.app import bash_app
from pylab import *

import generate_config

# basic parsl config
parsl.load(config)

# Initialize empty run config
run_config = {}


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
    return "python3 {11}/{5}/Master_Codes/{12} {0} {6} {7} {2} {3} {8} {10} {11}".format(
        size, n, write_T_min, write_T_max, model, model_folder, delta_T,
        measurements, y_tilde, whole_path, theta_coefficient, path,
        scripts[model])


def submit_all_jobs(temp_list):
    for temp_pair in temp_list:
        run_single_temp_range(temp_pair)


def setup_environment():
    # Make sure environment is set up
    if not os.path.exists(run_config["folder_path"]):
        os.makedirs(run_config["folder_path"])
    else:
        shutil.rmtree(run_config["folder_path"])
        os.makedirs(run_config["folder_path"])


def gen_data(model):
    names = glob.glob("{}_model/finished_data/*".format(model))
    data = [[], [], [], [], [], [], []]
    helpi = names[0].split(";")[2]
    names.sort(key=lambda x: float(x.split(';')[2]))
    for n in range(len(names)):
        i_data = list(loadtxt(names[n]))
        for i in range(len(i_data)):
            i_data_i = list(i_data[i])
            for j in i_data_i:
                data[i].append(j)

    return data, run_config["size"], run_config["measurements"]


def three_models_plot(T_plot, E_XY, E_AUB, E_replica, sigma_XY, sigma_AUB,
                      sigma_replica):
    plot(T_plot, E_XY, 'b', label="Normal XY")
    errorbar(T_plot, E_XY, yerr=sigma_XY)
    plot(T_plot, E_AUB, 'g', label="Union XY")
    errorbar(T_plot, E_AUB, yerr=sigma_AUB)
    plot(T_plot, E_replica, 'r', label="Replica XY")
    errorbar(T_plot, E_AUB, yerr=sigma_replica)
    title(
        "Energies of the Three Models for ".format(run_config["model"]),
        fontsize=16)
    xlabel(r"$T$", fontsize=16)
    ylabel("Energy", fontsize=16)
    xlim(0, 10)
    legend()
    savefig("Three_Models_{}".format(run_config["model"]))


def plot_rmi(T_plot, RMIpts, RMIsigmaplot):
    plot(T_plot, RMIpts)
    xlim(0.5, 5)
    ylim(-0.05, 0.5)
    errorbar(T_plot, RMIpts, yerr=RMIsigmaplot)
    title("Renyi Mutual Information for {}".format(run_config["model"]))
    xlabel(r"$T$", fontsize=16)
    ylabel("RMI", fontsize=16)
    savefig("RMI_{}".format(run_config["model"]))


def calc_rmi_for_temp(E_XY, E_replica, E_AUB, T_plot, sigma_replica, sigma_AUB,
                      sigma_XY):
    count = len(E_XY)
    RMIpts = []
    RMIsigmaplot = []
    deltaT = run_config["delta_T"]
    for i in range(count):
        RMI = 0.0
        sigma_sigma_i = 0.0
        for j in range(i, count):
            term = deltaT * (2 * E_replica[j] - E_AUB[j] - 2 * E_XY[j]) / (
                T_plot[j]**2)
            sigma_sigma_j = ((2 * deltaT) / ((T_plot[j] ** 2) * size * 2))\
                ** 2 * (sigma_replica[j] ** 2) + (deltaT / ((T_plot[j] ** 2) *
                                                            size * 2)) ** 2 * (sigma_AUB[j] ** 2) + (
                (2 * deltaT) / ((T_plot[j] ** 2) * size * 2))\
                ** 2 * (sigma_XY[j] ** 2)
            sigma_sigma_i += sigma_sigma_j
            RMI += term
        sigma_i = sqrt(sigma_sigma_i)
        RMI /= 2 * size
        RMIpts.append(RMI)
        RMIsigmaplot.append(sigma_i)
    return RMIsigmaplot, RMIpts, sigma_i


def save_data(model, out_data):
    path = 'final_data'

    if model == "XY":
        savetxt(
            '{0}/RMI_XY;{1};{2}.txt'.format(path, run_config["size"],
                                            run_config["measurements"]),
            out_data)
    elif model == "QCD":
        savetxt(
            '{0}/RMI_QCD;{1};{2};{3};{4}.txt'.format(
                path, run_config["size"], run_config["measurements"],
                run_config["y_tilde"], run_config["theta_coefficient"]),
            out_data)
    elif model == "beta":
        savetxt(
            '{0}/RMI_beta;{1};{2}.txt'.format(path, run_config["size"],
                                              run_config["measurements"]),
            out_data)
    else:
        print("I don't know how to save the data for this model")


def aggregate(DATA, Tstep, plot=False):
    T_plot = DATA[0]
    # Replica data
    E_replica = DATA[5]
    sigma_replica = DATA[6]
    # AUB data
    E_AUB = DATA[3]
    sigma_AUB = DATA[4]
    # Normal data
    E_XY = DATA[1]
    sigma_XY = DATA[2]
    three_models_plot(T_plot, E_XY, E_AUB, E_replica, sigma_XY, sigma_AUB,
                      sigma_replica)

    RMIsigmaplot, RMIpts, sigma_i = calc_rmi_for_temp(
        E_XY, E_replica, E_AUB, T_plot, sigma_replica, sigma_AUB, sigma_XY)
    out_data = [
        T_plot, E_XY, sigma_XY, E_AUB, sigma_AUB, E_replica, sigma_replica,
        RMIpts, RMIsigmaplot
    ]

    save_data(run_config['model'], out_data)

    if plot:
        three_models_plot(T_plot, E_XY, E_aub, E_replica, sigma_XY, sigma_AUB,
                          sigma_replica)
        plot_rmi(T_plot, RMIpts, RMIsigmaplot)

    return [T_plot, RMIpts]


if __name__ == '__main__':
    try:
        conf_file = sys.argv[1]
        with open(conf_file) as fh:
            run_config = json.load(fh)
    except Exception as e:
        run_config = generate_config.ask_user_for_info()
    setup_environment()
    temp_list = array(
        temp_spread(run_config["T_start"], run_config["T_end"],
                    run_config["T_batch"], run_config["delta_T"]))
    submit_all_jobs(temp_list)
    data, size, measurements = gen_data(run_config["model"])
    try:
        if run_config["delta_beta"]:
            delta = run_config["delta_beta"]
        else:
            delta = run_config["delta_T"]
    except KeyError as e:
        delta = run_config["delta_T"]
    aggregate(data, delta)
