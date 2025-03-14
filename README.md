# Scripts
Useful scripts and their aliases, and more aliases useful for manipulating SLURM and other ML jobs.

### Installation
```
git clone https://github.com/tristanengst/Scripts ~/Scripts # It does actually expect to be in your home directory
python ~/Scripts/WriteAliases.py
```

### Useful on SLURM clusters
**makedef [list of SLURM job IDs]** moves each job in the input list to the def-keli account

**makerrg [list of SLURM job IDs]** moves each job in the input list to the rrg-keli account

**scb [JOB ID]** is a nicer version of `scontrol JOB ID`

**sqb** is a nicer version of `squeue` for rrg-keli and def-keli accounts, and shows jobs of the current user

**sqbau** is a nicer version of `squeue` for rrg-keli and def-keli accounts, and shows jobs of all users

**sshareb** is a nicer version of `sshare` for rrg-keli and def-keli accounts

**extract_job_ids [s]** accepts copied output `[s]` of `sqb` or `sqbau` in quotes and returns all the job IDs

**historyb** nicely displays the command history

**find_free_gpus** displays information about free APEX workstation and server GPUs

### Useful on APEX workstations and servers
**python_ddpX** is an alias for single-node `torchrun` with power-of-two `X` GPUs

**tpython_ddpX** is an alias for single-node `torchrun` with power-of-two `X` GPUs, but also uses `TaskSet.py` to ensure only specific CPU cores are used

### Miscellaneous
**killwandb** pkills WandB when it's being slow and annoying

**get_wandb_id** prints a new WandB UID to the terminal
