import os
import sys
import json

def ask_user_for_info():
    # Begin parameter collection

    print("Enter the following parameters:")

    # Determine desired model

    models = {
        'Ising': 'Ising_model',
        'XY': 'XY_model',
        'QCD': 'QCD_model',
        'beta': 'beta_model'}
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

    calc_file = "N={0}x{0},{1}M,{2}dT,n={3}".format(
        size, measurements, delta_T, n)
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

    model_folder = path
    # Script name format

    scripts = {
        'XY': 'RMI_{0}.py'.format(model),
        'QCD': 'RMI_{0}.py'.format(model),
        'beta': 'RMI_{0}.py'.format(model)}

    # Folder paths

    packed_folder = 'N={0}x{0},{1}M,{2}dT,n={3}'.format(size, measurements,
                                                        delta_T, n)
    whole_path = '{1}/{2}dT/{3}'.format(path,
                                            model_folder,
                                            delta_T,
                                            packed_folder)
    folder_path = '{1}/{2}dT/{3}'.format(path,
                                             model_folder,
                                             delta_T,
                                             packed_folder)

    return {
          "folder_path": folder_path,
          "packed_folder": packed_folder,
          "whole_path": whole_path,
          "scripts": scripts,
          "model_folder": model_folder,
          "T_start": T_start,
          "T_end": T_end,
          "T_batch": T_batch,
          "path": path,
          "calc_file": calc_file,
          "measurements": measurements,
          "delta_T": delta_T,
          "size": size,
          "n": n,
          "theta_coefficient": theta_coefficient,
          "y_tilde": y_tilde,
          "model": model,
          "models": models
            }


if __name__ == '__main__':
    try:
        with open(sys.argv[1]) as fh:
            json.dump(ask_user_for_info(), fh)
    except Exception as e:
        print(json.dumps(ask_user_for_info(), indent=2))
