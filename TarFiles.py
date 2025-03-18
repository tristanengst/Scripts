import argparse
import os
import os.path as osp
import time

# Sometimes this takes a bit, so tqdm is nice. But we can't assume it's installed.
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x): return x

def tar_imle_ssl_dir(args):

    dirs_to_tar = ["models_mae", "models_imle", "models_stop", "models_dino", "probes", "finetunes"]

    if "narval" in os.uname().nodename:
        cluster = "narval"
    elif "cedar" in os.uname().nodename:
        cluster = "cedar"
    elif "beluga" in os.uname().nodename:
        cluster = "beluga"
    elif "apex" in os.uname().nodename:
        cluster = "apex"
    else:
        raise NotImplementedError(f"Unknown cluster for {os.uname().nodename}")

    # Format the date as YYYY_MM_DD
    date = time.strftime("%Y_%m_%d")
    os.chdir(osp.expanduser("~/scratch/IMLE-SSL"))
    for d in tqdm(dirs_to_tar):
        out = f"{d}_{cluster}_{date}.tar"
        print(f"Tar: {d} -> {out}")
        _ = tar_folder(argparse.Namespace(**vars(args) | dict(dir=d, out=out)))

def is_newer_than(f, days, ignore_errors=False):
    """Returns if file [f] is newer than [days] days."""
    return osp.getmtime(f) > time.time() + days * 86400

def tar_folder(args):
    files_in_folder = [f"{args.dir}/{f}" for f in os.listdir(args.dir)]
    files_to_tar = [f for f in files_in_folder if is_newer_than(f, args.last_k_days)]
    files_to_tar = [f for f in files_to_tar if not (f.startswith(".") and args.ignore_hidden)]

    print(f"Found {len(files_in_folder)} in {args.dir} and {len(files_to_tar)} files to tar")

    if len(files_to_tar) > 0:
        os.system(f"tar -cvf {args.out} {' '.join(files_to_tar)}")
    else:
        print(f"No files to tar in {args.dir}. Ending.")

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("--dir", default=None,
        help="Folder to tar files in")
    P.add_argument("--last_k_days", type=int,
        help="Only tar files after this date", default=-60)
    P.add_argument("--out", default=None,
        help="Name of tar file to create")
    P.add_argument("--ignore_hidden", default=1, type=int, choices=[0, 1],
        help="Ignore hidden files")
    P.add_argument("--imle_ssl_scratch_tar", choices=[0, 1], type=int, default=0,
        help="Generate tarfiles for IMLE-SSL")
    args = P.parse_args()

    if args.last_k_days > 0:
        print(f"Got last_k_days={args.last_k_days}, will interpret as negative")
        args.last_k_days = -1 * args.last_k_days

    if args.imle_ssl_scratch_tar:
        _ = tar_imle_ssl_dir(args)
    else:
        _ = tar_folder(args)
