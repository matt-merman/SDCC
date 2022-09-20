from src.main import Register
import argparse
import os
import pyfiglet


def run():

    parser = argparse.ArgumentParser(
        description='desc ...'
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args = parser.parse_args()

    os.system("clear")
    intro = pyfiglet.figlet_format("REGISTER", font="slant")
    print(intro)
    print("(Info: https://github.com/matt-merman/sdcc)\n")

    verbose = False
    if args.verbose:
        verbose = True

    register = Register(verbose, "../config.json")
    register.receive()
    register.send()


if __name__ == '__main__':
    run()
