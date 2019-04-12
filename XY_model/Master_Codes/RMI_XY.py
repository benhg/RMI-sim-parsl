# Imports

from numpy import zeros, sqrt, arange, array, savetxt, vstack
from math import exp, pi, cos, sin
from random import random, randint, uniform
from multiprocessing import Pool
from pylab import plot, title, xlabel, ylabel, \
    legend, show, savefig, xlim
import sys
import time
import datetime

from parsl.configs.local_threads import config
from parsl.app.app import bash_app, python_app

# basic parsl config
parsl.load(config)

# Parameters

todate = datetime.date.today()

size_global = int(sys.argv[1])    # Linear lattice size
output_path = 'output_data.txt'     # Directory path

if size_global == 16:   # Equilibration times
    tau_global = 10240
    tau_after = 1000
elif size_global == 24:
    tau_global = 14000
    tau_after = 1200
elif size_global == 32:
    tau_global = 21000
    tau_after = 4000
elif size_global == 40:
    tau_global = 35000
    tau_after = 6500
elif size_global == 64:
    tau_global = 55000
    tau_after = 10000

E_measurements = int(sys.argv[3])

# Function block


def calcdE(J, lattice, spin, newspin, i, j):
    # Change in energy function
    global size_global
    size = size_global
    dE = 0.0
    neighbor = i - 1
    # Note periodic boundary conditions
    if neighbor > -1:
        dE += cos(newspin - lattice[neighbor, j]) - \
            cos(spin - lattice[neighbor, j])
    else:
        dE += cos(newspin - lattice[size - 1, j]) - \
            cos(spin - lattice[size - 1, j])
    neighbor = i + 1
    if neighbor < size:
        dE += cos(newspin - lattice[neighbor, j]) -\
            cos(spin - lattice[neighbor, j])
    else:
        dE += cos(newspin - lattice[0, j]) - \
            cos(spin - lattice[0, j])
    neighbor = j - 1
    if neighbor > -1:
        dE += cos(newspin - lattice[i, neighbor]) - \
            cos(spin - lattice[i, neighbor])
    else:
        dE += cos(newspin - lattice[i, size - 1]) - \
            cos(spin - lattice[i, size - 1])
    neighbor = j + 1
    if neighbor < size:
        dE += cos(newspin - lattice[i, neighbor]) - \
            cos(spin - lattice[i, neighbor])
    else:
        dE += cos(newspin - lattice[i, 0]) - \
            cos(spin - lattice[i, 0])
    dE *= -J

    return dE


def calcsigma(c, cpts):
    # Bootstrap error analysis
    resample = len(cpts)
    bootc = []
    for x in range(resample):
        bootci = 0.0
        for y in range(resample):
            z = randint(0, resample - 1)
            bootci += cpts[z]
        bootci /= resample
        bootc.append(bootci)
    sigma1 = 0.0
    for w in range(resample):
        sigma1 += (bootc[w] - c) ** 2
    sigma1 /= resample
    error = sqrt(sigma1)

    return error

@python_app
def XYmcsim(T):
    # XY Monte Carlo Simulation
    equilibrium_test = 'no'    # For equilibrium
    global size_global, E_measurements, tau_global, tau_after
    J = 1
    kB = 1  # Boltzmann's constant
    beta = 1 / (kB * T)
    tau = tau_global
    if T > 20:
        tau = tau_after
    BM = E_measurements    # Number of independent measurements
    size = size_global
    N = size ** 2
    corr = 2 * tau
    steps = corr + BM * N
    L = zeros([size, size], float)    # Initial lattice all spin 0
    E = -2 * J * N  # Initially all set at 0

    print("N =", size, "x", size, "; XY model at T =", T)
    E_plot = []
    expectE = 0.0  # Expectation value for E
    E_raw = []

    # Main cycle

    for k in range(steps):
        # Choose random spin
        i = randint(0, size - 1)
        j = randint(0, size - 1)
        s = L[i, j]
        # Generate random configuration
        config = uniform(0, 2 * pi)
        # Calculate change in energy:
        dE = calcdE(J, L, s, config, i, j)
        # Calculate Boltzmann probability
        P = exp(-beta * dE)
        # Accept or reject the spin
        if P > 1 or random() < P:
            L[i, j] = config
            E += dE
        if equilibrium_test == 'yes':
            E_plot.append(E)
        # Record raw data every sweep
        if k >= corr and k % N == 0:
            expectE += E
            E_raw.append(E)

    expectE /= len(E_raw)
    sigma_E = calcsigma(expectE, E_raw)

    if equilibrium_test == 'yes':
        plot(E_plot)
        show()

    return [T, expectE, sigma_E]

