#!/bin/bash
qsub -pe smp 4 -terse  << EOF 
            /local/cluster/bin/python3 /home/users/briansmith/files/XY_model/Master_Codes/RMI_XY.py 16 0.05 20000 99.05 100.0 0.0 0 /home/users/briansmith/files
EOF            