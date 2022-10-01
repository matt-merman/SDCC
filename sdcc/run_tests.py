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


def run():

    os.system("clear")
    intro = pyfiglet.figlet_format("TEST", font="slant")
    print(intro)
    print("(Info: https://github.com/matt-merman/sdcc)\n")

    # Bully alg. by default
    algorithm = True
    nodes = 4

    while True:
        try:
            op = int(input(
                "1. Node Failure\n2. Coordinator Failure\n3. Two nodes fail (include the Coordinator)\n4. Change Algorithm (Bully by default)\n5. Exit\n(NOTICE: 4 nodes except the register is spawning)\n"))
        except ValueError:
            print(INVALID_OUT)
            continue
        except KeyboardInterrupt:
            return

        if op not in [1, 2, 3, 4, 5]:
            print(INVALID_OUT)
            continue

        if op == 4:
            algorithm = not(algorithm)
            if algorithm:
                print("\nChang and Roberts Algorithm -> Bully Algorithm\n")
            else:
                print("\nBully Algorithm -> Chang and Roberts Algorithm\n")
            continue

        if op == 5:
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
