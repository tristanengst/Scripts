import argparse
import os

P = argparse.ArgumentParser()
P.add_argument("--job")
args = P.parse_args()
os.system(f"scontrol show job {args.job}")