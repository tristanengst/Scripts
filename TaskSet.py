"""Hacky wrapper for using APEX servers until we can put SLURM on them. The basic
idea is to specify specific GPU indices with --gpus like normal, figure out which CPUs
these should use, and then set only the specified GPUs to be visible and replace them
with --gpus starting at zero, using the specified ones.

Should be more portable, but a hacky, horrible thing to undo once possibe.

I recommend aliasing this:
alias tasksetpy="python ~/Scripts/TaskSet.py"

You can even combine it with the torchrun aliases:

alias tpython_ddp1="python TaskSet.py torchrun --standalone --nnodes=1 --nproc-per-node 1"
alias tpython_ddp="python TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 2"
alias tpython_ddp2="python TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 2"
alias tpython_ddp4="python TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 4"
alias tpython_ddp8="python TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 8"
alias tpython_ddp10="python TaskSet.py  torchrun --standalone --nnodes=1 --nproc-per-node 10"

"""
import argparse
from collections import defaultdict
import os
import os.path as osp
import sys
import uuid

shell2rc = dict(zsh="~/.zshrc", bash="~/.bashrc")

cs_apex_servers = ["cs-apex-srv01s.cmpt.sfu.ca", "cs-apex-srv02s.cmpt.sfu.ca", "cs-apex-srv03s.cmpt.sfu.ca"]

cs_apex_workstation_16cpu = ["cs-apex-01s", "cs-apex-02s", "cs-apex-03s", "cs-apex-04s.cmpt.sfu.ca"]

cs_apex_workstation_12cpu = ["cs-apex-05s", "cs-apex-06s", "cs-apex-07s", "cs-apex-08s", "cs-apex-09s"]

cs_apex_workstation_8cpu = ["cs-apex-99s.cmpt.sfu.ca"]


def get_hyperthread_by_host(default=0):
    """Returns if hyperthreading is enabled on the current host."""
    hyperthread_enabled_hosts = ["cs-apex-srv01s.cmpt.sfu.ca", "cs-apex-srv02s.cmpt.sfu.ca", "cs-apex-srv03s.cmpt.sfu.ca"]
    return 1 if os.uname().nodename in hyperthread_enabled_hosts else default

def inset_arg_into_arg_list(*, arg_list, k, v):
    """Returns [arg_list] with argument --k inserted with values [v] before the first
    keyword argument that is alphabetically after [k].

    Args:
    arg_list    -- list of arguments
    k           -- key to insert (does not start with '--')
    v           -- value to insert (as a list)
    """
    new_arg_list = []
    already_inserted = False
    for a in arg_list:
        if a.startswith(f"--") and a.lstrip("--") > k and not already_inserted:
            new_arg_list.append(f"--{k}")
            new_arg_list += v
            new_arg_list.append(a)
            already_inserted = True
        else:
            new_arg_list.append(a)
    return new_arg_list

def get_script_from_alias(alias):
    if alias == "python":
        return "python"
    elif alias == "python_ddp1":
        return "torchrun --standalone --nnodes=1 --nproc-per-node 1"
    elif alias == "python_ddp2":
        return "torchrun --standalone --nnodes=1 --nproc-per-node 2"
    elif alias == "python_ddp4":
        return "torchrun --standalone --nnodes=1 --nproc-per-node 4"
    elif alias == "python_ddp8":
        return "torchrun --standalone --nnodes=1 --nproc-per-node 8"
    else:
        print(f"Unknown alias {alias}, returning alias={alias}")
        return alias


def get_cpus_from_gpus(*, gpus, hyperthread=0):
    """Returns the CPU range that should be used for the specified GPUs.
    """
    if os.uname().nodename in cs_apex_servers:
        gpu2min = {0: 0, 1: 6, 2: 12, 3: 18, 4: 24, 5: 32, 6: 38, 7: 44, 8: 50, 9: 56}
        gpu2max = {0: 5, 1: 11, 2: 17, 3: 23, 4: 29, 5: 37, 6: 43, 7: 49, 8: 55, 9: 61}
    elif os.uname().nodename in cs_apex_workstation_16cpu:
        gpu2min, gpu2max = {0: 0, 1: 8}, {0: 7, 1: 15}
    elif os.uname().nodename in cs_apex_workstation_12cpu:
        gpu2min, gpu2max = {0: 0, 1: 6}, {0: 5, 1: 11}
    elif os.uname().nodename in cs_apex_workstation_8cpu:
        gpu2min, gpu2max = {0: 0, 1: 4}, {0: 3, 1: 7}
    else:
        raise Exception(f"Unknown hostname {os.uname().nodename}")

    gpu_min = min([gpu2min[gpu] for gpu in gpus])
    gpu_max = max([gpu2max[gpu] for gpu in gpus])

    if hyperthread == 1:
        gpu_min *= 2
        gpu_max = gpu_max * 2 + 1

    return f"{gpu_min}-{gpu_max}"

P = argparse.ArgumentParser()
P.add_argument("-c", default="parse_gpus",
    help="CPU specification")
P.add_argument("--gpus", nargs="+", type=int, required=True,
    help="GPU specification")
P.add_argument("--shell", default="bash", choices=["bash", "zsh"],
    help="Shell type")
P.add_argument("--taskset_scripts_dir", default=osp.expanduser("~/.taskset_scripts"),
    help="Directory to store taskset scripts")
P.add_argument("--taskset_debug", action="store_true",
    help="Print the taskset script instead of running it")
P.add_argument("--hyperthread", choices=[-1, 0, 1], type=int, default=-1,
    help="Whether to assume hyperthreading is enabled or not. -1 checkes the hostname and sets automatically.")
args, unparsed_args = P.parse_known_args()
args.hyperthread = get_hyperthread_by_host() if args.hyperthread == -1 else args.hyperthread

args.c = get_cpus_from_gpus(gpus=args.gpus, hyperthread=args.hyperthread) if args.c == "parse_gpus" else args.c
unparsed_args = inset_arg_into_arg_list(arg_list=unparsed_args,
    k="gpus",
    v=[str(gpu) for gpu in range(len(args.gpus))])

unparsed_args[0] = get_script_from_alias(unparsed_args[0])

script_file = osp.join(args.taskset_scripts_dir, f"{uuid.uuid4()}.sh")
script = f"source {shell2rc[args.shell]}\nCUDA_VISIBLE_DEVICES={','.join([str(g) for g in args.gpus])} taskset -c {args.c} {' '.join(unparsed_args)}"

if args.taskset_debug:
    print(script)
else:
    os.makedirs(osp.dirname(script_file), exist_ok=True)
    with open(script_file, "w+") as f:
        f.write(script)
    os.system(f"taskset -c {args.c} {args.shell} {script_file}")
