from src.main import *
import argparse


def run():

    parser = argparse.ArgumentParser(
        description='desc ...'
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-a", "--algorithm", help="ring or bully")

    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True

    algorithm = False
    if args.algorithm == "bully":
        algorithm = True

    Node(verbose, algorithm)


if __name__ == '__main__':
    run()
