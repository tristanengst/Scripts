import argparse
import os

P = argparse.ArgumentParser()
P.add_argument("--glob")
args = P.parse_args()

print(args)

os.system(f"cat `ls -tr {args.glob}`")
