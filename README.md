## RMI Simulation

This set of modules is a Parsl-based version of a Renyi-Mutual-Information particle simulation. It uses information theory principles to solve physical problems related to quantum field theory and quark confinement.

### Physics at Play

Ask brian for some physics help.

### Simulation Concepts

We are running this simulation using Parsl, a workflow management system designed and implemented at Argonne National Lab. We will use Parsl to orchestrate the simulations and after that works, we plan to offload some of the number-crunching to GPUs.

### File Structure

This section is mostly for me, to help me understand how it works.

```
/ aggregate*.py (for output handling)             
  auto_bash.py (handling input and execution) - /<MODEL NAME>_model/ - NUMBERdT/* (intermediate output data)
                                                                     - finished_data/ (final output data)
                                                                     - master_codes/ - RMI_<MODEL NAME>.py (Domain code, run as bash app)
                                                /finished_data (final output data for all things in the package)
  sim_runner.py (handling input)
```

This is the current file structure. We will attempt to merge all of `aggregate`, `auto_bash`, and `sim_runner` into one parsl-based script, to start with.

### Authors

The primary developer is [Ben Glick](https://glick.cloud). All of the physics at play comes from Mohamed Anber and Brian Smith, who also wrote the initial code. Ben's faculty advisor, Jens Mache is also involved with the project. 

If you have any questions, feel free to reach out to Ben at (mailto:glick@lclark.edu).