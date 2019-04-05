from glob import *
from pylab import *

names = glob("/home/users/briansmith/files/XY_model/finished_data/*")
data = [[], [], [], [], [], [], []]
helpi = names[0].split(";")[2]
names.sort(key=lambda x: float(x.split(';')[2]))
for n in range(len(names)):
    i_data = list(loadtxt(names[n]))
    for i in range(len(i_data)):
        i_data_i = list(i_data[i])
        for j in i_data_i:
            data[i].append(j)

size = int(input("Enter the linear lattice size: "))
measurements = int(input("Enter the number of independent measurements: "))


def calcRMI(DATA, Tstep, graph='yes'):
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

    plot(T_plot, E_XY, 'b', label="Normal XY")
    errorbar(T_plot, E_XY, yerr=sigma_XY)
    plot(T_plot, E_AUB, 'g', label="Union XY")
    errorbar(T_plot, E_AUB, yerr=sigma_AUB)
    plot(T_plot, E_replica, 'r', label="Replica XY")
    errorbar(T_plot, E_AUB, yerr=sigma_replica)
    title("Energies of the Three Models", fontsize=16)
    xlabel(r"$T$", fontsize=16)
    ylabel("Energy", fontsize=16)
    xlim(0, 10)
    legend()
    savefig("Three_Models")
    show()

    # Calculate RMI for each temperature
    print("Working on Renyi Mutual Information...")
    count = len(E_XY)
    RMIpts = []
    RMIsigmaplot = []
    deltaT = Tstep
    for i in range(count):
        RMI = 0.0
        sigma_sigma_i = 0.0
        for j in range(i, count):
            term = deltaT * (2 * E_replica[j] - E_AUB[j] - 2 *
                             E_XY[j]) / (T_plot[j] ** 2)
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

    if graph == 'yes':
        plot(T_plot, RMIpts)
        xlim(0.5, 5)
        ylim(-0.05, 0.5)
        errorbar(T_plot, RMIpts, yerr=RMIsigmaplot)
        title("Renyi Mutual Information")
        xlabel(r"$T$", fontsize=16)
        ylabel("RMI", fontsize=16)
        savefig("RMI")
        show()

    out_data = [
        T_plot,
        E_XY,
        sigma_XY,
        E_AUB,
        sigma_AUB,
        E_replica,
        sigma_replica,
        RMIpts,
        RMIsigmaplot]
    path = '/home/users/briansmith/files/final_data'
    savetxt('{0}/RMI_XY;{1};{2}.txt'.format(path, size, measurements), out_data)
    return [T_plot, RMIpts]


calcRMI(data, 0.05, graph='yes')
