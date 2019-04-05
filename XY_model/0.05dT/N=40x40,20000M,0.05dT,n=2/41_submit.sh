#!/bin/bash
qsub -pe smp 4 -terse  << EOF 
            /local/cluster/bin/python3 /home/users/briansmith/files/XY_model/Master_Codes/RMI_XY.py 40 0.05 20000 40.05 41.0 0.0 0 /home/users/briansmith/files
EOF            