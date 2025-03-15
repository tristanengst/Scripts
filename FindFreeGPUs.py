"""Pretty prints information on available APEX GPUs. Heuristically, GPUs that aren't
running a process with 'python' in the name are available.
"""
import argparse
import subprocess
import HostInfo

def find_free_gpus(h):
    """Returns a dictionary containing which GPUs on host [h] are free or not.
    Heuristically, a free GPU is one for which nvidia-smi doesn't show any processes
    including 'python' in their name.
    """
    def gpu_line_to_data(l):
        """Returns a Namespace containing the GPU index and process name given by line
        of nvidia-smi output [l].
        """
        l = l.split()
        return argparse.Namespace(gpu=int(l[1]), proc_name=l[6])

    host_info = HostInfo.get_updated_host_to_info(h)

    if host_info.nvidia_smi_ok:
        lines = host_info.nvidia_smi.split("\n")
        eq_line_idxs = [idx for idx,l in enumerate(lines) if l.startswith("|=")]
        idx_of_last_eq_line = eq_line_idxs[-1]
        lines = lines[idx_of_last_eq_line+1:-1]

        gpu_proc_name = [gpu_line_to_data(l) for l in lines]
        gpu_proc_name = [(gpn.gpu, gpn.proc_name) for gpn in gpu_proc_name]
        gpu2proc_names = {idx: [pn for gpu,pn in gpu_proc_name if gpu == idx] for idx in range(host_info.total_gpus)}
        return {idx: not any(["python" in pn for pn in proc_names]) for idx,proc_names in gpu2proc_names.items()} 
    else:
        return {i: False for i in range(host_info.total_gpus)}

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("--hosts", type=str, nargs="*", default=HostInfo.host2info.keys(),
        help="hosts to check for free GPUs.")
    args = P.parse_args()

    args.hosts = HostInfo.host2info.keys() if len(args.hosts) == 0 else args.hosts

    host2gpu2free = {h: find_free_gpus(h) for h in args.hosts}
    host2num_free = {h: sum(gpu2free.values()) for h,gpu2free in host2gpu2free.items()}
    host2total = {h: len(gpu2free) for h,gpu2free in host2gpu2free.items()}

    for h in sorted(host2gpu2free, key=lambda h: host2num_free[h], reverse=True):
        h_pretty_name = HostInfo.host_to_ssh_name(h) if h in HostInfo.host2info else h
        print(f"{h_pretty_name}: free={host2num_free[h]}/{host2total[h]} IDs={[gpu_id for gpu_id,free in host2gpu2free[h].items() if free]}")
    
    print(f"Total free GPUs: {sum(host2num_free.values())}/{sum(host2total.values())}")