# Scripts
Useful scripts, primarily for manipulating SLURM jobs via Python code aliased to bash commands. Clone the repo into your home folder, and put the following in your `~/.bashrc`. Or clone it wherever and modify the aliases accordingly.

For SLURM clusters:
```
alias makedef="python ~/Scripts/SwitchAccounts.py --account def --job"
alias makerrg="python ~/Scripts/SwitchAccounts.py --account rrg --job"
alias scb="python ~/Scripts/Scb.py --job "
alias jcat="python ~/Scripts/JobCat.py --job "
```
Both `makedef` and `makerrg` accept one or more job IDs.

A bunch of other functionality is useful on APEX lab workstations. Quick install:
```
cd ; git clone https://github.com/tristanengst/Scripts
cd Scripts
cat WorkstationAliases.txt >> ~/.zshrc
cat WorkstationAliases.txt >> ~/.bash
```
giving the following aliases, and more!
```
alias find_free_gpus="python ~/Scripts/FindFreeGPUs.py"
alias tpython_ddp1="python ~/Scripts/TaskSet.py torchrun --standalone --nnodes=1 --nproc-per-node 1"
alias tpython_ddp2="python ~/Scripts/TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 2"
alias tpython_ddp4="python ~/Scripts/TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 4"
alias tpython_ddp8="python ~/Scripts/TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 8"
```
