#!/bin/bash
qsub -pe smp 10 -terse  << EOF 
            /local/cluster/bin/python3 /home/users/briansmith/files/beta_model/Master_Codes/RMI_beta.py 16 0.001 20000 0.701 0.8 0.0 0 /home/users/briansmith/files
EOF            