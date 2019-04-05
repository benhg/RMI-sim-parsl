#!/bin/bash
qsub -pe smp 10 -terse  << EOF 
            /local/cluster/bin/python3 /home/users/briansmith/files/beta_model/Master_Codes/RMI_beta.py 24 0.001 20000 0.201 0.3 0.0 0 /home/users/briansmith/files
EOF            