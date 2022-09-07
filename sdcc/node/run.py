from src.main import *
import argparse


def run():

    parser = argparse.ArgumentParser(
        description='desc ...'
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True

    Node(verbose)


if __name__ == '__main__':
    run()
