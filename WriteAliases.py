"""Writes useful ML aliases to .zshrc and .bashrc files."""

import argparse
import os.path as osp
import re

aliases = [
    "# START USEFUL ML ALIASES",

    # Useful on SLUR, doesn't require a Python script
    "alias sqb=\"squeue -u $USER -O 'JobArrayID:.10,Name:.175,State:.8,TimeLeft:.10'\"",
    "alias historyb=\"history | cut -c 8-\"",
    "alias sshareb=\"sshare -l -A rrg-keli_gpu; sshare -l -A def-keli_gpu\"",
    "alias sqbau=\"squeue -A rrg-keli_gpu -O 'JobArrayID:11,UserName:6,State:9,tres-per-node:17,TimeLeft:12,Reason:20,Name:.160'; squeue -A def-keli_gpu  -O 'JobArrayID:11,UserName:6,State:9,tres-per-node:17,TimeLeft:12,Reason:20,Name:.160'\"",

    # Useful on SLURM
    "alias makedef=\"python ~/Scripts/SwitchAccounts.py --account def --job\"",
    "alias makerrg=\"python ~/Scripts/SwitchAccounts.py --account rrg --job\"",
    "alias scb=\"python ~/Scripts/Scb.py --job \"",
    "alias scu=\"python ~/Scripts/Scu.py \"",
    "alias extract_job_ids=\"python ~/Scripts/ExtractJobIds.py \"",
    
    # Useful APEX workstations and servers
    "alias python_ddp1=\"torchrun --standalone --nnodes=1 --nproc-per-node 1\"",
    "alias python_ddp2=\"torchrun --standalone --nnodes=1 --nproc-per-node 2\"",
    "alias python_ddp4=\"torchrun --standalone --nnodes=1 --nproc-per-node 4\"",
    "alias python_ddp8=\"torchrun --standalone --nnodes=1 --nproc-per-node 8\"",
    "alias tpython_ddp1=\"python ~/Scripts/TaskSet.py python_ddp1\"",
    "alias tpython_ddp2=\"python ~/Scripts/TaskSet.py python_ddp2\"",
    "alias tpython_ddp4=\"python ~/Scripts/TaskSet.py python_ddp4\"",
    "alias tpython_ddp8=\"python ~/Scripts/TaskSet.py python_ddp8\"",
    "alias get_wandb_id=\"python -c 'import wandb ; print(wandb.util.generate_id())'\"",
    "alias find_free_gpus=\"python ~/Scripts/FindFreeGPUs.py\"",
    "alias killwandb=\"pkill -9 wandb\"",
    
    "# END USEFUL ML ALIASES"]


def alias_to_name(alias): return alias.split("=")[0].strip()

def write_aliases_to_file(fname):
    """Writes the aliases to file [fname], removing any that are already there."""
    aliases_names = set([alias_to_name(a) for a in aliases])
    with open(fname, "r") as f:
        existing_lines = f.readlines()
    
    lines = [e for e in existing_lines if not alias_to_name(e) in aliases_names]
    lines = lines + aliases
    lines = [l.strip() for l in lines]
    lines_str = "\n".join(lines)
    
    all_multi_empty_lines = re.findall(r'\n{3,}', lines_str)
    for multi_empty_line in all_multi_empty_lines:
        lines_str = lines_str.replace(multi_empty_line, "\n")
    lines = lines_str.split("\n")

    with open(fname, "w") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("--files", nargs="+", default=["~/.bashrc", "~/.zshrc"],
        help="Files to write aliases to")
    args = P.parse_args()

    args.files = [osp.expanduser(f) for f in args.files]
    for fname in args.files:
        _ = write_aliases_to_file(fname)
        print(f"Aliases written to {fname}")