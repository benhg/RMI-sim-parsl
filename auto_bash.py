# Auto generates bash scripts of desired size

import sys, os, shutil, io
from numpy import *

# Important variables for naming directories

size = int(sys.argv[5])
measurements = int(sys.argv[7])
delta_T = float(sys.argv[6])
n = int(sys.argv[4])
path = sys.argv[9]
model = sys.argv[1]
model_folder = sys.argv[8]
y_tilde = float(sys.argv[2])
theta_coefficient = int(sys.argv[3])

# Script name format

scripts = {'XY':'RMI_{0}.py'.format(model), 'QCD':'RMI_{0}.py'.format(model), 'beta':'RMI_{0}.py'.format(model)}

# Folder paths

packed_folder = 'N={0}x{0},{1}M,{2}dT,n={3}'.format(size, measurements,
                                                               delta_T, n)
whole_path = '{0}/{1}/{2}dT/{3}'.format(path, model_folder, delta_T, packed_folder)
folder_path = '{0}/{1}/{2}dT/{3}'.format(path, model_folder, delta_T, packed_folder)

# Create directories based on paths

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
else:
    shutil.rmtree(folder_path)    # Remove extraneous subdirectories
    os.makedirs(folder_path)


def temp_spread(t_min, t_max, T_ba, dT):
    # Stores each temp pair as a tuple
    t_s = arange(t_min, t_max, T_ba)
    count = len(t_s)
    range_list = []
    for i in range(count):
        range_list.append((t_s[i] + dT, t_s[i] + T_ba))
    return range_list


# Temperature parameters

T_start = float(sys.argv[10])
T_end = float(sys.argv[11])
T_batch = float(sys.argv[12])

# Populate list of temp pairs to run in parallel

temp_list = array(temp_spread(T_start, T_end, T_batch, delta_T))

# WRITE ALL BATCH SCRIPTS

script_num = 1
for temp_pair in temp_list:
    with io.open('{0}/{3}dT/{1}/{2}_submit.sh'.format(model_folder,
                packed_folder, script_num, delta_T), 'w', newline='\n') as batchscript:
        write_T_min = round(temp_pair[0], 3)
        write_T_max = round(temp_pair[1], 3)
        # Now generate:
        batchscript.write(
            """#!/bin/bash
qsub -pe smp 20 -terse  << EOF 
            /local/cluster/bin/python3 {11}/{5}/Master_Codes/{12} {0} {6} {7} {2} {3} {8} {10} {11}
EOF            """.format(size, n, write_T_min, write_T_max, model, model_folder,
            delta_T, measurements, y_tilde, whole_path, theta_coefficient, path, scripts[model])
        )
        script_num += 1

# Create a script that runs all other scripts

with io.open('{0}/{1}dT/{2}/run_it_all.sh'.format(model_folder, delta_T,
            packed_folder), 'w', newline='\n') as run_file:
    run_file.write('#!/bin/bash\n')
    for script_number in range(1, len(temp_list) + 1):
        # Run ALL batch scripts
        run_file.write('bash {}_submit.sh\n'.format(script_number))