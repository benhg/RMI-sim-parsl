# Master code to make everything run

import os, io

# Begin parameter collection

print("Enter the following parameters:")

# Determine desired model

models = {'Ising': 'Ising_model', 'XY': 'XY_model', 'QCD': 'QCD_model', 'beta':'beta_model'}
model = input("Enter model to simulate: ")
while model not in models:
    print("Valid models are:", list(models.keys()))
    model = input("Model entered was invalid. Retry: ")
print(models[model])
# Based on model, determine y_tilde and theta coefficient

if model == 'Ising' or 'XY' or 'beta':
    y_tilde = 0
    theta_coefficient = 0
if model == 'QCD':
    y_tilde = int(input("Enter y_tilde: "))
    theta_coefficient = int(input("Enter the theta coefficient: "))

# Get the replica number

n_valid = [2]
n = int(input("Enter replica number: "))
while n not in n_valid:
    n = int(input("Invalid replica number. Retry: "))

# Get the lattice size

size = int(input("Enter linear lattice size: "))
while size % 8 != 0:
    size = int(input("Please enter a multiple of 8: "))

# Get delta_T

delta_T = float(input("Enter temperature step size: "))

# Get number of independent measurements

measurements = int(input("Enter number of independent measurements: "))

calc_file = "N={0}x{0},{1}M,{2}dT,n={3}".format(size, measurements, delta_T, n)
path = os.path.dirname(os.path.realpath(__file__))
print("Ready to populate calculation file: ", calc_file)

if model == 'beta':
    T_start = float(input("Enter starting beta: "))
    T_end = float(input("Enter final beta: "))
    T_batch = float(input("Enter batch beta step size: "))
else:
    T_start = float(input("Enter starting T: "))
    T_end = float(input("Enter final T: "))
    T_batch = float(input("Enter batch T step size: "))

# RUN BASH SCRIPT GENERATOR
os.system('python3 auto_bash.py {0} {1} {2} {3} "{4}" "{5}" "{6}" {7} {8} {9} {10} {11} '.format(model, y_tilde,
        theta_coefficient, n, size, delta_T, measurements, models[model], path, T_start, T_end, T_batch))

print("\nCalculation file populated.")
while input("\nIs the Monte Carlo script up to date? ") != 'yes':
    print("Update the script then enter 'yes' to continue.")

switch = input("Would you like to run the simulation now? ")

while switch != 'yes':
    if switch == 'no':
        break
    else:
        print("Enter 'yes' to run.")

if switch == 'yes':
    os.system('sh /home/users/briansmith/files/{0}/{1}dT/{2}/run_it_all.sh'.format(models[model], delta_T, calc_file))
