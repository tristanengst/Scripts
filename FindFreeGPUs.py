import argparse
import subprocess

servers = ["S1", "S2", "S3", "A3", "A4", "A8", "A9"]
server2num_gpus = dict(S1=10, S2=10, S3=10, A3=2, A4=2, A8=2, A9=2)

def find_free_gpus(s):
    """Uses an SSH connection to server [s] and the nvidia-smi command to find free
    GPUs. A free GPU is one for which nvidia-smi doesn't show any processes including
    'python' in their name.
    """
    def gpu_line_to_data(l):
        l = l.split()
        return argparse.Namespace(
            gpu=int(l[1]),
            proc_name=l[6]
        )

    lines = subprocess.getoutput(f"ssh {s} nvidia-smi")
    lines = lines.split("\n")

    eq_line_idxs = [idx for idx,l in enumerate(lines) if l.startswith("|=")]
    if not len(eq_line_idxs) == 2:
        print(f"Error: {s} doesn't have the expected number of equal lines. Probably nvidia-smi isn't working.\n\n{lines}")
        return {i: False for i in range(server2num_gpus[s])}

    idx_of_last_eq_line = eq_line_idxs[-1]
    lines = lines[idx_of_last_eq_line+1:-1]

    gpu2free = dict()
    for l in lines:
        gpu_data = gpu_line_to_data(l)
        gpu2free[gpu_data.gpu] = not "python" in gpu_data.proc_name

    for gpu_idx in range(server2num_gpus[s]):
        if gpu_idx not in gpu2free:
            gpu2free[gpu_idx] = True

    return gpu2free

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("--servers", type=str, choices=servers, nargs="+", default=servers,
        help="Servers to check for free GPUs.")
    args = P.parse_args()


    server2gpu2free = {s: find_free_gpus(s) for s in args.servers}
    server2num_free = {s: sum(gpu2free.values()) for s,gpu2free in server2gpu2free.items()}

    for s in sorted(server2gpu2free, key=lambda s: server2num_free[s], reverse=True):
        print(f"{s}: free={server2num_free[s]}/{server2num_gpus[s]} IDs={[gpu_id for gpu_id,free in server2gpu2free[s].items() if free]}")
    print(f"Total free GPUs: {sum(server2num_free.values())}/{sum(server2num_gpus.values())}")