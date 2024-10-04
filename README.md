# Scripts
Useful scripts, primarily for manipulating SLURM jobs via Python code aliased to bash commands. Clone the repo into your home folder, and put the following in your `~/.bashrc`. Or clone it wherever and modify the aliases accordingly.

```
alias makedef="python ~/Scripts/SwitchAccounts.py --account def --job"
alias makerrg="python ~/Scripts/SwitchAccounts.py --account rrg --job"
alias scb="python ~/Scripts/Scb.py --job "
alias jcat="python ~/Scripts/JobCat.py --job "
```
Both `makedef` and `makerrg` accept one or more job IDs.
