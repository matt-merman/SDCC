import os
import pyfiglet
import tests as t

INVALID_OUT = "Wrong Input!"


def test_a(test):
    test.test_a()


def test_b(test):
    test.test_b()


def test_c(test):
    test.test_c()


def get_nodes():
    while True:
        try:
            num = int(input("Insert nodes number\n"))
        except ValueError:
            print(INVALID_OUT)
            continue
        except KeyboardInterrupt:
            print()
            return

        if num < 4:
            print("Error (InvalidNumber): number of nodes must be greater then 4\n")
        else:
            return num


def run():

    os.system("clear")
    intro = pyfiglet.figlet_format("TEST", font="slant")
    print(intro)
    print("(Info: https://github.com/matt-merman/sdcc)\n")
    print("(WARNING: Using a UDP connection may cause the packet loss)\n")

    algorithm = True  # i.e., Bully alg.
    nodes = 4

    while True:
        try:
            op = int(input(
                "1. Node Failure\n2. Coordinator Failure\n3. Two nodes fail (include the Coordinator)\n4. Change Algorithm (Bully by default)\n5. Set Nodes (4 by default)\n6. Exit\n"))
        except ValueError:
            print(INVALID_OUT)
            continue
        except KeyboardInterrupt:
            print()
            return

        if op not in [1, 2, 3, 4, 5, 6]:
            print(INVALID_OUT)
            continue

        if op == 4:
            algorithm = not(algorithm)
            if algorithm:
                print("\n(Bully Algorithm configured)")
            else:
                print("\n(Chang and Roberts Algorithm configured)")
            continue

        if op == 5:
            nodes = get_nodes()
            continue

        if op == 6:
            return

        command = {1: test_a,
                   2: test_b,
                   3: test_c
                   }

        test = t.Tests(nodes, algorithm)
        command[op](test)
        return


if __name__ == '__main__':
    run()