@python_app
def XYunionsim(T):
    # XY Monte Carlo Simulation union, for RMI calculation
    global size_global, E_measurements, tau_global, tau_after
    J = 1
    kB = 1  # Boltzmann's constant
    beta = 1 / (kB * T)
    tau = tau_global
    if T > 20:
        tau = tau_after
    size = size_global
    BM = E_measurements
    n = 2
    N = size ** 2
    corr = 2 * tau
    steps = corr + BM * N
    L = zeros([size, size], float)    # Initial lattice all spin 0
    E = -2 * n * J * N     # Initially all set at 0

    print("N =", size, "x", size, "; XY union model at T =", T)
    expectE = 0.0  # Expectation value for E
    Eraw = []

    # Main cycle

    for k in range(steps):
        # Choose random spin
        i = randint(0, size - 1)
        j = randint(0, size - 1)
        s = L[i, j]
        # Generate random configuration
        config = uniform(0, 2 * pi)
        # Calculate change in energy:
        dE = 2 * calcdE(J, L, s, config, i, j)
        # Calculate Boltzmann probability
        P = exp(-beta * dE)
        # Accept or reject the spin
        if P > 1 or random() < P:
            L[i, j] = config
            E += dE
        # Record raw data every sweep
        if k >= corr and k % N == 0:
            expectE += E
            Eraw.append(E)

    expectE /= len(Eraw)
    sigma = calcsigma(expectE, Eraw)

    return [T, expectE, sigma]

@python_app
def XYreplicasim(T):
    # XY replica Monte Carlo simulation
    global size_global, E_measurements, tau_global, tau_after
    J = 1
    kB = 1  # Boltzmann's constant
    beta = 1 / (kB * T)     # Temperature constant
    size = size_global   # Linear dimension of the lattice
    N = size ** 2
    n = 2   # Two replicas
    tau = tau_global
    if T > 20:
        tau = tau_after
    BM = E_measurements
    corr = 2 * tau
    steps = corr + BM * N
    L1 = zeros([size, size], float)    # Initial "left" lattice all spin 0
    L2 = zeros([size, size], float)   # "Right"
    E = -2 * J * n * N

    # Correlation conditions
    bound = size // 2
    A1 = L1[:, 0:bound]
    A2 = L2[:, 0:bound]

    print("N =", size, "x", size, "; Replica XY model at T =", T)
    expectE = 0.0   # Energy expectation value
    Eraw = []

    # Main cycle

    for k in range(steps):

        # Choose random spin
        i = randint(0, size - 1)
        j = randint(0, size - 1)
        s = L1[i, j]
        r = L2[i, j]
        # Generate random configuration
        config = uniform(0, 2 * pi)
        config2 = uniform(0, 2 * pi)
        if j < bound:
            config2 = config
        # Calculate change in energy:
        dE1 = calcdE(J, L1, s, config, i, j)
        dE2 = calcdE(J, L2, r, config2, i, j)
        dE = dE1 + dE2
        # Calculate Boltzmann probability
        P = exp(-beta * dE)
        # Accept or reject the spin
        if P > 1 or random() < P:
            E += dE
            L1[i, j] = config
            L2[i, j] = config2
        # Record raw data every sweep
        if k >= corr and k % N == 0:
            expectE += E
            Eraw.append(E)
        # Ensure A1 = A2
        if k == steps - 1:
            corrtest = 'yes'
            matches = 0
            if corrtest == 'yes':
                for columns in range(bound):
                    for rows in range(size):
                        if A1[rows, columns] == A2[rows, columns]:
                            matches += 1
            if matches == (size * bound):
                print("The replica is working great!")
            else:
                print("Something is wrong with the replica.")

    expectE /= len(Eraw)
    sigma = calcsigma(expectE, Eraw)

    return [T, expectE, sigma]


@python_app
def vary_temps(Tm, TM, dT, savedata=True):
    global size_global, todate
    # Build temperature array, data[0]
    if Tm == 0:
        temps = arange(Tm + dT, TM + dT, dT)
    else:
        temps = arange(Tm, TM + dT, dT)

    normal = [XYmcsim(t) for t in temps]
    AUB = [XYunionsim(t) for t in temps]
    replica = [XYreplicasim(t) for t in temps]


    normal = array([n.result() for n in normal])
    # Normal model
    T_plot = normal[:, 0]
    XY_E = normal[:, 1]
    XY_sigma = normal[:, 2]


    AUB = array([t.result() for t in AUB])
    # AUB model
    AUB_E = AUB[:, 1]
    AUB_sigma = AUB[:, 2]


    replica = array([t.result() for t in replica])
    # Replica model
    replica_E = replica[:, 1]
    replica_sigma = replica[:, 2]

    if savedata:
        data = [
            T_plot,
            XY_E,
            XY_sigma,
            AUB_E,
            AUB_sigma,
            replica_E,
            replica_sigma]
        # Save to finished data
        path = 'XY_model/finished_data'
        savetxt('{0}/RMI_XY;{1};{2};{3};{4}'.format(path,
                                                    E_measurements, Tm, TM, dT), data)

    return [T_plot, replica_E, replica_sigma, AUB_E, AUB_sigma, XY_E, XY_sigma]


if __name__ == "__main__":   # Required for multiprocessing on windows

    tstart = time.time()

    Tmin = float(sys.argv[4])
    Tmax = float(sys.argv[5])
    T_step = float(sys.argv[2])
    vary_temps(Tmin, Tmax, T_step)

    # End of main program

    t_elapse = (time.time() - tstart) / 3600
    print("Full program done in {0: .3f} hours.".format(t_elapse))
