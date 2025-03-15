"""Contains dictionaries of host information and methods for accessing them, all in one place.

Feel free to submit a pull request to add additional SSH names for hosts if you don't
use what's here. The only requirement is that no two hosts can share an SSH name.
"""
import argparse
import os.path as osp
import subprocess

# Updated March 15, 2025.
# Commented out hosts are not currently online. The hardware information isn't
# necessarily accurate. Use get_updated_host_to_info for up-to-date information.
host2info = {
    "cs-apex-srv01s.cmpt.sfu.ca": dict(num_cpus=128, num_gpus=10, ssh_names=["S1"]),
    "cs-apex-srv02s.cmpt.sfu.ca": dict(num_cpus=128, num_gpus=10, ssh_names=["S2"]),
    "cs-apex-srv03s.cmpt.sfu.ca": dict(num_cpus=128, num_gpus=10, ssh_names=["S3"]),
    # "cs-apex-01.cmpt.sfu.cas": dict(num_cpus=16, num_gpus=2, ssh_names=["A1"]),
    "cs-apex-02s.cmpt.sfu.ca": dict(num_cpus=16, num_gpus=2, ssh_names=["A2"]),
    "cs-apex-03s.cmpt.sfu.ca": dict(num_cpus=16, num_gpus=2, ssh_names=["A3"]),
    "cs-apex-04s.cmpt.sfu.ca": dict(num_cpus=16, num_gpus=2, ssh_names=["A4"]),
    # "cs-apex-05s.cmpt.sfu.ca": dict(num_cpus=12, num_gpus=2, ssh_names=["A5"]),
    # "cs-apex-06s.cmpt.sfu.ca": dict(num_cpus=12, num_gpus=2, ssh_names=["A6"]),
    # "cs-apex-07s.cmpt.sfu.ca": dict(num_cpus=12, num_gpus=2, ssh_names=["A7"]),
    "cs-apex-08s.cmpt.sfu.ca": dict(num_cpus=12, num_gpus=2, ssh_names=["A8"]),
    "cs-apex-09s.cmpt.sfu.ca": dict(num_cpus=12, num_gpus=2, ssh_names=["A9"]),
    "cs-apex-99s.cmpt.sfu.ca": dict(num_cpus=8, num_gpus=1, ssh_names=["A99", "emily"]),
}

def host_to_ssh_name(h):
    """Returns the name of host [h] that can be logged into with SSH without manual
    authentication. See Alireza's pinned post in Slack. By assumption, the SSH names
    SSHable names of different hosts don't intersect.

    If no SSHable name is found in the hosts file, the first SSHable recorded for the
    host is returned.
    """
    if osp.exists("/private/etc/hosts"):
        ip2name_map = "/private/etc/hosts"
    elif osp.exists("/etc/hosts"):
        ip2name_map = "/etc/hosts"
    else:
        raise ValueError("No known hosts file found.")
    
    with open(ip2name_map, "r") as f:
        lines = f.readlines()
        lines_str = "".join(lines)
    lines = [l.split() for l in lines if not l.startswith("#")]

    for ssh_name in host2info[h]["ssh_names"]:
        for l in lines:
            for ll in l:
                if ll == ssh_name:
                    return ll
    
    return host2info[h]["ssh_names"][0]

def get_updated_host_to_info(h):
    """Returns a Namespace giving the nvidia-smi output, number of GPUs, and number
    CPU cores on host [h].
    """
    ssh_name = host_to_ssh_name(h) if h in host2info else h

    result = subprocess.getoutput(f"ssh {ssh_name} 'nvidia-smi ; nvidia-smi --query-gpu=name --format=csv,noheader | wc -l ; nproc'")

    result = result.split("\n")
    nvidia_smi_lines = result[:-2]
    nvidia_smi_output = "\n".join(nvidia_smi_lines)
    
    # Find the total number of GPUs and if nvidia-smi is working
    if not len([idx for idx,l in enumerate(nvidia_smi_lines) if l.startswith("|=")]) == 2:
        print(f"Error: {h} doesn't have any output. Probably nvidia-smi isn't working.\n\n{nvidia_smi_output}")
        nvidia_smi_ok = False
        total_gpus = host2info[h]["num_gpus"]
        total_cpus = host2info[h]["num_cpus"]
    else:
        nvidia_smi_ok = True
        total_gpus = int(result[-2])
        total_cpus = int(result[-1]) // 2
    return argparse.Namespace(nvidia_smi=nvidia_smi_output,
        nvidia_smi_ok=nvidia_smi_ok,
        total_gpus=total_gpus,
        total_cpus=total_cpus)
    