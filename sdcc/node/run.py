from src.main import Node
import argparse
import pyfiglet
import os


def run():

    parser = argparse.ArgumentParser(
        description='Implementation of distributed election algorithms.'
    )

    parser.add_argument("-v", "--verbose", default="False", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-d", "--delay", default="False",
                        help="generate a random delay to forwarding messages", action="store_true")
    parser.add_argument("-a", "--algorithm", action='store',
                        default="ring", choices=["ring", "bully"], help="ring by default")

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("NODE", font="slant")
    print(intro)
    print("(Info: https://github.com/matt-merman/sdcc)\n")

    algorithm = False
    if args.algorithm == "bully":
        algorithm = True

    node = Node(args.verbose, algorithm, "../config.json", args.delay)
    node.start()


if __name__ == '__main__':
    run()
