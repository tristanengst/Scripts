import argparse
import os
import os.path as osp
import time

def is_newer_than(f, days, ignore_errors=False):
    """Returns if file [f] is newer than [days] days."""
    return osp.getmtime(f) > time.time() + days * 86400

P = argparse.ArgumentParser()
P.add_argument("--dir",
    help="Folder to tar files in")
P.add_argument("--last_k_days", type=int,
    help="Only tar files after this date", default=-60)
P.add_argument("--out", required=True,
    help="Name of tar file to create")
P.add_argument("--ignore_hidden", default=1, type=int, choices=[0, 1],
    help="Ignore hidden files")
args = P.parse_args()

files_in_folder = [f"{args.dir}/{f}" for f in os.listdir(args.dir)]
files_to_tar = [f for f in files_in_folder if is_newer_than(f, args.last_k_days)]
files_to_tar = [f for f in files_to_tar if not (f.startswith(".") and args.ignore_hidden)]

print(f"Found {len(files_in_folder)} in {args.dir} and {len(files_to_tar)} files to tar")

os.system(f"tar -cvf {args.out} {' '.join(files_to_tar)}")
