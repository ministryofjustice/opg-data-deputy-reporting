#!/bin/python

# As many of the tools are removed from distroless images it can be hard to tell what's going on when building them.
# Use this as a replacement for the usual .py file when debugging and add any other useful output
# that will help you identify what's going on. Simply change the CMD to ["/app/debug.py", "/"]

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("root", type=str, help="The root directory to walk.")


def main(args):
    """Prints the files that are inside the container, rooted at the first argument."""
    print("PRINTING DIRECTORY STRUCTURE")
    for dirpath, _, files in os.walk(args.root):
        for f in files:
            print(os.path.join(dirpath, f))

    print("PRINTING ENVIRONMENT VARIABLES")
    for k, v in sorted(os.environ.items()):
        print(k + ":", v)
    print("\n")

    print("PRINTING PATH ENVIRONMENT VARIABLE")
    for item in os.environ["PATH"].split(";"):
        print(item)


if __name__ == "__main__":
    main(parser.parse_args())
