from glob import glob
from pylab import *


def gen_data(model):
    names = glob("{}/finished_data/*".format(model))
    data = [[], [], [], [], [], [], []]
    helpi = names[0].split(";")[2]
    names.sort(key=lambda x: float(x.split(';')[2]))
    for n in range(len(names)):
        i_data = list(loadtxt(names[n]))
        for i in range(len(i_data)):
            i_data_i = list(i_data[i])
            for j in i_data_i:
                data[i].append(j)

    return data, size, measurements


def three_models_plot(T_plot, E_XY, E_aub, E_replica, sigma_XY, sigma_AUB,
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


def calc_rmi_for_temp(E_XY, E_replica, E_AUB, T_plot):
    count = len(E_XY)
    RMIpts = []
    RMIsigmaplot = []
    deltaT = Tstep
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


def aggregate(DATA, Tstep):
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

    three_models_plot(T_plot, E_XY, E_aub, E_replica, sigma_XY, sigma_AUB,
                      sigma_replica)

    RMIsigmaplot, RMIpts, sigma_i = calc_rmi_for_temp()

    plot_rmi(T_plot, RMIpts, RMIsigmaplot)

    out_data = [
        T_plot, E_XY, sigma_XY, E_AUB, sigma_AUB, E_replica, sigma_replica,
        RMIpts, RMIsigmaplot
    ]
    path = 'final_data'
    savetxt('{0}/RMI_XY;{1};{2}.txt'.format(path, size, measurements),
            out_data)
    return [T_plot, RMIpts]


if __name__ == '__main__':
    data, size, measurements = gen_data(run_config["model"])
    aggregate(data, 0.05)
