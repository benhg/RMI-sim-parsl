#!/bin/bash
qsub -pe smp 20 -terse  << EOF 
            /local/cluster/bin/python3 /home/users/briansmith/files/QCD_model/Master_Codes/RMI_QCD.py 32 0.05 40000 1.05 1.5 1.0 4 /home/users/briansmith/files
EOF            