import argparse
import os
import os.path as osp
import time

def is_newer_than(f, days):
    """Returns if file [f] is newer than [days] days."""
    return osp.getmtime(f) > time.time() + days * 86400

P = argparse.ArgumentParser()
P.add_argument("--dir",
    help="Folder to tar files in")
P.add_argument("--last_k_days",
    help="Only tar files after this date", default=-60)
P.add_argument("--out", required=True,
    help="Name of tar file to create")
P.add_argument("--ignore_hidden", default=1, type=int, choices=[0, 1],
    help="Ignore hidden files")
P.add_argument("--ignore_errors", default=0, type=int, choices=[0, 1],
    help="Ignore errors in osp.getmtime(). I think ComputeCanada breaks things?")
args = P.parse_args()

files_in_folder = os.listdir(args.dir)
files_to_tar = [f for f in files_in_folder if is_newer_than(f, args.last_k_days)]
files_to_tar = [f for f in files_to_tar if not (f.startswith(".") and args.ignore_hidden)]

print(f"Found {len(files_in_folder)} in {args.dir} and {len(files_to_tar)} files to tar")

os.system(f"tar -cvf {args.out} {' '.join(files_to_tar)}")