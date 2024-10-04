"""Extracts line numbers from an `squeue`-derived input."""
import argparse

if __name__ == "__main__":
    P = argparse.ArgumentParser()
    P.add_argument("sq", type=str, help="squeue output")
    P.add_argument("--require_substring", type=str, default=None,
        help="Only include lines with this substring")
    args = P.parse_args()

    lines = args.sq.split("\n")
    lines = [l for l in lines if args.require_substring is None or args.require_substring in l]
    job_ids = [l.split()[0].strip() for l in lines]
    print(" ".join(job_ids))