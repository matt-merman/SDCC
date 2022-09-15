from src.main import Node
import argparse
import pyfiglet
import os


def run():

    parser = argparse.ArgumentParser(
        description='desc ...'
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-a", "--algorithm", help="ring or bully")

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("NODE", font="slant")
    print(intro)
    print("(Info: https://github.com/matt-merman/sdcc)\n")

    verbose = False
    if args.verbose:
        verbose = True

    algorithm = False
    if args.algorithm == "bully":
        algorithm = True

    node = Node(verbose, algorithm, "./config.json")
    node.start()


if __name__ == '__main__':
    run()
